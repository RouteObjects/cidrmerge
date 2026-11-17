#!/usr/bin/env python3
"""Read-only audit of report arithmetic/inventory and displayed benchmark tables."""
import argparse,pathlib,json,csv,statistics,math,datetime,hashlib,collections,sys
parser=argparse.ArgumentParser(description='Independently review existing benchmark audit metadata, CSVs, and rendered tables. Never runs product binaries or measurements.')
parser.add_argument('--root',type=pathlib.Path,required=True)
parser.add_argument('--dataset',type=pathlib.Path,required=True,help='Dataset directory, relative to root or absolute.')
parser.add_argument('--rendered',type=pathlib.Path,required=True,help='Rendered report directory, relative to root or absolute.')
parser.add_argument('--output',type=pathlib.Path,required=True,help='New JSON receipt; must not already exist. Relative to root or absolute.')
args=parser.parse_args()
ROOT=args.root.resolve()
def rooted(path):return path if path.is_absolute() else ROOT/path
DATA=rooted(args.dataset); READY=rooted(args.rendered); OUTPUT=rooted(args.output)
if OUTPUT.exists():raise SystemExit(f'Refusing to overwrite existing receipt: {OUTPUT}')
D=json.loads((DATA/'dataset.json').read_text()); errors=[]; checks=collections.Counter(); PLATFORMS=D['platforms']
def check(ok,detail):
 checks['assertions']+=1
 if not ok: errors.append(detail)
def eq(a,b):
 if a is None or b is None:return a is b
 if isinstance(a,(int,float)) and isinstance(b,(int,float)):return math.isclose(a,b,rel_tol=1e-12,abs_tol=1e-10)
 return a==b
def key(row):return tuple(row[k] for k in ['platform','kind','profile','comparison','phase','case'])
def pairkey(row):return key(row)+(row['round'],)
rows={key(s):s for s in D['summaries']}; pairs={pairkey(p):p for p in D['pairs']}
check(len(rows)==len(D['summaries']),'duplicate summary keys');check(len(pairs)==len(D['pairs']),'duplicate pair keys')
seen=set();seen_pairs=set();phase_counts={};source_receipts=[]
for platform in PLATFORMS:
 index=json.loads((ROOT/f'analysis/{platform}-report-index.json').read_text());source_receipts.append(f'analysis/{platform}-report-index.json')
 total_measured=total_warmups=summary_count=pair_count=0
 for phase in index['audit_rows']:
  audit=json.loads((ROOT/phase['receipt']).read_text());source_receipts.append(phase['receipt']); result=audit['result']
  check(audit['passed'] and result['passed'],['audit_failed',phase['receipt']]);check(result['measured_samples']==phase['measured_samples'],['phase_sample_count',phase])
  check(result['warmups']==phase['warmups'],['phase_warmups',phase]);check(set(result['configs'])==set(result['recomputed']),['audit_case_set',phase])
  total_measured+=result['measured_samples'];total_warmups+=result['warmups']
  for case,case_data in result['recomputed'].items():
   k=(platform,phase['kind'],phase['profile'],phase['comparison'],phase['phase'],case);seen.add(k); summary_count+=1
   check(k in rows,['missing_summary',k]); row=rows.get(k,{})
   n=len(case_data['pairs']);pair_count+=n
   check(n==result['rounds'],['round_count',k]);check(row.get('n')==n,['dataset_n',k]);check(row.get('audit_receipt')==phase['receipt'],['receipt',k])
   check(row.get('B_variant')==result['role_mapping']['B'] and row.get('C_variant')==result['role_mapping']['C'],['variant_roles',k])
   values={f'{role}_{metric}':[] for role in ['B','C'] for metric in ['elapsed_seconds','cpu_seconds','rss_bytes']};changes={metric:[] for metric in ['elapsed','cpu','rss']}
   for pair in case_data['pairs']:
    pk=k+(pair['round'],);seen_pairs.add(pk);check(pk in pairs,['missing_pair',pk]);pr=pairs.get(pk,{})
    for role in ['B','C']:
     obs={'elapsed_seconds':pair[role]['elapsed_ns']/1e9,'cpu_seconds':pair[role]['cpu_seconds'],'rss_bytes':pair[role]['peak_rss_bytes']}
     for metric,value in obs.items():
      values[f'{role}_{metric}'].append(value);check(eq(pr.get(f'{role}_{metric}'),value),['pair_value',pk,role,metric])
    for metric,field in [('elapsed','elapsed_ns'),('cpu','cpu_seconds'),('rss','peak_rss_bytes')]:
     change=100*(pair['C'][field]/pair['B'][field]-1) if pair['B'][field] else None
     check(eq(pr.get(f'{metric}_change_pct'),change),['pair_delta',pk,metric]);check(eq(pair.get(f'{metric}_change_pct'),change),['audit_pair_delta',pk,metric])
     if change is not None:changes[metric].append(change)
   for name,vals in values.items():
    for statistic,fn in [('median',statistics.median),('min',min),('max',max)]:check(eq(row.get(name+'_'+statistic),fn(vals)),['absolute_statistic',k,name,statistic])
   for metric,vals in changes.items():
    check(row.get(metric+'_change_n')==len(vals),['nonzero_cpu_n',k,metric])
    for statistic,fn in [('median',statistics.median),('min',min),('max',max)]:check(eq(row.get(metric+'_change_pct_'+statistic),fn(vals) if vals else None),['paired_statistic',k,metric,statistic])
  check(result['measured_samples']==2*sum(len(v['pairs']) for v in result['recomputed'].values()),['result_sample_count',phase])
  check(result['warmups']==2*len(result['configs']),['result_warmup_count',phase])
 phase_counts[platform]={'phases':len(index['audit_rows']),'measured_samples':total_measured,'warmups':total_warmups,'case_summaries':summary_count,'pairs':pair_count}
 check(all(value==D['reconciliation'][platform][field] for field,value in phase_counts[platform].items()),['platform_totals',platform])
check(seen==set(rows),'summary inventory mismatch');check(seen_pairs==set(pairs),'pair inventory mismatch')
# Verify all generated CSV values, not only displayed or rounded values.
for name,expected,keyer in [(DATA/'summaries.csv',rows,key),(DATA/'pairs.csv',pairs,pairkey),(READY/'retained.csv',{k:v for k,v in rows.items() if k[3]=='B-vs-R3'},key)]:
 actual=list(csv.DictReader(name.open()));seen_csv=set()
 for row in actual:
  for intkey in ['round','n','elapsed_change_n','cpu_change_n','rss_change_n']:
   if intkey in row:row[intkey]=int(row[intkey])
  k=keyer(row);seen_csv.add(k);check(k in expected,['csv_extra_row',name.name,k])
  for field,expected_value in expected.get(k,{}).items():
   if isinstance(expected_value,(int,float)):value=float(row[field]) if row[field] != '' else None
   elif expected_value is None:value=None if row[field]=='' else row[field]
   else:value=row[field]
   check(eq(value,expected_value),['csv_value',name.name,k,field])
 check(seen_csv==set(expected),['csv_inventory',name.name]);check(len(seen_csv)==len(actual),['csv_duplicates',name.name])
# Verify the complete displayed rows against audit-derived values, independently formatting them.
md=(READY/'RETAINED.md').read_text();actual_table_rows=[line for line in md.splitlines() if line.startswith('| ') and not line.startswith('| Case')]
expected_table_rows=[]
def pct(s,metric):return f"{s[metric+'_change_pct_median']:+.2f}% [{s[metric+'_change_pct_min']:+.2f}%, {s[metric+'_change_pct_max']:+.2f}%]"
retained=[s for s in D['summaries'] if s['comparison']=='B-vs-R3']
for s in retained:
 if s['kind']=='startup' and s['profile']=='ordinary':continue
 if s['kind']=='throughput':
  case=s['case'].removeprefix('text-'); suffix='no stats' if case.endswith('-no-stats') else 'stats';case=case.removesuffix('-no-stats').removesuffix('-stats')
  line=f"| {case} / {suffix} ({s['phase']}) | {s['B_elapsed_seconds_median']:.4f} | {s['C_elapsed_seconds_median']:.4f} | {pct(s,'elapsed')} | {s['B_rss_bytes_median']/2**20:.2f} | {s['C_rss_bytes_median']/2**20:.2f} | {pct(s,'rss')} |"
 else:
  line=f"| {s['case']} / {s['phase']} | {s['B_elapsed_seconds_median']*1000:.3f} | {s['C_elapsed_seconds_median']*1000:.3f} | {pct(s,'elapsed')} | {s['B_rss_bytes_median']/2**20:.2f} / {s['C_rss_bytes_median']/2**20:.2f} | {pct(s,'rss')} |"
 expected_table_rows.append(line)
check(collections.Counter(actual_table_rows)==collections.Counter(expected_table_rows),{'markdown_table_mismatch':{'missing':list((collections.Counter(expected_table_rows)-collections.Counter(actual_table_rows)).elements()),'extra':list((collections.Counter(actual_table_rows)-collections.Counter(expected_table_rows)).elements())}})
# Check regression registry independently against all primary-triggered case/metric records.
registry=json.loads((READY/'regression-observations.json').read_text()); expected_triggers={}
for s in D['summaries']:
 if not s['phase'].startswith('primary'):continue
 base=tuple(s[k] for k in ['platform','kind','profile','comparison','case'])
 followups=[f for f in D['summaries'] if tuple(f[k] for k in ['platform','kind','profile','comparison','case'])==base and f['phase'].startswith('followup')]
 for metric in ['elapsed','rss']:
  if s[metric+'_change_pct_max']>5:
   expected_triggers[base+(metric,)]=(s,followups)
   check(len(followups)==1,['missing_or_multiple_followup',base,metric])
actual_triggers={tuple(s[k] for k in ['platform','kind','profile','comparison','case','metric']):s for s in registry if s.get('primary_trigger',True)}
check(set(actual_triggers)==set(expected_triggers),'regression registry primary triggers mismatch')
for k,(s,fs) in expected_triggers.items():
 reg=actual_triggers.get(k,{})
 check(eq(reg.get('primary_median_pct'),s[k[-1]+'_change_pct_median']),['registry_primary',k])
 if fs:check(eq(reg.get('followup_median_pct'),fs[0][k[-1]+'_change_pct_median']),['registry_followup',k])
# Validate rendered regression tables and secondary metric observations independently.
regression_rows_checked=0; platform=None
platform_titles={'macOS ARM64':'macos','Linux ARM64':'arm64','Linux x86-64':'x86_64'}
for line in (READY/'REGRESSIONS.md').read_text().splitlines():
 if line.startswith('## ') and line[3:] in platform_titles:platform=platform_titles[line[3:]]
 if not line.startswith(('| startup /','| throughput /','| stdin /')):continue
 cols=[v.strip() for v in line.split('|')[1:-1]]
 kind,comparison,profile=cols[0].split(' / ');case=cols[1];metric=cols[2]
 for value,phase_prefix in [(cols[3],'primary'),(cols[4],'followup')]:
  selected=[r for r in D['summaries'] if (r['platform'],r['kind'],r['profile'],r['comparison'],r['case'])==(platform,kind,profile,comparison,case) and r['phase'].startswith(phase_prefix)]
  check(len(selected)==1,['regression_markdown_phase_count',platform,kind,profile,comparison,case,phase_prefix])
  if len(selected)!=1:continue
  row=selected[0];expected=f"{row[metric+'_change_pct_median']:+.2f}% [{row[metric+'_change_pct_min']:+.2f}%, {row[metric+'_change_pct_max']:+.2f}%] ({row['phase']})"
  check(expected==value,['regression_markdown_value',platform,kind,profile,comparison,case,metric,phase_prefix])
 matches=[r for r in registry if (r['platform'],r['kind'],r['profile'],r['comparison'],r['case'],r['metric'])==(platform,kind,profile,comparison,case,metric)]
 check(len(matches)==1,['regression_markdown_registry_count',platform,kind,profile,comparison,case,metric])
 if len(cols)==6 and len(matches)==1:check(cols[5]==matches[0]['interpretation'],['regression_markdown_interpretation',platform,comparison,case,metric])
 regression_rows_checked+=1
check(regression_rows_checked==len(registry),'regression markdown total count')
# Every required retained primary configuration must exist on each included platform.
expected_direct={
 ('throughput','ordinary'):{f'{case}-{mode}' for case in ['text-ipv4-canonical','text-ipv6-canonical','text-mixed-noncanonical','text-mixed-addresses','text-mixed-ranges','text-mixed-overlap','searchbot-canonical','searchbot-noncanonical'] for mode in ['no-stats','stats']},
 ('stdin','ordinary'):{'searchbot-canonical-no-stats','searchbot-noncanonical-stats'},
 ('startup','ordinary'):{'empty-stdin','mixed-100','mixed-10000','version'},
 ('startup','release-style'):{'empty-stdin','mixed-100','mixed-10000','version'},
}
for platform in PLATFORMS:
 for (kind,profile),expected in expected_direct.items():
  actual={r['case'] for r in D['summaries'] if r['platform']==platform and r['kind']==kind and r['profile']==profile and r['comparison']=='B-vs-R3' and r['phase'].startswith('primary')}
  check(actual==expected,['direct_configuration_inventory',platform,kind,profile])

# Retained direct comparison interpretation, keeping phases separate.
repeated=[];positive=[];cpu_mismatch=[];reports={};absolute_cpu_issues=[]
for s in retained:
 cpu=s['cpu_change_pct_median'];elapsed=s['elapsed_change_pct_median'];
 if cpu is not None and cpu*elapsed<0 and abs(cpu-elapsed)>2:cpu_mismatch.append({k:s[k] for k in ['platform','kind','profile','phase','case','elapsed_change_pct_median','cpu_change_pct_median','B_cpu_seconds_median','C_cpu_seconds_median']})
 if s['phase'].startswith('primary'):
  for metric in ['elapsed','rss','cpu']:
   value=s[metric+'_change_pct_median']
   fs=[f for f in retained if f['platform']==s['platform'] and f['kind']==s['kind'] and f['profile']==s['profile'] and f['case']==s['case'] and f['phase'].startswith('followup')]
   if value is not None and value>0:positive.append({'platform':s['platform'],'kind':s['kind'],'profile':s['profile'],'case':s['case'],'metric':metric,'primary_median_pct':value,'followup_median_pct':fs[0][metric+'_change_pct_median'] if fs else None})
   if value is not None and value>5 and fs and fs[0][metric+'_change_pct_median'] is not None and fs[0][metric+'_change_pct_median']>5:repeated.append(positive[-1])
for p in [x for x in D['pairs'] if x['comparison']=='B-vs-R3']:
 for role in ['B','C']:
  # This command is single-threaded in ordinary operation, but quantized system/user accounting and scheduling may differ.
  if p[role+'_cpu_seconds']>p[role+'_elapsed_seconds']+0.021:absolute_cpu_issues.append({'key':pairkey(p),'role':role,'cpu_seconds':p[role+'_cpu_seconds'],'elapsed_seconds':p[role+'_elapsed_seconds']})
for platform in PLATFORMS:
 rr=[s for s in retained if s['platform']==platform]; text=[s for s in rr if s['kind']=='throughput' and s['case'].startswith('text-') and s['phase'].startswith('primary')];search=[s for s in rr if s['kind']=='throughput' and s['case'].startswith('searchbot-')]
 def ranges(ss):return {metric:[min(s[metric+'_change_pct_median'] for s in ss),max(s[metric+'_change_pct_median'] for s in ss)] for metric in ['elapsed','cpu','rss']}
 reports[platform]={'direct_case_phase_count':len(rr),'text_primary_cases':len(text),'text_primary_paired_median_ranges_pct':ranges(text),'searchbot_file_case_phase_count':len(search),'searchbot_file_rows':[{k:s[k] for k in ['case','phase','n','elapsed_change_pct_median','cpu_change_pct_median','rss_change_pct_median']} for s in search],'stdin_rows':[{k:s[k] for k in ['case','phase','n','elapsed_change_pct_median','cpu_change_pct_median','rss_change_pct_median']} for s in rr if s['kind']=='stdin'],'startup_rows':[{k:s[k] for k in ['profile','case','phase','n','B_elapsed_seconds_median','C_elapsed_seconds_median','elapsed_change_pct_median','elapsed_change_pct_min','elapsed_change_pct_max','cpu_change_pct_median','rss_change_pct_median']} for s in rr if s['kind']=='startup']}
review={'passed':not errors,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'reviewer_previous_attempt':'analysis/review-partial-02-independent.json preserves false-positive reviewer checks: passed metadata was compared with pure counts, and CSV zero counts were incorrectly treated as missing. No report discrepancy was involved.','scope':'Independent arithmetic and inventory recomputation from existing passed platform audits; no product, source, harness, measurement or existing report mutation.','platforms':PLATFORMS,'complete_platform_set':D['complete_platform_set'],'source_dataset_directory':str(DATA.relative_to(ROOT)),'source_rendered_directory':str(READY.relative_to(ROOT)),'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [DATA/'dataset.json',DATA/'summaries.csv',DATA/'pairs.csv',READY/'retained.csv',READY/'RETAINED.md',READY/'regression-observations.json']},'checks':dict(checks),'reviewer_script_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'source_audit_count':len(source_receipts)-len(PLATFORMS),'case_summaries':len(rows),'pairs':len(pairs),'rendered_markdown_rows_checked':len(expected_table_rows),'regression_markdown_rows_checked':regression_rows_checked,'primary_regression_metric_triggers_checked':len(expected_triggers),'counts':phase_counts,'errors':errors,'retained_repeated_over_5_percent_median_regressions':repeated,'retained_elapsed_cpu_sign_mismatches_over_2_points':cpu_mismatch,'retained_cpu_above_elapsed_by_over_21ms':absolute_cpu_issues,'retained':reports,'limitations':['No new measurements or artifact/output hashing; source evidence is already-passed independent audits.','Mac CPU is quantized to0.01 seconds; startup zero baselines yield null percent changes and cannot substantiate CPU conclusions.','ARM tiny startup peak RSS is contaminated by the launcher fork/exec floor, independently demonstrated by preserved /bin/true control.','Primary and follow-up phases remain separate; >5% repetition is descriptive, not a significance test.']}
OUTPUT.parent.mkdir(parents=True,exist_ok=True)
OUTPUT.open('x').write(json.dumps(review,indent=2)+'\n')
print(json.dumps({'passed':review['passed'],'checks':checks,'errors':errors,'rows':len(rows),'pairs':len(pairs),'markdown_rows':len(expected_table_rows),'repeated_regressions':repeated,'cpu_sign_mismatches':cpu_mismatch,'cpu_elapsed_issues':absolute_cpu_issues},indent=2))

if errors:sys.exit(1)
