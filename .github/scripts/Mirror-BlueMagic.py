"""Mirror confirmed public facts from Shergaze's service; never accept identity fields."""
import json,urllib.request
from pathlib import Path
URL='https://shergaze-license.prggdw867p.workers.dev/v1/blue-magic'
def validate(data):
    if set(data)!={'schema','observations'} or data['schema']!=1 or not isinstance(data['observations'],list) or len(data['observations'])>10000: raise ValueError('Invalid list')
    for r in data['observations']:
        if set(r)!={'monster','zone','spell','confirmed'} or r['confirmed'] is not True or not isinstance(r['monster'],str) or not 0<len(r['monster'])<=64 or any(ord(c)<32 or ord(c)==127 for c in r['monster']) or type(r['zone'])!=int or not 0<=r['zone']<=4095 or type(r['spell'])!=int or not 512<=r['spell']<=767: raise ValueError('Invalid public observation')
    return data
if __name__=='__main__':
    with urllib.request.urlopen(URL,timeout=30) as response: raw=response.read(2097153)
    if len(raw)>2097152: raise ValueError('Oversized list')
    data=validate(json.loads(raw));path=Path('blue-magic.json')
    # Preserve existing observations and confirmed flags even if a service snapshot is incomplete.
    rows={}
    if path.exists():
        old=json.loads(path.read_text(encoding='utf-8'))
        if old.get('schema')!=1 or not isinstance(old.get('observations'),list): raise ValueError('Invalid existing list')
        for row in old['observations']:
            if set(row)-{'monster','zone','spell','confirmed'}: raise ValueError('Private fields in existing list')
            rows[(row['zone'],row['monster'].lower(),row['spell'])]=row
    for row in data['observations']: rows[(row['zone'],row['monster'].lower(),row['spell'])]=row
    if len(rows)>10000: raise ValueError('Too many observations')
    result=json.dumps({'schema':1,'observations':[rows[k] for k in sorted(rows)]},indent=2,ensure_ascii=True)+'\n'
    path.write_text(result,encoding='utf-8')
