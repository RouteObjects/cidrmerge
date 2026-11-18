from pathlib import Path
import ipaddress,json,hashlib
ROOT=Path(__file__).resolve().parents[1];old=Path('$PRIOR_EXPERIMENT/fixtures');dest=ROOT/'scale';dest.mkdir(exist_ok=False)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
cases=[]
for pattern in ['mixed-disjoint','mixed-permuted','mixed-overlap','mixed-adjacent']:
 with (old/pattern/'input.txt').open() as f:lines=[next(f) for _ in range(100000)]
 for n in [1000,10000,100000]:
  name=f'{pattern}-{n}';d=dest/name;d.mkdir();p=d/'input.txt';p.write_text(''.join(lines[:n]));by={4:[],6:[]}
  for s in lines[:n]:
   net=ipaddress.ip_network(s.strip(),strict=False);by[net.version].append(net)
  result=[str(net) for family in [4,6] for net in ipaddress.collapse_addresses(by[family])]
  ref=d/'reference.txt';ref.write_text('\n'.join(result)+'\n')
  cases.append({'case':name,'entries':n,'pattern':pattern,'input':str(p.relative_to(dest)),'input_bytes':p.stat().st_size,'input_sha256':sha(p),'output':str(ref.relative_to(dest)),'output_bytes':ref.stat().st_size,'output_sha256':sha(ref),'output_count':len(result)})
(dest/'reference.json').write_text(json.dumps({'cases':cases,'method':'Python ipaddress.collapse_addresses, independent of Swift parser/coalescer','parent_fixture_root':str(old)},indent=2)+'\n');print(json.dumps({'cases':len(cases),'path':str(dest)},indent=2))
