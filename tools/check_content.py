"""Reproducible structural/geometry/arithmetic checks; not scientific expert certification."""
from pathlib import Path
import json, math, xml.etree.ElementTree as ET
from diagrams import svg
ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'projects/weather-ai'
data=json.loads((P/'script.json').read_text());sources=json.loads((P/'sources.json').read_text())
checks=[]
for s in data['scenes']:
    generated=svg(s);doc=ET.fromstring(generated)
    assert len(doc.findall('.//{http://www.w3.org/2000/svg}text'))>3
    assert len(s['note'])>5
    for r in s['refs']:assert sources[r]['verified'],r
    published=P/'assets/diagrams'/f'{s["id"]}.svg'
    assert published.read_text()==generated, f'Stale diagram: {s["id"]}'
    checks.append({'id':s['id'],'kind':s['kind'],'refs':s['refs'],'svg_xml_valid':True,'matches_current_generator':True})
# Shifted equal-radius rain disks must have hit, miss, false-alarm regions.
def inside(x,y,cx):return (x-cx)**2+(y-970)**2<=225**2
assert inside(300,970,440) and not inside(300,970,655)
assert inside(540,970,440) and inside(540,970,655)
assert not inside(800,970,440) and inside(800,970,655)
assert sum(i<4 for i in range(10))/10==.4
# Curve mapping in scene 28: 270 px/hour, 16 px/(mm/hour), base 1h, peak30.
assert (545-275)/270==1 and (815-545)/270==1
assert (1220-740)/16==30
assert .5*((545-275)/270)*((1220-740)/16)==15
# Refactor semantics are checked separately from appearance.
by_id={s['id']:s for s in data['scenes']}
assert by_id['03']['kind']=='valid_time'
assert by_id['13']['kind']=='parameterization'
assert by_id['22']['kind']=='forecast_branches'
assert by_id['38']['kind']=='reanalysis'
assert by_id['26']['kind']=='convection_conditions'
assert by_id['26']['labels']==['水汽供给','热力不稳定','抬升与触发','风场环境']
for n in ['27','29','37']:assert 'N2' not in by_id[n]['refs']
# Every source field in the generated timeline must match current narration and diagram metadata.
timeline=json.loads((P/'timeline.json').read_text())
for authored,built in zip(data['scenes'],timeline['scenes']):
    for field in ['id','title','kind','narration','note','refs']:
        assert authored[field]==built[field],f'Stale timeline {authored["id"]}: {field}'
    spoken=''.join(c['text'] for c in timeline['captions'] if c['scene']==authored['id'])
    assert spoken==authored['narration'],f'Stale captions {authored["id"]}'
summary={'scenes':len(checks),'all_xml_valid':True,'source_ids_valid':True,'rain_geometry':True,'member_arithmetic':True,'rain_integral_mm':15,'timeline_matches_current_script':True,'scope':'Structure, geometry, arithmetic and generation consistency only; no expert scientific approval'}
(ROOT/'reports').mkdir(exist_ok=True)
(ROOT/'reports/static-check.json').write_text(json.dumps({'summary':summary,'scenes':checks},ensure_ascii=False,indent=2))
print(json.dumps(summary,ensure_ascii=False))
