"""Measured engineering layout, not designer-drawn concept art. Uses unchanged city.json."""
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
base=Path(__file__).resolve().parents[2]
data=json.loads((base/'data/lower_city/city.json').read_text());sites=json.loads((base/'data/fuel/stations.json').read_text())
im=Image.new('RGB',(1500,880),'#f1e7ce');d=ImageDraw.Draw(im);font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',18);big=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',27)
d.text((35,22),'ASAHI FUEL — measured station layout / td-206',font=big,fill='#352620')
d.text((35,65),'Technical graybox plan from active Lower City. Reuse td-174 kit; red fascia + cream enamel + amber digits.',font=font,fill='#352620')
for i,s in enumerate(sites):
 ox=45+i*750;oy=180;sc=11.;cx,cy=s['at'];
 def xy(p): return (ox+350+(p[0]-cx)*sc,oy+270-(p[1]-cy)*sc)
 d.text((ox,120),s['name'],font=big,fill='#352620');d.text((ox,152),f"Plan ({cx}, {cy}), grade 0 m; arc {s['arc']}",font=font,fill='#352620')
 for l in data['lots']:
  if any(abs(p[0]-cx)<38 and abs(p[1]-cy)<30 for p in l['p']):d.polygon([xy(p) for p in l['p']],fill='#c9aa76',outline='#352620')
 for a in data['roads']:
  pts=a['pts']
  if any(abs(p[0]-cx)<45 and abs(p[1]-cy)<38 for p in pts): d.line([xy(p) for p in pts],fill='#665b4c',width=int(a['w']*sc))
 def rect(x,z,w,h,col):
  p=xy([cx+x-w/2,cy-z+h/2]);q=xy([cx+x+w/2,cy-z-h/2]);d.rectangle((*p,*q),fill=col,outline='#352620',width=2)
 rect(0,0,30,20,'#ded2b8');rect(0,0,24,11,'#dd9c79')
 for x in [-9,-3,3,9]:
  for z in [-4.5,4.5]:rect(x,z,.5,.5,'#352620')
 for x in [-4.5,4.5]:
  rect(x,0,2,7,'#7a6e5e')
  for z in [-2,2]:rect(x,z,.8,.8,'#b22f24')
 rect(12,6.5,4,3,'#9f7843');rect(0,-7.2,4.6,2.2,'#66877f')
 d.line([xy([cx-16,cy+8]),xy([cx+16,cy+8])],fill='#348277',width=6)
 d.text((ox+90,oy+420),'30 x 20 m forecourt; 3.5 m front service lane',font=font,fill='#352620')
 d.text((ox+90,oy+454),'Two road openings; pumps + columns stay behind lane',font=font,fill='#352620')
 d.text((ox+90,oy+488),'Full fill ¥1,200. Tow ¥1,800 + fuel ¥1,200.',font=font,fill='#352620')
d.text((40,825),'No map/road/lot edits. Native ground + collision drive-in/out verification still required. Not gameplay evidence.',font=font,fill='#352620')
d.rectangle((0,0,1500,210),fill='#f1e7ce')
d.text((35,22),'ASAHI FUEL — measured station layout / td-206',font=big,fill='#352620')
d.text((35,65),'Technical graybox: unchanged road data, existing td-174 kit, enamel signage and clear service lanes.',font=font,fill='#352620')
for i,s in enumerate(sites):
 d.text((45+i*750,120),s['name'],font=big,fill='#352620')
 d.text((45+i*750,155),f"Plan {s['at']} / grade 0 m / road arc {s['arc']}",font=font,fill='#352620')
im.save(base/'qa/td-206/station-plan.png')
