"""Generate native ComfyUI and API-format graphs without local absolute paths."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TYPES = ['EXLoad', 'EXValidate', 'EXDiagrams', 'EXCaptions', 'EXReview']
TITLES = ['01 读取公开讲稿与冻结计时', '02 检查来源、字幕与时间线',
          '03 生成确定性科学图解', '04 导出完整字幕', '05 生成无声审阅报告']

def graphs():
    nodes, api = [], {}
    for i, (kind, title) in enumerate(zip(TYPES, TITLES), 1):
        inputs = [] if i == 1 else [{'name': 'bundle', 'type': 'EX_BUNDLE', 'link': i-1}]
        nodes.append({'id': i, 'type': kind, 'pos': [50+(i-1)*340, 180],
                      'size': [310, 130], 'flags': {}, 'order': i-1, 'mode': 0,
                      'inputs': inputs,
                      'outputs': [{'name': 'STRING' if i == 5 else 'EX_BUNDLE',
                                   'type': 'STRING' if i == 5 else 'EX_BUNDLE',
                                   'links': [] if i == 5 else [i], 'slot_index': 0}],
                      'title': title, 'properties': {'Node name for S&R': kind},
                      'widgets_values': ['projects/weather-ai'] if i == 1 else []})
        api[str(i)] = {'class_type': kind, '_meta': {'title': title},
                       'inputs': {'project': 'projects/weather-ai'} if i == 1 else {'bundle': [str(i-1), 0]}}
    native = {'last_node_id': 5, 'last_link_id': 4, 'nodes': nodes,
              'links': [[i, i, 0, i+1, 0, 'EX_BUNDLE'] for i in range(1, 5)],
              'groups': [], 'config': {}, 'extra': {'ds': {'scale': 0.75, 'offset': [0, 0]}},
              'version': 0.4}
    return native, api

if __name__ == '__main__':
    folder = ROOT/'workflows'
    folder.mkdir(exist_ok=True)
    for name, graph in zip(['weather-silent.json', 'weather-silent-api.json'], graphs()):
        (folder/name).write_text(json.dumps(graph, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print('Generated 5 nodes / 4 links in native and API formats')
