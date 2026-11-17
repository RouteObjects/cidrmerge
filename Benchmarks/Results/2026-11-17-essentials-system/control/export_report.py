#!/usr/bin/env python3
"""Export only selected report evidence, without modifying original observations."""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--root',type=Path,required=True)
    parser.add_argument('--output',type=Path,required=True)
    parser.add_argument('--data',default='analysis/report-data-final-01')
    parser.add_argument('--rendered',default='analysis/report-ready-final-01')
    parser.add_argument('--redact',action='append',default=[],help='literal prefix=public placeholder')
    args=parser.parse_args()
    root=args.root.resolve()
    replacements=[(str(root),'$EXPERIMENT')]
    replacements += [tuple(value.split('=',1)) for value in args.redact]
    replacements.sort(key=lambda item:len(item[0]),reverse=True)
    dataset=json.loads((root/args.data/'dataset.json').read_text())
    assert dataset['passed'] and dataset['complete_platform_set']
    assert set(dataset['platforms'])=={'macos','arm64','x86_64'}
    selections={
        'analysis/RESULTS-final.md':'RESULTS.md',
        'analysis/report-drafts/REPRODUCING.md':'REPRODUCING.md',
        'analysis/report-drafts/COMPATIBILITY.md':'COMPATIBILITY.md',
        'analysis/report-drafts/ARTIFACTS.md':'ARTIFACTS.md',
        'analysis/report-drafts/ARTIFACTS.json':'evidence/ARTIFACTS.json',
        'control/baseline-freeze.json':'evidence/baseline-freeze.json',
        'control/dependency-freeze.json':'evidence/dependency-freeze.json',
        'control/final-variant-isolation.json':'evidence/final-variant-isolation.json',
        'control/R3-freeze.json':'evidence/R3-freeze.json',
        'control/E4-freeze.json':'evidence/E4-freeze.json',
        'control/S2-freeze.json':'evidence/S2-freeze.json',
        'control/retained-candidate.json':'evidence/retained-candidate.json',
        'control/report-export-recovery.json':'evidence/report-export-recovery.json',
        'control/aggregate_report.py':'control/aggregate_report.py',
        'control/render_report.py':'control/render_report.py',
        'control/export_report.py':'control/export_report.py',
        'control/finalize_report.py':'control/finalize_report.py',
        'control/validate_deliverables.py':'control/validate_deliverables.py',
        'control/review_report_independent.py':'control/review_report_independent.py',
        'control/plot-environment-requirements.txt':'control/plot-environment-requirements.txt',
        'analysis/review-final-independent.json':'evidence/review-final-independent.json',
        'analysis/REVIEW-final.md':'REVIEW.md',
        'analysis/review-final-conclusions.json':'evidence/review-final-conclusions.json',
        'analysis/borrowed-line-source-analysis.md':'BORROWED-LINE-ANALYSIS.md',
    }
    for platform in dataset['platforms']:
        selections[f'analysis/{platform}-report-index.json']=f'evidence/{platform}-report-index.json'
    for name in ['summaries.csv','pairs.csv','dataset.json','aggregation.json']:
        selections[str(Path(args.data)/name)]=name if name.endswith('.csv') else f'evidence/{name}'
    for name in ['RETAINED.md','REGRESSIONS.md','retained.csv','retained-elapsed.png','retained-rss.png','regression-observations.json','render.json']:
        selections[str(Path(args.rendered)/name)]=name if not name.endswith('.json') else f'evidence/{name}'
    for name in ['comparison-protocol-final.json','retained-R3-protocol-addendum.json','release-style-protocol-addendum.json','stdin-protocol-addendum.json']:
        selections[f'control/{name}']=f'evidence/{name}'
    # The platform indices map original paths; preserve receipts under that same layout
    # beneath evidence/original/ so each paired result is independently reviewable.
    for platform in dataset['platforms']:
        index=json.loads((root/f'analysis/{platform}-report-index.json').read_text())
        for row in index['audit_rows']:
            receipt=row['receipt']
            assert not Path(receipt).is_absolute() and '..' not in Path(receipt).parts
            selections[receipt]=str(Path('evidence/original')/receipt)
        def referenced_metadata(value):
            if isinstance(value,dict):
                for child in value.values():
                    yield from referenced_metadata(child)
            elif isinstance(value,list):
                for child in value:
                    yield from referenced_metadata(child)
            elif isinstance(value,str) and value.endswith('.json'):
                candidate=Path(value)
                if not candidate.is_absolute() and '..' not in candidate.parts and (root/candidate).is_file():
                    yield value
        for receipt in referenced_metadata(index):
            selections[receipt]=str(Path('evidence/original')/receipt)
    sources=[]
    for source,destination in selections.items():
        path=root/source
        assert path.is_file(),path
        original=path.read_bytes()
        payload=original
        changes={'path_redaction_applied':False,'csv_line_endings_normalized':False}
        if path.suffix not in ['.png']:
            value=original.decode('utf-8')
            for old,new in replacements:
                value=value.replace(old,new)
            changes['path_redaction_applied']=value!=original.decode('utf-8')
            if path.suffix=='.csv':
                normalized=value.replace('\r\n','\n')
                assert list(csv.reader(io.StringIO(value)))==list(csv.reader(io.StringIO(normalized)))
                changes['csv_line_endings_normalized']=normalized!=value
                value=normalized
            payload=value.encode('utf-8')
        sources.append((source,destination,original,payload,changes))
    args.output.mkdir(parents=True,exist_ok=False)
    manifest=[]
    for source,destination,original,payload,changes in sources:
        target=args.output/destination
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_bytes(payload)
        manifest.append({'source':source,'destination':destination,
                         'source_sha256':hashlib.sha256(original).hexdigest(),
                         'export_sha256':hashlib.sha256(payload).hexdigest(),
                         'export_bytes':len(payload),'presentation_transformed':original!=payload,**changes})
    (args.output/'evidence-export.json').write_text(json.dumps({
        'scope':'Selected evidence; original raw outputs, SVG figures, binaries, fixtures and runtime remain under the Downloads experiment root. Repository figures use the identical preserved PNG exports.',
        'original_path_base':'$EXPERIMENT',
        'audit_receipt_export_base':'evidence/original/',
        'redaction':'Known local path prefixes are replaced with public placeholders. Exported CSV line endings use LF with parsed records verified unchanged. Measurement values and original-content hashes are unchanged.',
        'files':manifest},indent=2)+'\n')
    print(json.dumps({'files':len(manifest),'bytes':sum(f['export_bytes'] for f in manifest),'output':str(args.output)}))


if __name__=='__main__':
    main()
