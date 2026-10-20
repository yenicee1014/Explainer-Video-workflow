"""Submit the public API graph to an already running local ComfyUI instance."""
import argparse
import json
from pathlib import Path
import time
from urllib.request import Request, build_opener, ProxyHandler
from urllib.error import HTTPError

ROOT = Path(__file__).resolve().parents[1]

def request(url, payload=None):
    req = Request(url, data=json.dumps(payload).encode() if payload is not None else None,
                  headers={'Content-Type': 'application/json'})
    try:
        with build_opener(ProxyHandler({})).open(req, timeout=30) as response:
            return json.load(response)
    except HTTPError as error:
        raise RuntimeError(f'ComfyUI HTTP {error.code}: {error.read().decode()}') from error

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', default='http://127.0.0.1:8190')
    args = parser.parse_args()
    if not args.url.startswith(('http://127.0.0.1:', 'http://localhost:')):
        raise ValueError('Verification is restricted to a local ComfyUI server')
    url = args.url.rstrip('/')
    graph = json.loads((ROOT/'workflows/weather-silent-api.json').read_text(encoding='utf-8'))
    info = request(url+'/object_info')
    assert all(n['class_type'] in info for n in graph.values()), 'Public nodes are not installed'
    submitted = request(url+'/prompt', {'prompt': graph, 'client_id': 'explainer-public-verification'})
    assert not submitted.get('node_errors'), submitted
    prompt_id = submitted['prompt_id']
    deadline = time.monotonic()+90
    while time.monotonic() < deadline:
        entry = request(url+'/history/'+prompt_id).get(prompt_id)
        if entry:
            break
        time.sleep(.3)
    else:
        raise TimeoutError('ComfyUI did not finish within 90 seconds')
    status = entry.get('status', {})
    if status.get('status_str') != 'success':
        raise RuntimeError(f'ComfyUI execution failed: {status}')
    result = json.loads(entry['outputs']['5']['text'][0])
    assert result['status'] == 'passed' and result['scenes'] == 40
    stats = request(url+'/system_stats')
    report = {'status': 'passed', 'prompt_id': prompt_id, 'nodes': len(graph),
              'links': 4, 'comfyui_version': stats['system'].get('comfyui_version'),
              'result': result, 'scope': 'Actual local ComfyUI API execution; not scientific expert approval'}
    (ROOT/'reports').mkdir(exist_ok=True)
    (ROOT/'reports/comfy-check.json').write_text(json.dumps(report, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=False, indent=2))
