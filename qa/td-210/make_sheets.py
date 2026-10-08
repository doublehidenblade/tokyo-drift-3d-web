from pathlib import Path
from PIL import Image,ImageDraw
import json,hashlib
qa=Path(__file__).resolve().parent;out=qa/'review-sheets';out.mkdir(exist_ok=True);manifest=[]

def sheets(pairs,label,per_sheet,thumb):
 for offset in range(0,len(pairs),per_sheet):
  subset=pairs[offset:offset+per_sheet];cols=3 if label.startswith('lots') else 2;rows=(len(subset)+cols-1)//cols;w,h=thumb
  sheet=Image.new('RGB',(cols*w*2,rows*(h+28)+40),(24,22,18));d=ImageDraw.Draw(sheet);d.text((12,10),f'td-210 {label} | reviewed Tenjin before / Kamome f05048b1 after | seed185',(245,229,195))
  for i,(before,after,key) in enumerate(subset):
   x=i%cols*w*2;y=40+i//cols*(h+28);d.text((x+6,y+4),key,(255,255,255))
   for j,path in enumerate([before,after]):
    image=Image.open(path).convert('RGB');image.thumbnail((w,h));sheet.paste(image,(x+j*w+(w-image.width)//2,y+28+(h-image.height)//2))
  path=out/f'{label}-{offset//per_sheet+1:02}.jpg';sheet.save(path,quality=92)
  manifest.append({'sheet':str(path.relative_to(qa)),'pairs':[{'before':str(a.relative_to(qa)),'after':str(b.relative_to(qa)),'id':k} for a,b,k in subset],'sha256':hashlib.sha256(path.read_bytes()).hexdigest()})
pairs=[]
for i in range(1022,1367):
 a=qa/f'native-before/lots/{i}/td-210-criterion-1-before.png';b=qa/f'native-after/lots/{i}/td-210-criterion-1-after.png'
 assert a.exists() and b.exists(),i
 pairs.append((a,b,str(i)))
sheets(pairs,'lots',12,(320,320))
pairs=[]
for i in range(1022,1367):
 a=qa/f'native-before/lots-overhead/{i}/td-210-criterion-1-before.png';b=qa/f'native-after/lots-overhead/{i}/td-210-criterion-1-after.png'
 if a.exists() and b.exists():pairs.append((a,b,str(i)))
if len(pairs)==345:sheets(pairs,'lots-overhead',12,(320,320))
for platform in ['native','browser']:
 if not (qa/f'{platform}-after/routes').exists():continue
 for hud in ['hud','world']:
  pairs=[]
  for a in sorted((qa/f'{platform}-before/routes').glob(f'*-{hud}-*/*before.png')):
   b=qa/f'{platform}-after/routes'/a.parent.name/a.name.replace('before','after')
   if b.exists():pairs.append((a,b,a.parent.name))
  sheets(pairs,platform+'-'+hud,6,(480,270))
(out/'manifest.json').write_text(json.dumps(manifest,indent=2));print('sheets',len(manifest))
