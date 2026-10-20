"""Public-package regression checks; no ComfyUI installation or network required."""
import copy
import importlib.util
import json
import math
from pathlib import Path
import sys
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT/'tools'))
import build
from workflows import graphs

spec = importlib.util.spec_from_file_location('test_public_nodes', ROOT/'comfyui/custom_nodes/explainer_public/__init__.py')
nodes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(nodes)

class PublicPipelineTests(unittest.TestCase):
    def setUp(self):
        self.bundle = build.load()

    def test_reference_project(self):
        build.validate(self.bundle)
        t = self.bundle['timeline']
        self.assertEqual((t['width'], t['height']), (1080, 1920))
        self.assertEqual(len(t['chapters']), 8)
        self.assertEqual(len(t['captions']), 167)
        self.assertAlmostEqual(t['duration'], 947.0416875)
        self.assertIs(t['audio'], False)

    def test_reject_external_paths(self):
        with self.assertRaises(ValueError):
            build.project_path('../outside')
        with self.assertRaises(ValueError):
            build.project_path('/tmp')

    def test_reject_stale_metadata(self):
        self.bundle['timeline']['scenes'][0]['title'] = 'stale'
        with self.assertRaises(AssertionError):
            build.validate(self.bundle)

    def test_reject_timeline_gap(self):
        self.bundle['timeline']['scenes'][1]['start'] += 1
        with self.assertRaises(AssertionError):
            build.validate(self.bundle)

    def test_reject_nonfinite_time(self):
        self.bundle['timeline']['duration'] = float('nan')
        with self.assertRaises(AssertionError):
            build.validate(self.bundle)

    def test_reject_altered_caption(self):
        self.bundle['timeline']['captions'][0]['text'] = 'altered'
        with self.assertRaises(AssertionError):
            build.validate(self.bundle)

    def test_reject_caption_overflow(self):
        self.bundle['timeline']['captions'][0]['end'] = 99999
        with self.assertRaises(AssertionError):
            build.validate(self.bundle)

    def test_reject_unknown_source(self):
        self.bundle['sources'].pop('E1')
        with self.assertRaises(AssertionError):
            build.validate(self.bundle)

    def test_generated_graphs_match_files(self):
        for name, expected in zip(['weather-silent.json', 'weather-silent-api.json'], graphs()):
            self.assertEqual(json.loads((ROOT/'workflows'/name).read_text(encoding='utf-8')), expected)

    def test_native_graph_links_and_schemas(self):
        native, api = graphs()
        self.assertEqual(len(native['nodes']), 5)
        self.assertEqual(len(native['links']), 4)
        for node in native['nodes']:
            cls = nodes.NODE_CLASS_MAPPINGS[node['type']]
            self.assertTrue(callable(getattr(cls(), cls.FUNCTION)))
            required = cls.INPUT_TYPES()['required']
            self.assertEqual(set(api[str(node['id'])]['inputs']), set(required))
        for link_id, source, slot, target, target_slot, kind in native['links']:
            self.assertIn(link_id, native['nodes'][source-1]['outputs'][slot]['links'])
            self.assertEqual(native['nodes'][target-1]['inputs'][target_slot]['link'], link_id)
            self.assertEqual(kind, 'EX_BUNDLE')

    def test_execute_api_graph_as_python_nodes(self):
        # This is a direct node regression test, not a ComfyUI server execution.
        _, graph = graphs()
        results = {}
        for key, node in graph.items():
            inputs = {k: results[v[0]][v[1]] if isinstance(v, list) else v for k, v in node['inputs'].items()}
            cls = nodes.NODE_CLASS_MAPPINGS[node['class_type']]
            result = getattr(cls(), cls.FUNCTION)(**inputs)
            results[key] = result['result'] if isinstance(result, dict) else result
        report = json.loads(results['5'][0])
        self.assertEqual(report['status'], 'passed')
        self.assertEqual(report['captions'], 167)

    def test_file_inputs_disable_stale_comfy_cache(self):
        self.assertTrue(math.isnan(nodes.EXLoad.IS_CHANGED('projects/weather-ai')))

    def test_engine_does_not_import_unrelated_diagrams(self):
        original = sys.modules.get('diagrams')
        sys.modules['diagrams'] = object()
        try:
            self.assertEqual(nodes.engine().svg(self.bundle['script']['scenes'][0]),
                             build.svg(self.bundle['script']['scenes'][0]))
        finally:
            if original is None:
                sys.modules.pop('diagrams', None)
            else:
                sys.modules['diagrams'] = original

    def test_srt_timestamp(self):
        self.assertEqual(build.stamp(3661.125), '01:01:01,125')

if __name__ == '__main__':
    unittest.main()
