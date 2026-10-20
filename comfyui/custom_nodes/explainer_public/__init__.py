"""Copy/symlink this folder into ComfyUI/custom_nodes; set EXPLAINER_REPO."""
import importlib.util
import os
from pathlib import Path
import sys

def engine():
    root = Path(os.environ.get('EXPLAINER_REPO', Path(__file__).resolve().parents[3])).expanduser().resolve()
    tools = root/'tools'
    if not (tools/'build.py').is_file():
        raise RuntimeError('Set EXPLAINER_REPO to the cloned Explainer-Video-workflow repository')
    spec=importlib.util.spec_from_file_location('explainer_public_engine', tools/'build.py',
                                               submodule_search_locations=[str(tools)])
    module=importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module

class EXLoad:
    @classmethod
    def INPUT_TYPES(cls):
        return {'required':{'project':('STRING',{'default':'projects/weather-ai'})}}
    RETURN_TYPES=('EX_BUNDLE',);FUNCTION='run';CATEGORY='Explainer / Silent review'
    @classmethod
    def IS_CHANGED(cls, project):
        # JSON inputs can change without the project widget changing.
        return float('nan')
    def run(self,project):return (engine().load(project),)

class EXValidate:
    @classmethod
    def INPUT_TYPES(cls):return {'required':{'bundle':('EX_BUNDLE',)}}
    RETURN_TYPES=('EX_BUNDLE',);FUNCTION='run';CATEGORY='Explainer / Silent review'
    def run(self,bundle):return (engine().validate(bundle),)

class EXDiagrams(EXValidate):
    def run(self,bundle):return (engine().diagrams(bundle),)

class EXCaptions(EXValidate):
    def run(self,bundle):return (engine().captions(bundle),)

class EXReview(EXValidate):
    RETURN_TYPES=('STRING',);OUTPUT_NODE=True
    def run(self,bundle):
        text=engine().review(bundle)
        return {'ui':{'text':[text]},'result':(text,)}

NODE_CLASS_MAPPINGS={'EXLoad':EXLoad,'EXValidate':EXValidate,'EXDiagrams':EXDiagrams,'EXCaptions':EXCaptions,'EXReview':EXReview}
NODE_DISPLAY_NAME_MAPPINGS={'EXLoad':'01 读取公开讲稿与冻结计时','EXValidate':'02 检查来源、字幕与时间线','EXDiagrams':'03 生成确定性科学图解','EXCaptions':'04 导出完整字幕','EXReview':'05 生成无声审阅报告'}
