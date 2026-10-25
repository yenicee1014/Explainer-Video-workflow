"""Photographic scene assignments for the revised, narration-led film."""
from pathlib import Path
import json

from full_film import ROOT, dump, plan

V2 = ROOT / "full-film-v2"
STYLE = (
    "Black-and-white observational documentary footage for a serious economics explainer. "
    "Neutral grayscale silver-gelatin photography, detailed faces and material textures, "
    "soft daylight, moderate contrast, clear readable composition. Original illustrative "
    "reconstruction. Natural restrained gestures, physically coherent objects and hands. "
    "Landscape 16:9. One continuous shot, gentle camera movement only. "
    "No subtitles, no readable lettering, no logos, no watermark, no graphic overlays. "
)

# Each action is small enough to remain legible in a single generated shot.
ASSETS = {
    "factory_close": (1, "工厂停工与离岗",
        "Medium wide shot outside a small American factory in 1931. A foreman in a wool coat "
        "locks the factory's iron gate. Three dismissed manual workers, wearing flat caps "
        "and worn jackets, pick up their lunch pails and walk away slowly. Smoke stacks are "
        "idle. Period correct clothing and street, no modern cars. The closed gate and "
        "workers leaving are both clearly visible."),
    "bank_queue": (1, "储户排队与银行压力",
        "Wide street-level shot of a modest American bank entrance in 1931. A long orderly "
        "queue of ordinary depositors in period coats waits outside heavy stone doors. "
        "A bank employee quietly speaks to the first person in line. Natural worried faces. "
        "The queue bends along the bank facade, no violence, no readable signs."),
    "exchange": (2, "1929年交易所内的混乱",
        "High angle medium wide shot inside a 1929 American stock exchange. Floor brokers "
        "in dark suits hurry between wooden trading desks while one broker studies a long "
        "ticker tape and another holds his head in his hands. Period correct telephones "
        "and paper. No digital screens, no modern equipment, no readable text."),
    "planning": (3, "开发商评估办公楼计划",
        "Over-the-shoulder medium shot of two contemporary East Asian property developers "
        "at a plain planning table. They spread a large architectural floor plan beside "
        "a scale model of an ordinary twelve-storey rectangular office building and a "
        "calculator. One points at the land parcel and the other makes budget notes. "
        "Architectural plans and people dominate, not a skyscraper."),
    "budget": (3, "土地、建造与运营成本",
        "Close tabletop documentary shot of an East Asian property finance analyst's hands "
        "sorting three folders beside a calculator, a small ordinary office building model, "
        "a construction material sample and a site plan. She calculates on the calculator, "
        "then checks a folder. Blank or indistinct document text, no readable numbers. "
        "Keep hands and objects stable and realistic."),
    "signature": (3, "银行借贷签约特写",
        "Close shot at an ordinary contemporary bank desk. An East Asian male property "
        "developer in a dark jacket receives a pen from a female loan officer, signs a "
        "single page of a thick loan contract and slides it back to her. Loan officer "
        "checks the signature. Faces partly visible above desk, natural anatomically "
        "correct hands. Paper contract and signing action are the main subject."),
    "tenant_visit": (3, "潜在租户实地看办公室",
        "Wide interior shot in a contemporary ordinary office floor with rectangular "
        "windows. An East Asian letting agent holds a lease folder and shows the space "
        "to two potential business tenants. One tenant checks where desks could go and "
        "the other examines the floor plan. The agent points to the usable floor area. "
        "No luxury penthouse, no exterior tower shot."),
    "growth": (3, "企业扩张与新增工位",
        "Medium wide shot in a busy contemporary East Asian company office. A manager "
        "welcomes two new employees and points to newly installed desks. Existing staff "
        "work in the background and a technician finishes placing an office chair. "
        "Ordinary corporate workplace, confident practical business activity."),
    "sites": (4, "多家开发商同时开工",
        "Elevated wide shot across four adjacent independent commercial construction "
        "sites in an East Asian city. Four different mid-rise concrete office buildings "
        "at different stages, each with its own tower crane and temporary perimeter. "
        "Cranes move slowly and concrete trucks enter different gates. Show clearly "
        "separate projects competing in the same district, no single landmark."),
    "lease_competition": (4, "多栋新楼争取同一批租户",
        "Medium wide shot in a commercial office leasing showroom. Three distinct "
        "East Asian property agents each stand beside a separate ordinary office "
        "building scale model. Only two potential corporate tenants stand together "
        "in front, comparing the competing brochures. The agents gesture toward "
        "their own models. Show limited tenants and multiple separate offers."),
    "tourism": (4, "地标观光的实际使用",
        "Wide shot on an enclosed high-rise observation deck in a modern Asian city. "
        "A handful of ordinary visitors use binoculars, photograph the skyline and "
        "walk along the glass railing. Clear practical tourist activity in a public "
        "observation deck, daylight, no recognizable brand, no dramatic stunt."),
    "investors": (4, "开发商、贷款人与投资者的共同预期",
        "Medium wide shot around a contemporary boardroom table. Three East Asian "
        "professionals, a property developer, a bank credit officer and a private "
        "investor, review one ordinary office project model, a valuation folder "
        "and a financial forecast. Each points to a different document and nods. "
        "The same set of assumptions is being shared across the table."),
    "cancel_order": (5, "企业取消扩张订单",
        "Medium close shot in a contemporary small company office. An East Asian "
        "business manager ends a phone call, removes an expansion floor plan from "
        "the active folder and places it in a closed folder. A stack of unopened "
        "office equipment boxes stands behind her. A quiet decision to postpone "
        "an office expansion, no dramatic acting."),
    "contraction": (5, "企业收缩办公面积",
        "Wide shot of an East Asian company's office being downsized. Workers "
        "unplug several computers and stack empty chairs while a manager compares "
        "a smaller floor plan with the existing office. Half the room is already "
        "unused and staff continue working in a smaller area. No factory setting."),
    "departure": (6, "租户搬走",
        "Medium wide shot in a contemporary office corridor. Two East Asian "
        "employees carry cardboard boxes of desk belongings out of a leased "
        "office while a property manager watches and receives a key from the "
        "last tenant. Through the open door, rows of empty desks are visible. "
        "Tenant departure, boxes, key handover and vacant space are all legible."),
    "vacancy": (6, "空置楼层与租金让步",
        "Slow lateral wide shot across a nearly empty contemporary office floor. "
        "Many unoccupied desk positions and disconnected monitors. At one side "
        "an East Asian property manager shows a revised lease folder to a "
        "prospective tenant, who considers it but hesitates. Broad daylight, "
        "vacancy rather than ruined or collapsed architecture."),
    "refinance": (6, "到期贷款的再融资谈判",
        "Medium shot in a bank meeting room. An East Asian developer brings an "
        "old loan folder to a female bank credit officer. She sets a new loan "
        "proposal next to the old contract and points at its repayment schedule. "
        "The developer compares the two pages with a calculator and looks "
        "concerned. Show old contract versus new proposal clearly as two folders."),
    "valuation": (6, "物业估值重估",
        "Medium wide shot of a contemporary property appraiser and a bank "
        "surveyor inspecting an underoccupied office floor. One measures floor "
        "space with a handheld laser device, while the other compares rental "
        "records and photographs empty units for a valuation report. Practical "
        "inspection of usable property, no construction damage."),
    "credit": (6, "贷款收紧传给其他企业",
        "Medium shot at a contemporary small-business loan interview. An East "
        "Asian workshop owner in work clothes brings an equipment purchase "
        "folder. The bank loan officer closes the application folder, pauses, "
        "and slides it back while the owner listens with concern. Restrained "
        "business conversation. Ordinary bank desk, no money raining."),
    "sample": (7, "把成功与失败案例一起检查",
        "High angle shot over an economic researcher's large worktable. An "
        "East Asian female researcher starts with two selected architectural "
        "photo clippings, then pulls a wider stack of case files into view "
        "and lays them out in a complete grid. Other building photographs, "
        "calendars and printed data sheets are present. Show the sample "
        "expanding from selected anecdotes to many cases, no readable text."),
    "precommit": (7, "先定标准，再检验新数据",
        "Medium shot of two East Asian economic researchers at a desk. They "
        "agree on a short checklist, place it visibly at the side, then open "
        "a sealed folder containing additional case records and compare "
        "the new records with the checklist. Printed sheets contain only "
        "indistinct markings. Methodical testing, no fabricated readable charts."),
    "stress": (8, "用更低租金和更高利息检查计划",
        "Medium close shot of an East Asian property financial reviewer at a "
        "desk with a calculator, a lease folder and a loan contract. She "
        "sets optimistic forecasts aside, calculates an alternative budget, "
        "and points to a shortfall on the new sheet while a developer listens. "
        "Calm analytical work, no readable paper text or screen text."),
    "ledger": (8, "核对账本与下一笔到期日",
        "Close overhead shot of a contemporary accountant's hands comparing "
        "a rental ledger, an ordinary paper calendar and a loan repayment "
        "schedule on a textured desk. She circles one calendar cell, checks "
        "it against the contract, then presses a calculator key. Papers have "
        "indistinct writing, the exact labels will be added in post-production."),
}

OLD = {
    "old_worker": 1, "old_construction": 2, "old_signing": 3,
    "old_sites": 4, "old_core": 5, "old_empty": 6,
    "old_research": 7, "old_review": 8,
}

# Ordered photographic beats per approved paragraph. Lists produce actual cuts
# within a paragraph, rather than a single generic insert for an entire chapter.
BEATS = {
    1: [
        ["esb_open"], ["esb_motion"],
        ["factory_close", "old_worker", "bank_queue"],
        ["esb_motion", "factory_close"], ["dubai_notice", "burj_motion"],
        ["esb_motion", "burj_motion", "sample"], ["sample"],
        ["signature", "ledger"],
    ],
    2: [
        ["exchange", "esb_build"], ["exchange", "esb_build"],
        ["esb_build", "old_construction"],
        ["planning", "esb_build", "esb_open"],
        ["sample", "precommit"], ["planning", "vacancy"],
    ],
    3: [
        ["planning"], ["budget"], ["planning", "budget", "tenant_visit"],
        ["signature"], ["tenant_visit", "growth"],
        ["budget", "old_signing"], ["signature", "tenant_visit"],
        ["planning", "signature"], ["old_signing", "budget"],
        ["growth", "sites"], ["growth", "investors", "vacancy"],
    ],
    4: [
        ["old_sites", "sites"], ["growth", "lease_competition"],
        ["signature", "old_signing"], ["sites"],
        ["lease_competition"], ["sites", "lease_competition"],
        ["tourism", "burj_motion"], ["tourism", "tenant_visit"],
        ["investors"], ["investors"],
        ["investors", "vacancy"],
    ],
    5: [
        ["old_core", "ledger"], ["petronas_motion", "petronas_photo"],
        ["exchange", "old_core"], ["cancel_order", "old_core"],
        ["growth", "contraction"], ["planning", "vacancy"],
        ["old_core", "contraction"], ["petronas_motion", "old_review"],
    ],
    6: [
        ["old_signing", "signature"], ["departure", "vacancy"],
        ["signature", "ledger"], ["refinance"],
        ["vacancy", "stress"], ["old_empty", "vacancy"],
        ["refinance", "tenant_visit"], ["refinance", "valuation"],
        ["valuation", "refinance"], ["credit"],
        ["departure", "stress", "valuation", "credit"],
        ["credit", "old_review", "investors"],
    ],
    7: [
        ["esb_motion", "burj_motion", "sample"],
        ["growth", "investors"], ["sample"],
        ["esb_open", "exchange"], ["precommit"],
        ["sample"], ["sample", "old_research"],
        ["paper_study", "old_research"], ["paper_study", "sample"],
        ["paper_debate", "old_research"], ["precommit"],
        ["burj_motion", "sample"],
    ],
    8: [
        ["old_review", "ledger"], ["tenant_visit", "old_review"],
        ["investors", "signature"], ["ledger", "refinance"],
        ["stress", "vacancy"], ["budget", "valuation"],
        ["growth", "petronas_motion"], ["stress", "signature"],
        ["esb_motion", "ledger"], ["ledger"],
    ],
}

PROOFS = {
    "factory_close": "锁上停工工厂的大门，工人提着饭盒离开",
    "bank_queue": "储户沿银行门口排队，呈现银行承压",
    "exchange": "1929年代交易员、纸带与交易所，区别于建筑工地",
    "planning": "开发商在办公楼模型和地块图上做决策",
    "budget": "计算器、成本文件与项目模型一起入镜",
    "signature": "贷款人递笔，开发商签署借款合同",
    "tenant_visit": "真实可见的租户看房与可用办公面积",
    "growth": "新员工与新增工位说明企业扩张",
    "sites": "四个独立工地和塔吊同时建设",
    "lease_competition": "多名代理、多个楼盘模型争取少量企业租户",
    "tourism": "观景台游客说明地标的非租金收益",
    "investors": "开发商、银行与投资者共同讨论同一组预测",
    "cancel_order": "企业把扩张计划从待执行文件中撤下",
    "contraction": "撤走电脑、堆起椅子，缩减实际办公空间",
    "departure": "租户搬箱离开并交还钥匙",
    "vacancy": "空工位和让步中的租约谈判",
    "refinance": "旧借款到期，新贷款方案与旧合同并置",
    "valuation": "估值人员检查空置率、租金记录和物业面积",
    "credit": "贷款申请退回，贷款收紧影响另一家企业",
    "sample": "从两个被选中的案例扩展到完整案例集合",
    "precommit": "先把判断标准放在桌上，再打开新案例检验",
    "stress": "下调收入、提高融资成本后的预算计算",
    "ledger": "账本、贷款还款表和到期日相互核对",
    "esb_open": "帝国大厦官网标注1931年的开幕仪式历史照片",
    "esb_build": "帝国大厦官网标注1930年的施工历史影像",
    "esb_motion": "帝国大厦实景照片的黑白动态编排，保持真实轮廓",
    "burj_motion": "SOM哈利法塔实景照片的黑白动态编排，保持真实轮廓",
    "petronas_motion": "双子塔设计事务所实景照片的动态编排，保留双塔与空中连桥",
    "petronas_photo": "双子塔官方建筑照片与1992至1999年时间线",
    "dubai_notice": "迪拜世界债务事件与哈利法塔开发商分开标注",
    "paper_study": "真实论文标题、作者、发表信息及研究结论",
    "paper_debate": "研究与评论的不同证据解释并置",
}


def make_plan():
    chapters = plan()
    result = []
    for ch in chapters:
        number = ch["id"]
        if len(BEATS[number]) != len(ch["paragraphs"]):
            raise ValueError(f"Incomplete mapping for chapter {number}")
        scenes = []
        for index, (para, shot, beats) in enumerate(zip(ch["paragraphs"], ch["shots"], BEATS[number]), 1):
            scenes.append({
                "scene": index, "narration": para, "mode": shot[0],
                "title": shot[1], "detail": shot[2], "assets": beats,
                "visible_evidence": [
                    PROOFS.get(a, f"上一版已生成、只在相应情境使用的 {a}") for a in beats
                ],
            })
        result.append({"chapter": number, "title": ch["title"], "scenes": scenes})
    V2.mkdir(exist_ok=True)
    dump(V2 / "storyboard.json", result)
    dump(V2 / "asset-plan.json", [
        {"id": key, "chapter": ch, "title": title, "planned_duration": 8, "prompt": STYLE + prompt}
        for key, (ch, title, prompt) in ASSETS.items()
    ])
    lines = [
        "# V2 逐段画面执行表", "",
        "沿用获准的完整旁白与配音。每一段都指定可见人物、物件和动作。",
        "所有经济机制为情境重建；历史建筑照片、来源说明与生成重建分别标注。", "",
    ]
    for ch in result:
        lines.extend([f"## {ch['chapter']:02d}｜{ch['title']}", ""])
        for sc in ch["scenes"]:
            lines.extend([
                f"### {ch['chapter']:02d}-{sc['scene']:02d} {sc['title']}", "",
                sc["narration"], "",
                "画面顺序：" + " → ".join(sc["visible_evidence"]), "",
            ])
    (V2 / "逐段画面执行表.md").write_text("\n".join(lines), encoding="utf-8")
    return result


if __name__ == "__main__":
    data = make_plan()
    print(f"{sum(len(c['scenes']) for c in data)} paragraphs mapped; {len(ASSETS)} new mechanism clips.")
