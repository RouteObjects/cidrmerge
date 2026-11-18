#!/usr/bin/env python3
"""Synthetic macOS binding-gate controls; no real release or product claims."""
from pathlib import Path
import argparse,json,os,platform,subprocess,sys
p=argparse.ArgumentParser();p.add_argument('--shared',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=False);assert platform.system()=='Darwin','These synthetic executable controls exercise the macOS binding branch';checks=[]
def save(p,j):p.write_text(json.dumps(j,indent=2)+'\n')
for mode in ['valid','wrong-candidate-version','wrong-candidate-revision','unpublished-receipt','wrong-publication-revision','other-pin-drift','local-manifest','local-workspace']:
 root=a.output/mode;root.mkdir();baseline_revision='5e4b3d2f881340a6ced05742429f1bd680dfd1e0';candidate_revision='a'*40
 for v in ['B','C']:
  source=root/('source-'+v);source.mkdir();pinmap=[{'identity':'swift-cidr','kind':'remoteSourceControl','location':'https://github.com/RouteObjects/swift-cidr.git','state':{'revision':baseline_revision if v=='B' else candidate_revision,'version':'0.10.1' if v=='B' else '0.11.0'}}]+[{'identity':'dependency-'+str(i),'kind':'remoteSourceControl','location':'https://example.invalid/dependency-'+str(i)+'.git','state':{'revision':str(i)*40,'version':'1.0.0'}} for i in range(1,8)]
  if v=='C':
   if mode=='wrong-candidate-version':pinmap[0]['state']['version']='0.10.2'
   if mode=='wrong-candidate-revision':pinmap[0]['state']['revision']='b'*40
   if mode=='other-pin-drift':pinmap[1]['state']['version']='2.0.0'
  save(source/'Package.resolved',{'pins':pinmap,'version':3});(source/'Package.swift').write_text('.package(\n path: "../local")\n' if v=='C' and mode=='local-manifest' else '// synthetic source control\n');binary=root/v;binary.write_text('#!'+sys.executable+'\nprint("0.4.2")\n');binary.chmod(0o755)
 swift=root/'swift';swift.write_text('#!'+sys.executable+'\nprint("Swift version 6.4.2 (synthetic control)")\n');swift.chmod(0o755);save(root/'gate.json',{'passed':True,'synthetic_control':True});publication={'passed':True,'published':mode!='unpublished-receipt','version':'0.11.0','revision':'b'*40 if mode=='wrong-publication-revision' else candidate_revision,'release_url':'https://github.com/RouteObjects/swift-cidr/releases/tag/0.11.0','synthetic_control':True};save(root/'publication.json',publication)
 command=[sys.executable,str(a.shared/'control/freeze_bindings.py'),'--shared',str(a.shared),'--baseline-source',str(root/'source-B'),'--candidate-source',str(root/'source-C'),'--baseline',str(root/'B'),'--candidate',str(root/'C'),'--output',str(root/'bindings.json'),'--evidence',str(root/'gate.json'),'--swift',str(swift),'--candidate-version','0.11.0','--candidate-revision',candidate_revision,'--publication-receipt',str(root/'publication.json')]
 if mode=='local-workspace':
  save(root/'workspace-state.json',{'object':{'dependencies':[{'packageRef':{'identity':'swift-cidr','kind':'fileSystem'},'state':{'name':'fileSystem'}}]}});command+=['--candidate-workspace',str(root/'workspace-state.json')]
 with (root/'check.log').open('x') as f:proc=subprocess.run(command,stdout=f,stderr=subprocess.STDOUT)
 assert (proc.returncode==0)==(mode=='valid'),mode;receipt=json.loads((root/'bindings.json').read_text());assert receipt['passed']==(mode=='valid');checks.append({'name':mode,'passed':True,'exit_code':proc.returncode})
save(a.output/'summary.json',{'passed':True,'checks':checks,'count':len(checks),'synthetic_control':True,'real_product_binaries_executed':False});print(json.dumps({'passed':True,'checks':len(checks)}))
