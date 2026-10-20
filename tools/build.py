"""Portable deterministic silent-review pipeline (Python standard library only)."""
from pathlib import Path
import argparse
import json
import math
import xml.etree.ElementTree as ET
if __package__:
    from .diagrams import svg
else:
    from diagrams import svg

ROOT = Path(__file__).resolve().parents[1]

def project_path(project='projects/weather-ai'):
    path = (ROOT / project).resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError('Project must be inside this repository')
    return path

def load(project='projects/weather-ai'):
    p = project_path(project)
    return {'path': p, 'script': json.loads((p/'script.json').read_text(encoding='utf-8')),
            'timeline': json.loads((p/'timeline.json').read_text(encoding='utf-8')),
            'sources': json.loads((p/'sources.json').read_text(encoding='utf-8'))}

def validate(bundle):
    if not __debug__:
        raise RuntimeError('Validation requires Python without -O or PYTHONOPTIMIZE')
    s, t, refs = bundle['script'], bundle['timeline'], bundle['sources']
    if len(s['scenes']) != 40 or len(t['scenes']) != 40:
        raise ValueError('This release expects exactly 40 scenes')
    assert t['audio'] is False and math.isfinite(t['duration']) and t['duration'] > 0
    cursor = 0
    ids = set()
    for a, b in zip(s['scenes'], t['scenes']):
        assert a['id'] == b['id'] and a['id'] not in ids
        ids.add(a['id'])
        for key in ['title', 'kind', 'labels', 'narration', 'note', 'refs', 'chapter']:
            assert a[key] == b[key], f'Stale timeline metadata: {a["id"]} {key}'
        assert a['note'] and all(ref in refs and refs[ref]['verified'] for ref in a['refs'])
        assert all(math.isfinite(b[k]) for k in ['start','end','duration'])
        assert abs(b['start']-cursor) < 1e-6 and b['end'] > b['start']
        assert abs(b['end']-b['start']-b['duration']) < 1e-6
        captions = [c for c in t['captions'] if c['scene'] == a['id']]
        assert ''.join(c['text'] for c in captions) == a['narration'], f'Caption text differs: {a["id"]}'
        last = b['start']
        for c in captions:
            assert all(math.isfinite(c[k]) for k in ['start','end'])
            assert c['start'] >= last-1e-6 and c['end'] > c['start']
            assert c['end'] <= b['end']+1e-6
            last = c['end']
        cursor = b['end']
    assert abs(cursor-t['duration']) < 1e-6
    assert all(c['scene'] in ids for c in t['captions'])
    return bundle

def diagrams(bundle):
    p = bundle['path']/'assets/diagrams';p.mkdir(parents=True, exist_ok=True)
    for scene in bundle['timeline']['scenes']:
        text = svg(scene)
        ET.fromstring(text)
        (p/f'{scene["id"]}.svg').write_text(text, encoding='utf-8')
    return bundle

def stamp(seconds):
    n = round(seconds*1000)
    return f'{n//3600000:02}:{n//60000%60:02}:{n//1000%60:02},{n%1000:03}'

def captions(bundle):
    lines = [f'{i}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}\n'
             for i,c in enumerate(bundle['timeline']['captions'],1)]
    (bundle['path']/'captions.srt').write_text('\n'.join(lines), encoding='utf-8')
    return bundle

def review(bundle):
    p = ROOT/'reports';p.mkdir(exist_ok=True)
    t = bundle['timeline']
    report = {'status':'passed', 'scope':'structure, source IDs, caption text/timing, SVG generation only; not scientific expert approval',
              'project':str(bundle['path'].relative_to(ROOT)), 'scenes':len(t['scenes']),
              'captions':len(t['captions']), 'duration_seconds':t['duration'], 'audio':False}
    (p/'build-check.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    return json.dumps(report,ensure_ascii=False)

if __name__ == '__main__':
    parser = argparse.ArgumentParser();parser.add_argument('--project',default='projects/weather-ai')
    args = parser.parse_args()
    print(review(captions(diagrams(validate(load(args.project))))))
