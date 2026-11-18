#!/usr/bin/env python3
"""Small positive and adversarial runner/auditor checks; no product benchmark claims."""
from pathlib import Path
import argparse,hashlib,json,os,platform,shutil,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--shared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=False);checks=[]
def sha(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def save(p,v):p.write_text(json.dumps(v,indent=2)+'\n')
def command(args,log):
 with log.open('x') as f:proc=subprocess.run(args,stdout=f,stderr=subprocess.STDOUT)
 return proc.returncode
for mode in ['valid','wrong-output','wrong-stderr','nonzero','bad-input-hash']:
 root=a.output/mode;root.mkdir();shared=root/'shared';(shared/'control').mkdir(parents=True);(shared/'input.txt').write_bytes(b'hello\n');(shared/'reference.txt').write_bytes(b'hello\n')
 body='import pathlib,sys\nb=pathlib.Path(sys.argv[-1]).read_bytes()\n'
 if mode=='wrong-output':body+="sys.stdout.buffer.write(b'wrong\\n')\n"
 else:body+='sys.stdout.buffer.write(b)\n'
 if mode=='wrong-stderr':body+="sys.stderr.write('unexpected\\n')\n"
 if mode=='nonzero':body+='sys.exit(7)\n'
 for v in ['B','C']:
  file=root/v;file.write_text('#!'+sys.executable+'\n'+body);file.chmod(0o755)
 part={'label':'mixed','family':None,'input':'input.txt','input_sha256':('0'*64 if mode=='bad-input-hash' else sha(shared/'input.txt')),'input_bytes':6,'input_entries':1,'reference':'reference.txt','output_sha256':sha(shared/'reference.txt'),'output_bytes':6};case={'id':'control','group':'original','suite':'native','case':'control','entries':1,'flags':[],'parts':[part]};save(shared/'control/cases.json',{'configs':[case]});save(shared/'control/protocol.json',{'test_control':True});save(root/'bindings.json',{'passed':True,'files':{str(root/v):sha(root/v) for v in ['B','C']},'binaries':{v:{'path':str(root/v),'sha256':sha(root/v)} for v in ['B','C']}})
 cmd=[sys.executable,str(a.shared/'control/run_matched.py'),'--platform','macos' if platform.system()=='Darwin' else 'linux','--shared',str(shared),'--baseline',str(root/'B'),'--candidate',str(root/'C'),'--bindings',str(root/'bindings.json'),'--group','original','--output',str(root/'measurements'),'--content-store',str(root/'content')];code=command(cmd,root/'runner.log');assert (code==0)==(mode=='valid'),mode;checks.append({'name':'runner-'+mode,'passed':True,'exit_code':code})
 if mode=='valid':
  code=command([sys.executable,str(a.shared/'control/audit_measurements.py'),'--run',str(root/'measurements'),'--output',str(root/'audit.json')],root/'audit.log');assert code==0;(root/'audit.json').read_text();checks.append({'name':'audit-valid','passed':True,'exit_code':code})
base=a.output/'valid/measurements'
for mutation in ['bad-summary','bad-resource','missing-warmup','wrong-order','extra-sample','wrong-output','wrong-followup']:
 target=a.output/('audit-'+mutation);shutil.copytree(base,target)
 if mutation=='bad-summary':
  path=target/'summary.json';j=json.loads(path.read_text());j['pairs']['control']['paired_change_medians']['elapsed']+=2;save(path,j)
 elif mutation=='missing-warmup':(target/'warmup/control/B/sample.json').unlink()
 elif mutation=='extra-sample':
  d=target/'round-07/control/B';d.mkdir(parents=True);shutil.copy2(target/'round-01/control/B/sample.json',d/'sample.json')
 elif mutation=='wrong-followup':
  path=target/'summary.json';j=json.loads(path.read_text());j['followup_required']=[] if j['followup_required'] else ['control'];save(path,j)
 elif mutation=='wrong-output':(target/'round-01/control/B/mixed/stdout').write_bytes(b'wrong\n')
 elif mutation=='wrong-order':
  path=target/'round-01/control/B/sample.json';j=json.loads(path.read_text());j['sequence']+=1;save(path,j)
 else:
  path=target/'round-01/control/B/mixed/process.json';j=json.loads(path.read_text());j['peak_rss_bytes']+=4096;save(path,j)
 output=a.output/(mutation+'-audit.json');code=command([sys.executable,str(a.shared/'control/audit_measurements.py'),'--run',str(target),'--output',str(output),'--map',str(base)+'='+str(target)],a.output/(mutation+'-audit.log'));assert code!=0,mutation;checks.append({'name':'audit-reject-'+mutation,'passed':True,'exit_code':code})
save(a.output/'summary.json',{'passed':True,'checks':checks,'count':len(checks),'product_binaries_executed':False});print(json.dumps({'passed':True,'checks':len(checks)}))
