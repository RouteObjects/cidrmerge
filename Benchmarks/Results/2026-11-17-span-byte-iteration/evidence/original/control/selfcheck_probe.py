from pathlib import Path
from types import SimpleNamespace
import ast,datetime,hashlib,importlib.util,io,json,sys
sys.dont_write_bytecode=True
root=Path('$EXPERIMENT');control=root/'control'
output=control/'selfcheck-01';output.mkdir(exist_ok=False)
results=[]
for name in ['audit_comparison.py','audit_stdin_comparison.py']:
    spec=importlib.util.spec_from_file_location(name,control/name);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    class FakePath:
        def __init__(self,change=None):self.calls=0;self.change=change
        def stat(self):
            self.calls+=1
            fields=dict(st_dev=1,st_ino=2,st_size=3,st_mtime_ns=4,st_ctime_ns=5,st_atime_ns=6)
            if self.calls>1 and self.change:fields[self.change]+=1
            return SimpleNamespace(**fields)
        def open(self,mode):assert mode=='rb';return io.BytesIO(b'abc')
        def __str__(self):return '<controlled-file>'
    args=SimpleNamespace(root=root,platform_root=root,directory=root)
    for change in [None,'st_atime_ns','st_dev','st_ino','st_size','st_mtime_ns','st_ctime_ns']:
        auditor=module.Auditor(args);fake=FakePath(change);original=module.Path;module.Path=lambda value:value
        try:
            try:value=auditor.digest(fake)
            except ValueError as error:
                assert change not in [None,'st_atime_ns'];assert 'Content identity changed' in str(error)
                results.append({'auditor':name,'change':change,'expected':'reject','passed':True})
            else:
                assert change in [None,'st_atime_ns'];assert value==hashlib.sha256(b'abc').hexdigest()
                results.append({'auditor':name,'change':change,'expected':'accept','passed':True})
        finally:module.Path=original
    auditor=module.Auditor(args);fake=FakePath();original=module.Path;module.Path=lambda value:value
    try:
        try:auditor.check_hash(fake,hashlib.sha256(b'wrong').hexdigest())
        except ValueError as error:assert 'Hash mismatch' in str(error);results.append({'auditor':name,'change':'wrong reference content hash','expected':'reject','passed':True})
        else:raise AssertionError('Wrong reference hash accepted')
    finally:module.Path=original
freeze=json.loads((control/'common-harness-freeze.json').read_text())
for rel,digest in freeze['control_sha256'].items():
    assert hashlib.sha256((root/rel).read_bytes()).hexdigest()==digest,rel
protocol=json.loads((control/'measurement-protocol.json').read_text())
assert [len(protocol['matrices'][k]['config_ids']) for k in ['throughput','stdin']]==[8,2]
assert sum(x['measured_samples'] for x in protocol['matrices'].values())==120
assert sum(x['warmups'] for x in protocol['matrices'].values())==20
for name in freeze['syntax_parsed_scripts']:ast.parse((control/name).read_text())
summary={'passed':True,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'Deterministic in-memory auditor identity/reference controls and frozen syntax/protocol checks; no product execution or measurement.','observations':results,'frozen_control_files_verified':len(freeze['control_sha256']),'protocol_measured':120,'protocol_warmups':20,'script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
(output/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps({'passed':True,'auditor_controls':len(results),'frozen_control_files_verified':len(freeze['control_sha256'])}))
