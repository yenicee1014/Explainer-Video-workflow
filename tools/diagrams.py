"""Deterministic scientific SVG diagrams; no diffusion model, no invented observations."""
from html import escape
import math
BG='#F1EEE7'; INK='#181818'; RED='#DA291C'; GREY='#57544F'; LINE='#C8C2B8'
def text(x,y,t,size=36,fill=INK,bold=False,anchor='start'):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{700 if bold else 400}" text-anchor="{anchor}">{escape(str(t))}</text>'
def lines(x,y,t,size=34,width=24,fill=INK):
    return ''.join(text(x,y+i*size*1.45,t[i*width:(i+1)*width],size,fill) for i in range(math.ceil(len(t)/width)))
def line(x1,y1,x2,y2,color=LINE,w=3,dash=''):
    return f'<path d="M{x1},{y1} L{x2},{y2}" fill="none" stroke="{color}" stroke-width="{w}" stroke-dasharray="{dash}"/>'
def rect(x,y,w,h,fill='none',stroke=LINE,sw=2):
    return f'<rect x="{x}" y="{y}" width="{w}" height="{h}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def circle(x,y,r,fill='none',stroke=INK,sw=3):
    return f'<circle cx="{x}" cy="{y}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>'
def arrow(x1,y1,x2,y2):
    return f'<path d="M{x1} {y1} L{x2} {y2}" fill="none" stroke="{INK}" stroke-width="3" marker-end="url(#arrow)"/>'
def step(content,i):
    return f'<g class="reveal" data-at="{0.12+i*0.15:.2f}">{content}</g>'
def pipeline(labels):
    out=''
    for i,l in enumerate(labels):
        y=650+i*145
        out+=step(rect(150,y,780,104)+text(187,y+67,f'{i+1:02}',32,RED,True)+text(280,y+67,l,38,bold=True),i)
        if i<len(labels)-1:out+=arrow(540,y+108,540,y+138)
    return out

def diagram(s):
    k=s['kind']; labels=s['labels']; o=''
    if k in ['pipeline','satellite']:return pipeline(labels)
    if k=='ai':
        o+=text(110,620,'训练：从历史资料学习',38,RED,True)
        o+=step(rect(110,680,360,135)+lines(135,730,'历史状态与对应目标',32,9)+rect(610,680,360,135)+text(650,760,'模型训练',36,bold=True)+arrow(480,748,598,748),0)
        o+=step(arrow(790,830,790,1000)+text(110,960,'推理：输入当前状态',38,RED,True),1)
        o+=step(rect(110,1020,360,140)+lines(135,1075,'当前初始状态',34,8)+rect(610,1020,360,140)+text(645,1100,'已训练模型',34,bold=True)+arrow(480,1090,598,1090),2)
        o+=step(arrow(790,1170,790,1240)+rect(390,1250,580,120)+text(430,1325,'未来状态或概率分布',34,bold=True),3)
        o+=text(110,1450,'训练与推理是两个阶段，不是现场重新学一遍',29,GREY)
        return o
    if k=='convection_conditions':
        o+=text(110,620,'环境条件共同作用，不是串行步骤',36,RED,True)
        o+=step(rect(110,700,400,125)+text(310,777,'水汽供给',36,bold=True,anchor='middle')+rect(570,700,400,125)+text(770,777,'热力不稳定',36,bold=True,anchor='middle'),0)
        o+=step(rect(110,1100,400,125)+text(310,1177,'抬升与触发',36,bold=True,anchor='middle')+rect(570,1100,400,125)+text(770,1177,'风场环境',36,bold=True,anchor='middle'),1)
        o+=step(arrow(310,835,460,915)+arrow(770,835,620,915)+arrow(310,1090,460,1015)+arrow(770,1090,620,1015)+circle(540,965,90,'none',INK,3)+text(540,950,'共同影响',30,bold=True,anchor='middle')+text(540,997,'对流发展',30,bold=True,anchor='middle'),2)
        o+=text(110,1360,'云雨微物理影响降水；风场影响组织和移动',30,GREY)
        o+=text(110,1450,'满足部分条件 ≠ 雷暴必然发生',32,RED,True)
        return o
    if k=='forecast_branches':
        o+=text(110,620,'2025-02-25 · ECMWF 业务实例',34,RED,True)
        o+=step(rect(250,690,580,120)+text(290,765,'观测 + 短期背景预报',36,bold=True),0)
        o+=step(arrow(540,820,540,880)+rect(250,890,580,120)+text(290,965,'同化得到相同初始条件',36,bold=True),1)
        o+=step(arrow(440,1020,300,1100)+arrow(640,1020,780,1100)+rect(110,1110,380,140)+rect(590,1110,380,140)+text(300,1170,'物理预报',36,bold=True,anchor='middle')+text(300,1220,'IFS',30,anchor='middle')+text(780,1170,'AI 预报',36,bold=True,anchor='middle')+text(780,1220,'AIFS',30,anchor='middle'),2)
        o+=text(110,1390,'并行运行与互补使用，不是依次通过两个模式',30,GREY)
        return o
    if k=='reanalysis':
        o+=text(110,625,'回看历史：采用较一致的分析系统',36,RED,True)
        o+=step(rect(110,700,380,140)+lines(140,755,'历史观测及质量控制',32,9)+rect(590,700,380,140)+text(620,755,'模式与同化方法',32)+text(620,805,'误差描述',32),0)
        o+=step(arrow(300,850,430,980)+arrow(780,850,650,980)+rect(190,990,700,145)+text(235,1075,'历史大气状态估计',42,bold=True),1)
        o+=step(line(160,1250,930,1250,INK)+text(160,1325,'过去时刻 1 → 2 → 3 → …',36)+text(160,1430,'时间连续的资料集 ≠ 无误差真值',32,GREY),2)
        return o
    if k in ['matrix','metrics','decision']:
        for i,l in enumerate(labels):
            y=650+i*155
            o+=step(text(95,y+60,f'{i+1:02}',66,RED,True)+line(220,y,990,y)+text(230,y+64,l,42,bold=True),i)
        return o
    if k=='observations':
        o+=line(100,1240,980,1240,INK)
        for i,(name,y) in enumerate(zip(labels,[1100,920,700])):
            x=220+i*310
            o+=step(circle(x,y,35,RED,RED)+line(x,y+40,x,1235,LINE,2,'8 10')+text(x,y-70,['局地测量','体积采样','辐射视场'][i],32,anchor='middle')+text(110,1330+i*55,name,34),i)
        o+=text(110,610,'多种观测量 → 共同约束状态',34,GREY)
        return o
    if k=='radar':
        o+=line(105,1200,980,1200,INK,4)+text(760,1255,'地面',30)
        o+=f'<path d="M150 1170 Q510 1110 955 720 M150 1170 Q510 1120 955 860" stroke="{RED}" stroke-width="3" fill="none"/>'
        o+=step(rect(118,1150,64,50,INK,INK)+text(100,1310,'雷达天线',34),0)
        o+=step(circle(800,870,55,'none',INK)+text(730,750,'散射目标',36)+arrow(780,1020,780,1160)+text(560,1065,'下落时可能蒸发',30),1)
        o+=step(text(250,730,'距离增大 → 通常采样更高',34,RED,True)+text(185,1400,'回波强度 ≠ 地面雨量直接读数',34),2)
        return o
    if k=='assimilation':
        o+=step(rect(95,670,400,150)+text(130,755,labels[0],36,bold=True),0)
        o+=step(rect(585,670,400,150)+lines(620,725,labels[1],32,10),1)
        o+=arrow(300,830,450,1000)+arrow(785,830,630,1000)
        o+=step(rect(160,1010,760,170,'none',INK,3)+text(200,1070,'结合误差与状态关系',34,RED,True)+text(200,1130,labels[2],36,bold=True),2)
        o+=text(160,1320,'不是简单平均，也不是无误差真值',33,GREY)
        return o
    if k=='grid':
        for i in range(11):o+=line(110+i*86,690,110+i*86,1206,LINE,2)
        for j in range(7):o+=line(110,690+j*86,970,690+j*86,LINE,2)
        o+=f'<path d="M210 1060 C250 700 590 760 715 900 C900 1020 660 1240 420 1130 Z" fill="none" stroke="{INK}" stroke-width="6"/>'
        o+=step(line(110,1260,196,1260,RED,5)+text(110,1320,'Δx：网格采样间隔',34,RED,True),0)
        o+=step(text(110,610,'结构可以跨越多个网格',38,bold=True)+text(110,1410,'没有统一的“一个格点就能看清”规则',32),1)
        return o
    if k=='scales':
        for i,l in enumerate(labels):
            y=660+i*220
            o+=step(rect(110,y,850-i*190,135,'none',INK,3)+text(140,y+82,l,38,bold=True),i)
        o+=text(110,1390,'尺度关系为概念示意，非定量比例',30,GREY)
        return o
    if k=='terrain':
        o+=f'<path d="M100 1180 L180 1140 L260 1060 L320 1110 L380 880 L450 980 L510 720 L590 990 L660 920 L730 1120 L850 1090 L980 1180" fill="none" stroke="{INK}" stroke-width="5"/>'
        o+=step(f'<path d="M100 1195 H280 V1100 H460 V1000 H640 V1090 H820 V1185 H980" fill="none" stroke="{RED}" stroke-width="5"/>',1)
        o+=text(100,640,'黑线：概念中的连续地形',35)+text(100,710,'红线：一种离散表示示意',35,RED)
        o+=text(100,1350,'不代表某个实际模式的地形处理方式',31,GREY)
        return o
    if k=='trajectories' or k=='ensemble':
        o+=line(140,1220,970,1220,INK)+line(140,1220,140,640,INK)
        paths=5 if k=='trajectories' else 10
        for i in range(paths):
            end=720+i*(390/max(1,paths-1)); start=1050+i*3
            o+=step(f'<path d="M160 {start} C420 1040 530 {1010-i*18} 680 {900+i*8} S870 {end} 950 {end}" stroke="{RED if i==paths//2 else GREY}" stroke-width="{5 if i==paths//2 else 2}" fill="none"/>',min(i//3,3))
        o+=text(900,1290,'提前量 →',30,anchor='end')+text(170,600,'可能情景，不是真实模式输出',32,GREY)
        o+=text(140,1390,'纵向位置：仅表示状态差异，无物理单位',29,GREY)
        return o
    if k=='valid_time':
        o+=text(110,630,'模式起报 → 目标时刻',40,bold=True)
        o+=line(140,940,950,940,INK,4)
        o+=step(circle(180,940,12,RED,RED)+text(180,1020,'起报',34,anchor='middle')+circle(380,940,9,INK,INK)+text(380,1020,'产品发布',32,anchor='middle'),0)
        o+=step(rect(700,880,230,120,'none',RED,3)+text(815,1070,'有效时段',34,RED,True,anchor='middle')+line(815,880,815,1000,RED,2,'8 8'),1)
        o+=step(arrow(180,775,815,775)+line(180,790,180,900)+line(815,790,815,860)+text(480,725,'到该目标时刻的预报提前量',32,RED,True,anchor='middle'),2)
        o+=text(110,1270,'提前量以起报时刻为基点，不以打开手机为基点',30,GREY)
        o+=text(110,1370,'有效时段内的其他目标时刻，提前量也不同',30,GREY)
        return o
    if k=='parameterization':
        o+=text(110,620,'同一次模式计算中的两种处理',38,bold=True)
        o+=step(rect(110,710,380,190)+text(300,780,'可解析状态',38,bold=True,anchor='middle')+text(300,850,'显式数值求解',30,anchor='middle'),0)
        o+=step(rect(590,710,380,190)+text(780,780,'未解析影响',38,bold=True,anchor='middle')+text(780,850,'参数化表示',30,anchor='middle'),1)
        o+=step(arrow(500,750,580,750)+arrow(580,850,500,850)+arrow(300,920,440,1080)+arrow(780,920,640,1080)+rect(190,1090,700,140)+text(540,1175,'共同影响下一时刻状态',38,bold=True,anchor='middle'),2)
        o+=text(110,1380,'云微物理、湍流等处理依模式配置而异',32,GREY)
        return o
    if k=='time':
        o+=line(130,840,960,840,INK,4)
        for i,l in enumerate(labels):
            x=170+i*350
            o+=step(circle(x,840,11,RED,RED)+lines(x-60,940,l,34,6),i)
        o+=text(130,1170,'时间方向 →',32,GREY)+text(130,1280,'具体起止时刻以产品标注为准',34)
        return o
    if k=='rain':
        o+=step(text(110,670,'位置：两块雨区的落点',38,bold=True)+circle(500,790,65,'none',INK)+circle(640,790,65,'none',RED)+arrow(510,890,640,890),0)
        o+=step(text(110,980,'时间：同一地点的到达时刻',38,bold=True)+line(400,1120,920,1120,INK)+f'<path d="M400 1120 H470 L530 1020 L590 1120 H920" fill="none" stroke="{INK}" stroke-width="4"/><path d="M400 1120 H660 L720 1020 L780 1120 H920" fill="none" stroke="{RED}" stroke-width="4"/>',1)
        o+=step(text(110,1270,'强度：同一时窗的雨量差异',38,bold=True)+rect(440,1330,310,32,INK,INK)+rect(440,1390,190,32,RED,RED),2)
        o+=text(110,1475,'黑／红为参照与偏差示意，不含真实量值',28,GREY)
        return o
    if k=='displacement':
        o+=text(110,630,'相同阈值下的二值雨区',36,bold=True)
        o+=f'<defs><clipPath id="observed"><circle cx="440" cy="970" r="225"/></clipPath><pattern id="hatch" width="16" height="16" patternUnits="userSpaceOnUse"><path d="M0 16L16 0" stroke="{LINE}" stroke-width="3"/></pattern></defs>'
        o+=circle(440,970,225,'none',INK,5)+f'<circle cx="655" cy="970" r="225" fill="url(#hatch)" clip-path="url(#observed)"/>'
        o+=f'<circle cx="655" cy="970" r="225" fill="none" stroke="{RED}" stroke-width="5" stroke-dasharray="12 9"/>'
        o+=step(text(300,980,'漏报',40,bold=True)+text(540,975,'交叠',34,anchor='middle')+text(720,980,'空报',40,RED,True),1)
        o+=text(110,1320,'黑实线：观测示意',34)+text(570,1320,'红虚线：预报示意',34,RED)
        return o
    if k=='rain_time':
        o+=line(140,1220,950,1220,INK)+line(140,1220,140,660,INK)
        for n in range(4):
            x=140+270*n
            o+=line(x,1220,x,1235,INK)+text(x,1285,str(n),28,anchor='middle')
        o+=text(110,1230,'0',28,anchor='end')+text(110,750,'30',28,anchor='end')
        o+=f'<path d="M140 1220 H275 L410 740 L545 1220 H950" fill="none" stroke="{INK}" stroke-width="5"/>'
        o+=step(f'<path d="M140 1220 H545 L680 740 L815 1220 H950" fill="none" stroke="{RED}" stroke-width="5"/>',1)
        o+=text(140,620,'构造雨强（mm/h）',32,GREY)+text(600,1350,'相对时间（h）→',32)
        o+=text(140,1430,'每条曲线累计：½ × 1 h × 30 mm/h = 15 mm',29)
        return o
    if k=='neighborhood':
        o+=rect(110,670,860,600)
        o+=circle(540,970,200,'none',GREY,3)+circle(540,970,12,RED,RED)
        o+=step(text(540,890,'目标点',36,RED,True,anchor='middle')+text(540,1090,'统计邻域',36,anchor='middle'),1)
        o+=text(110,1370,'邻近发生 ≠ 目标点一定发生',36,bold=True)
        return o
    if k=='probability':
        o+=step(text(100,825,'40',220,RED,True)+text(450,825,'%',95,RED,True),0)
        for i,l in enumerate(labels[:3]):o+=step(line(100,965+i*120,970,965+i*120)+text(110,1030+i*120,l,38,bold=True),i)
        o+=text(100,1420,'概率针对一个完整定义的事件',34,GREY)
        return o
    if k=='members':
        for i in range(10):
            x=190+(i%5)*175;y=800+(i//5)*230
            o+=step(circle(x,y,55,RED if i<4 else BG,RED if i<4 else INK)+text(x,y+12,i+1,30,BG if i<4 else INK,True,'middle'),i//3)
        o+=text(110,1200,'4 / 10 = 40%',74,RED,True)
        o+=text(110,1320,'达到同一阈值的原始成员频率',32)+text(110,1390,'不是任何App的后台成员数声明',30,GREY)
        return o
    if k=='calibration':
        o+=line(190,1260,910,1260,INK)+line(190,1260,190,650,INK)
        o+=step(line(190,1260,910,650,RED,5),0)
        for n in [0,40,100]:
            o+=text(190+7.2*n,1320,f'{n}%',28,anchor='middle')+text(160,1270-6.1*n,f'{n}%',28,anchor='end')
        o+=text(330,1420,'预报概率 →',34)+text(180,600,'长期实际发生频率 ↑',32)
        o+=step(text(400,850,'理想校准参考',34,RED,True),1)
        o+=text(110,1500,'数学参考线；没有展示实测样本点',29,GREY)
        return o
    raise ValueError(k)

def svg(s,total=40):
    title=s['title']; out=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1080 1920" role="img" aria-label="{escape(title)}"><defs><marker id="arrow" markerWidth="9" markerHeight="9" refX="7" refY="3" orient="auto"><path d="M0 0L7 3L0 6" fill="none" stroke="{INK}" stroke-width="1.3"/></marker></defs><style>text{{font-family:system-ui,"PingFang SC","Microsoft YaHei",sans-serif}} .reveal{{transition:none}}</style>'''
    out+=rect(0,0,1080,1920,BG,BG)+rect(72,80,14,48,RED,RED)+text(110,117,'天气预报 / 科学解读',32,bold=True)+text(1008,117,f'{s["id"]} / {total}',28,GREY,anchor='end')
    out+=line(72,165,1008,165,INK,3)+text(72,232,f'第 {s["chapter"]:02} 章   {s["chapter_title"]}',30,RED,True)
    title_lines=math.ceil(len(title)/12)
    title_width=math.ceil(len(title)/title_lines)
    out+=lines(72,340,title,76,title_width)
    out+=diagram(s)
    out+=line(72,1530,1008,1530)+lines(72,1760,s['note'],28,32,GREY)+text(72,1870,'原理示意 / 非真实天气数据',26,GREY)+text(1008,1870,'依据 '+', '.join(s['refs']),26,GREY,anchor='end')
    return out+'</svg>'
