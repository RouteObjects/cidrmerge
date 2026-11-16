from pathlib import Path
import datetime,hashlib,ipaddress,json,shutil
R=Path(__file__).resolve().parents[1];old=Path('$HOME/Downloads/cidrmerge-competitors-20261114T210745Z/fixtures');cases=['ipv4-disjoint','ipv6-disjoint','mixed-disjoint','mixed-permuted','mixed-overlap','range-derived-mixed'];out=R/'fixtures';out.mkdir(exist_ok=False);configs=[]
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
for name in cases:
 src=old/name;dest=out/name;dest.mkdir();expected=json.loads((src/'expected.json').read_text());assert sha(src/'input.txt')==expected['input_file_sha256'];shutil.copy2(src/'input.txt',dest/'input.txt');shutil.copy2(src/'expected.json',dest/'prior-expected.json');family={4:[],6:[]}
 with (dest/'input.txt').open() as f:
  for line in f:
   line=line.strip()
   if not line:continue
   if '...' in line:
    a,b=map(ipaddress.ip_address,line.split('...'));assert a.version==b.version and int(a)<=int(b);family[a.version].append((int(a),int(b)))
   else:
    n=ipaddress.ip_network(line,strict=False);family[n.version].append((int(n.network_address),int(n.broadcast_address)))
 coverage=hashlib.sha256();counts={'ranges':0,'cidr':0};addresses={};refs={}
 with (dest/'ranges.expected').open('wb') as ranges,(dest/'cidr.expected').open('wb') as cidrs:
  for version in (4,6):
   entries=family[version];entries.sort();merged=[]
   for a,b in entries:
    if merged and a<=merged[-1][1]+1:merged[-1]=(merged[-1][0],max(merged[-1][1],b))
    else:merged.append((a,b))
   covered=0;address=ipaddress.IPv4Address if version==4 else ipaddress.IPv6Address
   for a,b in merged:
    coverage.update(bytes([version])+a.to_bytes(16,'big')+b.to_bytes(16,'big'));covered+=b-a+1;ranges.write(f'{address(a)}...{address(b)}\n'.encode());counts['ranges']+=1
    for network in ipaddress.summarize_address_range(address(a),address(b)):
     cidrs.write((str(network)+'\n').encode());counts['cidr']+=1
   addresses['ipv'+str(version)]=str(covered)
 assert coverage.hexdigest()==expected['coverage_sha256'] and counts['ranges']==expected['range_count'] and counts['cidr']==expected['minimal_cidr_count'] and addresses==expected['addresses_covered']
 for representation in ['ranges','cidr']:
  p=dest/(representation+'.expected');configs.append({'id':name+'-'+representation,'fixture':name,'representation':representation,'input':'fixtures/'+name+'/input.txt','input_sha256':sha(dest/'input.txt'),'reference':'fixtures/'+name+'/'+representation+'.expected','output_sha256':sha(p),'output_bytes':p.stat().st_size,'output_count':counts[representation]})
 rec={'passed':True,'input_sha256':expected['input_file_sha256'],'prior_expected_sha256':sha(src/'expected.json'),'coverage_sha256':coverage.hexdigest(),'output_counts':counts,'oracle':'Python ipaddress input parsing and summarize_address_range, independent numeric interval union; full coverage/cardinality/address counts match preserved original oracle.'};(dest/'reference-receipt.json').write_text(json.dumps(rec,indent=2)+'\n');print(name,counts,flush=True)
(R/'control/cases.json').write_text(json.dumps({'schema':1,'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'configs':configs,'warmups_per_variant':1,'measured_pairs':6,'pair_order':'alternating B/C then C/B with rotating case order','followup_policy':'one separate fixed six-pair follow-up for any case with an individual elapsed/RSS regression >5%; preserve all observations'},indent=2)+'\n')
