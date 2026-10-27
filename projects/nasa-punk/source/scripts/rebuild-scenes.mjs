const ink="#20211d", red="#cf352c", paper="#eeebdf", pale="#f7f4e9";
const escape=s=>String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll('"',"&quot;");

export function makeScenes(data,logoPath) {
  const scenes=[];
  for (const chapter of data.chapters) {
    const id=`nasa-${chapter.id}`;
    const key=n=>`${id}-${n}`;
    const group=(n,body,latent=false,extra="")=>`<g id="${key(n)}" ${latent?'class="latent"':""} ${extra}>${body}</g>`;
    const tx=(x,y,text,size=16,fill=ink,cls="",extra="")=>`<text x="${x}" y="${y}" font-size="${size}" fill="${fill===red?"#b82f27":fill}" class="${cls}" ${size<14&&cls==="mono"?'data-layout-ignore=""':""} ${extra}>${escape(text)}</text>`;
    const img=(name,x,y,w,h,ext="jpg",extra="")=>`<image href="../assets/rebuild/${name}.${ext}" x="${x}" y="${y}" width="${w}" height="${h}" preserveAspectRatio="${name.endsWith("-texture")?"none":"xMidYMid slice"}" ${extra}/>`;
    const worm=(x,y,w,color=red)=>`<svg x="${x}" y="${y}" width="${w}" height="${w*6.55/24}" viewBox="0 8.7 24 6.55"><path d="${logoPath}" fill="${color}"/></svg>`;
    const bg=(type="desk")=>img(`${type}-texture`,0,0,1280,720);
    const line=(n,d,color=red,width=2)=>`<path id="${key(n)}" d="${d}" fill="none" stroke="${color}" stroke-width="${width}" pathLength="1" stroke-dasharray="1" stroke-dashoffset="1"/>`;
    const stripe=(x,y,w,h=5,colors=["#4c5a68","#7a7f4e","#d2a85e","#a8432f"])=>colors.map((c,i)=>`<rect x="${x}" y="${y+i*h}" width="${w}" height="${h}" fill="${c}"/>`).join("");
    const photo=(name,x,y,w,h,angle=0,ext="jpg")=>`<g transform="rotate(${angle} ${x+w/2} ${y+h/2})" class="paper-shadow"><rect x="${x-7}" y="${y-7}" width="${w+14}" height="${h+14}" fill="${pale}"/>${img(name,x,y,w,h,ext)}</g>`;
    const label=(x,y,no,text,en="")=>`<g><rect x="${x}" y="${y-21}" width="${Math.max(148,text.length*19+49)}" height="${en?54:34}" fill="#191a16e8"/><rect x="${x+9}" y="${y-13}" width="24" height="19" fill="${paper}"/>${tx(x+12,y+1,no,11,ink,"mono")}${tx(x+43,y+2,text,19,pale,"cn",`font-weight="700"`)}${en?tx(x+10,y+23,en,9,"#c7c5b7","mono"):""}</g>`;
    const paperRect=(x,y,w,h)=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" fill="${paper}"/>`;
    const tape=(x,y,angle=0)=>`<rect x="${x}" y="${y}" width="112" height="29" fill="#d4cda6" opacity=".66" transform="rotate(${angle} ${x+56} ${y+14})"/>`;
    const grid=(x,y,w,h,step=24)=>Array.from({length:Math.floor(w/step)+1},(_,i)=>`<path d="M${x+i*step} ${y}V${y+h}" stroke="#b8b7a7" stroke-width=".65"/>`).join("")+Array.from({length:Math.floor(h/step)+1},(_,i)=>`<path d="M${x} ${y+i*step}H${x+w}" stroke="#b8b7a7" stroke-width=".65"/>`).join("");
    const sheet=(name,x,y,w,h,angle=0)=>photo(name,x,y,w,h,angle,"png");
    const arrows=(x,y)=>`<path d="M${x} ${y+80}V${y}l-9 13m9-13 9 13" fill="none" stroke="${red}" stroke-width="2"/>`;
    const panelBody=()=>{
      const holes=[];
      for(let x=30;x<1280;x+=100) for(const y of [38,675]) holes.push(`<circle cx="${x}" cy="${y}" r="2" fill="#929487"/>`);
      for(let y=50;y<670;y+=45) for(const x of [205,967]) holes.push(`<circle cx="${x}" cy="${y}" r="1.8" fill="#999b8e"/>`);
      return `${bg("metal")}<path d="M205 0V720M967 0V720M0 38H1280M0 675H1280" stroke="#9b9e91" fill="none"/>${holes.join("")}<rect x="829" y="120" width="295" height="158" rx="9" fill="none" stroke="#71766c" stroke-width="2"/><rect x="841" y="132" width="271" height="134" rx="6" fill="none" stroke="#92968a" stroke-dasharray="4 3"/>${tx(848,162,"COPY ACCESS",17,ink,"mono")}${tx(850,184,"PULL TAB / AS INSTRUCTED",8,ink,"mono")}${tx(72,145,"STA 2140",24,ink,"mono")}${tx(74,175,"LOX TANK",13,ink,"mono")}${tx(74,196,"A FWD",9,ink,"mono")}<path d="M80 556l28-46 28 46Z" fill="none" stroke="${ink}" stroke-width="2"/>${tx(102,548,"!",20,ink)}${tx(76,578,"LIFT POINT",9,ink,"mono")}<rect x="844" y="581" width="158" height="30" fill="none" stroke="${ink}"/>${tx(856,602,"DO NOT STEP",13,ink,"mono")}<g>${Array.from({length:12},(_,i)=>`<path d="M${1035+i*12} 610l18-28" stroke="${i%2?ink:"#c5a24d"}" stroke-width="6"/>`).join("")}</g>`;
    };
    let body="",motion="",actions=[];
    if(chapter.id==="opening"){
      body=bg()+group("camera",`${img("hangar",0,0,1280,720)}
        ${group("brackets",`<path d="M430 210v-22h28m304 0h28v22M430 323v22h28m304 0h28v-22" stroke="${ink}" fill="none" stroke-width="2"/>${tx(434,175,"NASA LOGOTYPE / WORM · 1975",10,ink,"mono")}`,true)}
        ${group("void",`<g transform="rotate(-5 620 275)" class="paper-shadow">${paperRect(431,209,361,121)}${tx(476,277,"VOID · 1992",25,"#5b5c51","mono")}</g>`,true)}
        ${group("identity",`${stripe(433,374,355,7)}${tx(433,435,"NASA-PUNK",28,ink,"",`font-weight="800"`)}${tx(433,457,"DESIGN VOCABULARY / 04",10,ink,"mono")}`,true)}`);
      motion=`tl.fromTo(q('camera'),{scale:1.07,x:-20},{scale:1,x:0,duration:4.2,ease:'power1.inOut'},0);R('brackets',A.red+.8);R('void',A.retired+.5);F('void',A.future+.1);R('identity',A.future+.6);`;
      actions=["red：实际箭体与字标建立对象；镜头停稳后出现定位角标。","retired：退役纸条覆盖字标；future：撤走纸条并接出风格彩条，保留阅读停留。"];
    }
    if(chapter.id==="wordmark"){
      body=bg()+group("board",`${img("paper-texture",90,62,1100,580)}${tape(60,69,-37)}${tape(1100,605,-38)}
        ${group("badge",`${img("meatball",315,190,220,185,"png")}${tx(575,295,"1974",76,ink,"",`font-weight="800"`)}${tx(578,343,'INSIGNIA · "THE MEATBALL"',13,ink,"mono")}`)}
        ${group("smallbadge",`${img("meatball",137,93,100,85,"png")}${tx(245,130,"1974",26,ink,"",`font-weight="800"`)}${tx(246,153,"NASA / IDENTITY PROPOSAL",8,ink,"mono")}`,true)}
        ${group("draftgrid",grid(177,228,930,298,23),true)}
        ${group("plain",tx(271,459,"NASA",178,ink,"",`font-weight="800"`),true)}
        ${group("word",worm(265,314,740,ink),true)}
        ${group("crossbars",`<path d="M527 439H589M874 439H936" stroke="${ink}" stroke-width="27"/>`,true)}
        ${group("cut",`<path d="M517 435H599M864 435H946" stroke="${red}" stroke-width="3"/>${tx(485,501,"REMOVE CROSSBAR",11,red,"mono")}${tx(831,501,"REMOVE CROSSBAR",11,red,"mono")}`,true)}
        ${group("rockets",`${arrows(558,205)}${arrows(903,205)}<path d="M543 268v-31q15-35 30 0v31m315 0v-31q15-35 30 0v31" fill="none" stroke="${red}" stroke-width="2"/>${tx(727,216,"VERTICAL THRUST",10,red,"mono")}`,true)}
        ${group("wormlabel",`${tx(415,559,'THE WORM · "蠕虫"',27,red,"",`font-weight="700"`)}${stripe(414,578,372,3)}`,true)}
        <rect x="936" y="568" width="187" height="42" stroke="#969889" fill="none"/>
        ${tx(947,582,"NASA / LOGOTYPE STUDY",7,ink,"mono")}${tx(947,597,"DANNE & BLACKBURN",9,ink,"mono")}`);
      motion=`F('badge',A.proposal-.3);R('smallbadge',A.proposal-.3);R('draftgrid',A.proposal);R('plain',A.proposal+.25);
F('plain',A.stroke);R('word',A.stroke);R('crossbars',A.stroke);
R('cut',A.crossbar+.55);tl.to(q('crossbars'),{opacity:0,y:45,duration:.75,ease:'power2.in'},A.crossbar+1.7);F('cut',A.crossbar+3.15);
R('rockets',A.thrust+.45);tl.fromTo(q('rockets'),{y:14},{y:-8,duration:1.3,ease:'power2.out',immediateRender:false},A.thrust+.8);
F('rockets',A.worm);R('wormlabel',A.worm+.3);tl.to(q('word')+' path',{fill:'${red}',duration:1},A.worm+.4);`;
      actions=["proposal：肉丸退至页眉，出现网格及四个字母。stroke：替换为统一笔画的真实字标向量。","crossbar：录音句子锚点显示并移走两根横杠；thrust：箭头指向两个 A 的顶端，结束后停留阅读。"];
    }
    if(chapter.id==="manual"){
      const fanNames=["manual-type","manual-color","manual-misuse","manual-logo"];
      body=bg()+group("fan",fanNames.map((n,i)=>sheet(n,410+i*20,91,382,539,(i-1.5)*11)).join(""))+
        group("original",sheet("manual-logo",420,73,425,575),true)+
        group("grid",`${sheet("manual-grid",199,65,880,610)}${line("measure","M261 447V568M275.3 447V568M289.6 447V568M303.9 447V568M256 552H309",red,1.5)}${tx(333,577,"3 格 = 1 个笔画宽",22,red,"cn")}`,true)+
        group("misuse",`${sheet("manual-misuse",421,65,427,578)}${group("crosses",`<path d="M484 310l58 58m0-58-58 58M641 319l55 53m0-53-55 53M633 482l58 56m0-56-58 56" fill="none" stroke="${red}" stroke-width="3"/>`,true)}`,true)+
        group("color",`${sheet("manual-color",420,63,426,579)}${tx(456,306,"只用指定红色",17,red,"cn")}`,true)+
        group("reject",`<g transform="rotate(4 965 233)">${paperRect(894,174,155,104)}<rect x="906" y="187" width="131" height="72" fill="#48b773"/><path d="M906 187l131 72m0-72-131 72" stroke="${red}" stroke-width="3"/></g><g transform="rotate(-4 971 399)">${paperRect(894,339,155,104)}<rect x="906" y="352" width="131" height="72" fill="#9258cb"/><path d="M906 352l131 72m0-72-131 72" stroke="${red}" stroke-width="3"/></g>`,true)+
        group("type",`${sheet("manual-type",420,63,426,579)}`,true)+
        group("applications",`${group("letter",sheet("manual-letter",148,92,273,422,-4),true)}${group("truck",sheet("manual-truck",479,75,271,211,2),true)}${group("aircraft",sheet("manual-aircraft",799,82,292,203,-3),true)}${group("shuttle",sheet("manual-shuttle",461,342,310,235,1),true)}${group("uniform",sheet("manual-uniform",819,344,286,237,3),true)}`,true);
      body+=[["b1","01","形状不重画","ORIGINAL ARTWORK"],["b2","02","不许乱用","PROHIBITED USES"],["b3","03","只用指定红色","ONE RED"],["b4","04","字体与秩序","TYPOGRAPHY"]].map(([n,no,txt,en])=>group(n,label(52,64,no,txt,en),true)).join("");
      motion=`R('original',A.original);F('fan',A.original);R('b1',A.original);
F('original',A.grid);R('grid',A.grid);D('measure',A.grid+2.2,1.2);
F('grid',A.misuse);F('b1',A.misuse);R('misuse',A.misuse);R('b2',A.misuse);R('crosses',A.misuse+1.2,1.1);
F('misuse',A.red);F('b2',A.red);R('color',A.red);R('b3',A.red);R('reject',A.reject+.2);
F('color',A.type);F('reject',A.type);F('b3',A.type);R('type',A.type);R('b4',A.type);
F('type',A.letter);F('b4',A.letter);R('applications',A.letter);R('letter',A.letter);
R('truck',A.vehicles);R('aircraft',A.vehicles+.65);R('shuttle',A.vehicles+1.3);R('uniform',A.uniform);`;
      actions=["original / grid：实际手册页切入；按实测旁白锚点画出三格与笔宽的测量关系。","misuse：红叉覆盖错误示范；red / reject：指定红色与冲突色分层出现。","letter / vehicles / uniform：同一套规则逐步延伸至五种实物表面。"];
    }
    if(chapter.id==="roll"){
      body=bg()+group("saturn",img("saturn",0,0,1280,720))+group("diagram",`
        <defs><linearGradient id="${key("metal")}" x1="0" x2="1"><stop offset="0" stop-color="#a5a69c"/><stop offset=".45" stop-color="#fbf9ef"/><stop offset="1" stop-color="#b1b3a7"/></linearGradient></defs>
        <path d="M440 607V249l14-42V142l16-63 16 63v65l14 42v358Z" fill="url(#${key("metal")})" stroke="#a6a79a"/>
        <path d="M440 316h60M440 424h60M440 530h60" stroke="#777b6e"/>
        <rect x="440" y="329" width="31" height="59" fill="${ink}"/><rect x="470" y="435" width="30" height="77" fill="${ink}"/>
        ${line("leader","M500 464H608L730 315","#e2dfce",1)}
        ${group("disc",`<circle cx="855" cy="292" r="105" fill="${paper}" stroke="#9b9d8b" stroke-width="2"/><path d="M855 292V187a105 105 0 0 1 105 105ZM855 292v105a105 105 0 0 1-105-105Z" fill="#10120e"/>`)}
        ${tx(731,124,"ROLL / ORIENTATION",18,paper,"mono")}${label(707,503,"01","黑白姿态标记","ROLL PATTERN")}
        ${group("rotation",`${arrows(1033,228)}${tx(769,456,"0° → 270°",17,paper,"mono")}`,true)}`,true);
      motion=`F('saturn',A.marks+.45);R('diagram',A.marks+.4,.7);D('leader',A.marks+1.2);
R('rotation',A.rotate);tl.to(q('disc'),{rotation:270,svgOrigin:'855 292',duration:4.4,ease:'none'},A.rotate+.25);tl.to(q('diagram'),{scale:.94,svgOrigin:'640 360',duration:.8},A.result);`;
      actions=["marks：从火箭照片切到对应黑白标记的示意图，引线连接箭体与端面。","rotate：端面绕中心旋转 270°；固定箭头和黑白相位保持可比较，动作结束后停留。"];
    }
    if(chapter.id==="retirement"){
      body=group("surface",panelBody()+
        group("rivet-zoom",`<rect x="302" y="201" width="399" height="254" rx="12" fill="none" stroke="#777d70" stroke-width="2"/>${Array.from({length:9},(_,i)=>`<circle cx="${317+i*46}" cy="214" r="3" fill="#888d80"/><circle cx="${317+i*46}" cy="442" r="3" fill="#888d80"/>`).join("")}`)+
        group("word",worm(338,311,610),true)+
        group("tagfocus",`${line("tagline","M326 171L422 123H595",red,1.4)}${label(422,106,"02","编号 / 方向 / 警告","SMALL FUNCTIONAL LABELS")}`,true)+
        group("memo",`<g class="paper-shadow" transform="rotate(2 696 345)">${img("paper-texture",488,67,379,562)}${tx(518,108,"MEMO",15,ink,"mono")}<path d="M518 124H831" stroke="${ink}"/>
        ${tx(517,202,"1992",70,ink,"",`font-weight="800"`)}${tx(520,232,"旧标志回归 · 新字标退役",13,ink,"cn")}
        ${group("memotext",`${tx(518,326,"阿波罗时代的记忆",24,ink,"cn",`font-weight="700"`)}${tx(518,371,"也在决定一个机构",24,ink,"cn",`font-weight="700"`)}${tx(518,414,"选择怎样的形象。",24,ink,"cn",`font-weight="700"`)}`,true)}
        ${tx(519,580,"IDENTITY / PEOPLE / INSTITUTION",8,ink,"mono")}</g>`,true)+
        group("meatball",`${paperRect(927,306,122,112)}${img("meatball",933,313,112,94,"png")}`,true)+
        group("covers",Array.from({length:5},(_,i)=>group(`cover${i}`,`<g class="paper-shadow" transform="rotate(${i%2?4:-4} ${350+i*113} 385)">${img("paper-texture",320+i*112,294+(i%2)*30,145,179)}</g>`,true)).join(""),true)+
        group("voidstamp",tx(449,569,"RETIRED · 1992",22,red,"mono"),true));
      motion=`R('tagfocus',A.label);D('tagline',A.label+.4);F('tagfocus',A.identity);R('word',A.identity);R('memo',A.year);R('meatball',A.year+.7);R('memotext',A.memo+.2);F('memo',A.cover-.15);R('covers',A.cover);${Array.from({length:5},(_,i)=>`R('cover${i}',A.cover+${i*.6});`).join("")}R('voidstamp',A.retire+.3);`;
      actions=["panel / label：工程面板与标签建立功能对应；identity：字标落到设备表面。","year：1992 备忘录进入；cover：纸片逐块覆盖字标并换回圆形徽章，说明身份更替。"];
    }
    if(chapter.id==="reissue"){
      body=bg()+group("book",`<g class="paper-shadow">${paperRect(471,78,344,528)}<path d="M815 78l12 9v528l-12-9" fill="#bcbba9"/><path d="M478 81v521" stroke="#d2d0bf" stroke-width="4"/>${worm(516,219,253)}${tx(504,515,"Graphics Standards Manual",15,ink,"",`font-weight="700"`)}${tx(506,541,"NATIONAL AERONAUTICS",7,ink,"mono")}${tx(506,554,"AND SPACE ADMINISTRATION",7,ink,"mono")}</g>`)+
        group("fund",`${tx(164,269,"2015",65,paper,"",`font-weight="800"`)}${tx(166,304,"MANUAL / REISSUED",11,"#c5c2b3","mono")}<path d="M166 336H389" stroke="#8d8e80" stroke-width="2"/>${tx(167,371,"从内部规范",21,paper,"cn")}${tx(167,407,"到设计师的工具书",21,paper,"cn")}`,true)+
        group("system",`${sheet("manual-color",931,145,183,266,5)}${sheet("manual-logo",901,210,190,271,-3)}`,true)+
        group("return",`${img("hangar",0,0,1280,720)}${tx(74,99,"2020",73,pale,"",`font-weight="800"`)}${label(75,144,"↗","蠕虫重返火箭","THE WORM RETURNS")}`,true);
      motion=`tl.fromTo(q('book'),{scale:1.1,svgOrigin:'640 350'},{scale:1,svgOrigin:'640 350',duration:2.5,ease:'power2.out'},0);R('fund',A.fund);R('system',A.system);F('book',A.return);F('fund',A.return);F('system',A.return);R('return',A.return,.8);`;
      actions=["book：复刻封面作为连续对象；fund / system：出版与视觉系统的关系从书旁展开。","return：箭体照片接回开场对象，2020 年份作为历史锚点。"];
    }
    const constellation=(x,y,r)=>`<g><circle cx="${x}" cy="${y}" r="${r}" fill="#47617b"/><path d="M${x-r*.8} ${y+r*.5}q${r*.8}-${r*.7} ${r*1.6} 0" fill="none" stroke="#aa392c" stroke-width="${r*.17}"/><path d="M${x-r*.8} ${y+r*.35}q${r*.8}-${r*.7} ${r*1.6} 0" fill="none" stroke="#d8a84f" stroke-width="${r*.12}"/><path d="M${x-24} ${y-31}l6 10 12 1-9 8 2 12-11-6-11 6 2-12-9-8 12-1Z" fill="#ece7d6"/><circle cx="${x+40}" cy="${y-2}" r="3" fill="#ddd8c8"/><circle cx="${x-45}" cy="${y+11}" r="3" fill="#ddd8c8"/></g>`;
    if(chapter.id==="starfield"){
      body=bg()+group("site",`${img("starfield-landscape",0,49,1280,527)}<rect width="1280" height="45" fill="${paper}"/>
        ${tx(28,29,"S T A R F I E L D",20,ink)}${tx(410,28,"DISCOVER     FEATURES     EXPANSIONS     MEDIA",11,ink,"mono")}
        ${stripe(0,576,1280,8,["#bc2928","#db6939","#d6ae55","#55728c"])}
        ${tx(36,612,"NASA-PUNK / A TACTILE FUTURE",19,pale,"mono")}`)+
        group("photos",`${photo("apollo-detail",221,140,283,324,-4)}${photo("astronaut",752,144,299,324,3)}
        ${tx(223,495,"APOLLO / NASA",11,pale,"mono")}${tx(752,495,"STARFIELD / BETHESDA",11,pale,"mono")}`,true)+
        group("tactile",`<g class="paper-shadow" transform="rotate(-3 650 355)">${img("paper-texture",311,219,665,229)}
        ${tx(343,264,"NASA-PUNK / ART DIRECTION",12,ink,"mono")}<path d="M342 278H936" stroke="${ink}"/>
        ${tx(343,326,"可触摸的未来",37,ink,"cn",`font-weight="700"`)}${tx(344,371,"实体开关 · 真实材料 · 使用痕迹",23,ink,"cn")}
        ${line("tactileline","M342 388H879",red,2)}</g>`,true)+
        group("patch",`${paperRect(0,0,1280,720)}${constellation(642,326,113)}${stripe(293,496,694,8)}${tx(450,576,"CONSTELLATION / IDENTITY",15,ink,"mono")}`,true)+
        group("type",`${label(756,447,"04","横向加宽的无衬线","UNIVERS / EXTENDED")}${line("wide","M332 404H957M332 394v20M957 394v20",paper,1.5)}`,true);
      motion=`tl.to(q('site'),{opacity:.28,duration:.7},A.photos);R('photos',A.photos);F('photos',A.tactile);F('site',A.tactile);R('tactile',A.tactile);D('tactileline',A.tactile+1.5);
F('tactile',A.patch);R('patch',A.patch);F('patch',A.type);tl.to(q('site'),{opacity:1,duration:.6},A.type);R('type',A.type);D('wide',A.type+1.1);`;
      actions=["photos：并置真实航天与游戏宇航服，说明可信未来的参考关系。","tactile：实体开关、材料与痕迹进入说明纸；patch：徽章和彩条聚合为身份。type：标题两侧出现测量边界。"];
    }
    if(chapter.id==="layers"){
      const frame=`<rect x="60" y="72" width="1160" height="580" fill="${paper}"/>${img("storage",73,86,1134,554)}`;
      const overlay=(n,shape,x,y,no,title,en)=>group(n,`${shape}${label(x,y,no,title,en)}`,true);
      body=bg()+group("camera",frame+
        overlay("base",line("base-line","M644 362L975 287L1118 320",paper,2),870,265,"01","浅色的真实硬件","MATERIAL / WHITE HARDWARE")+
        overlay("seams",`${line("seam1","M1042 98L960 615",red,2)}${line("seam2","M108 466L955 616",red,2)}${line("seam3","M912 353L921 458",red,2)}`,120,153,"02","接缝 / 面板 / 拆装","STRUCTURE / SEAMS")+
        overlay("labels",`<rect x="284" y="499" width="190" height="45" fill="none" stroke="${paper}" stroke-width="2"/>${line("labels-line","M375 501L398 468H586",paper,1.5)}`,399,454,"04","编号与方向标签","STOW 84S / THIS SIDE UP")+
        overlay("patch",`<ellipse cx="816" cy="388" rx="79" ry="43" fill="none" stroke="${red}" stroke-width="2"/>${line("patch-line","M859 364L947 291H1148",paper,1.4)}`,875,270,"05","身份徽章与复古彩条","PATCH / IDENTITY")+
        overlay("accent",`<rect x="768" y="419" width="78" height="83" fill="none" stroke="${red}" stroke-width="3"/>${line("accent-line","M810 497L868 563H1071",paper,1.5)}`,830,554,"06","只强调关键的拉片","ONE ACCENT / PULL")+
        overlay("wear",`<ellipse cx="532" cy="217" rx="123" ry="91" fill="none" stroke="${red}" stroke-width="2"/>${line("wear-line","M619 182L731 145H938",paper,1.5)}`,740,139,"07","裂纹与手写提醒","WEAR / DON'T USE"))+
        group("hazard",`${paperRect(218,122,809,430)}<rect x="235" y="139" width="775" height="395" fill="#101d23"/>
        ${Array.from({length:15},(_,i)=>`<path d="M274 ${179+i*19}l-18 18" stroke="${paper}" stroke-width="7"/>`).join("")}
        ${tx(326,210,"LOAD GAME",15,paper,"mono")}<path d="M327 230H519M327 260H519M327 290H519" stroke="#7e8985" stroke-width="2"/>
        ${tx(590,349,"STARFIELD",37,paper)}<circle cx="710" cy="334" r="83" fill="none" stroke="${paper}" stroke-width="1.5"/>
        ${label(239,587,"03","为机器与安全服务的图案","FUNCTIONAL GRAPHICS")}${line("hazard-line","M260 279L149 377H75",red,2)}`,true);
      motion=`tl.fromTo(q('camera'),{scale:.87,svgOrigin:'640 360'},{scale:1,svgOrigin:'640 360',duration:2,ease:'power2.out'},.1);
R('base',A.base+.3);D('base-line',A.base+.6);F('base',A.seams);
R('seams',A.seams);D('seam1',A.seams+.5);D('seam2',A.seams+1);D('seam3',A.seams+1.4);F('seams',A.hazard);
R('hazard',A.hazard);D('hazard-line',A.hazard+1.5);F('hazard',A.labels);
R('labels',A.labels);D('labels-line',A.labels+.5);F('labels',A.patch);
R('patch',A.patch);D('patch-line',A.patch+.5);F('patch',A.accent);
R('accent',A.accent);D('accent-line',A.accent+.5);F('accent',A.wear);
R('wear',A.wear);D('wear-line',A.wear+.5);
tl.to(q('camera'),{scale:1.3,x:-55,y:45,svgOrigin:'540 260',duration:1.2,ease:'power2.inOut'},A.wear+1.3);
tl.to(q('camera'),{scale:1,x:0,y:0,duration:1.2,ease:'power2.inOut'},A.punk+1.5);`;
      actions=["whole / base：保持同一张游戏截图，逐层解释材料。seams：引线沿真实面板边界绘制。","hazard：菜单侧的斜纹单独提取；labels / patch / accent：标注依次锚定编号、徽章、红色拉片。","wear：圈出裂纹与 DON'T USE 贴纸；镜头连同引线移动，之后退回全貌。"];
    }
    if(chapter.id==="lonetrail"){
      body=bg()+group("screen",`${photo("ark",65,127,1150,488,-1)}${tx(71,95,"ARKNIGHTS / LONE TRAIL",12,paper,"mono")}`)+
        group("stripes",`${line("stripeleader","M114 180L170 91H377",paper,1.4)}${line("orangeleader","M1063 552L1135 621H1201",paper,1.4)}
        ${label(180,78,"01","竖条 / 项目代号","PROJECT IDENTIFICATION")}${label(843,619,"02","唯一的橙色强调","ORANGE ACCENT")}`,true)+
        group("notice",`${photo("ark-notice",290,221,777,154,-2)}${label(291,186,"+","米白的公告页","CREAM NOTICE PANEL")}`,true)+
        group("rings",`${photo("ark-rings",862,353,242,242,5)}${photo("ark-character",104,292,159,290,-5)}<circle cx="984" cy="475" r="118" fill="none" stroke="${red}" stroke-width="2"/>`,true);
      motion=`R('stripes',A.stripes);D('stripeleader',A.stripes+.3);D('orangeleader',A.stripes+1.7);
F('stripes',A.notice);tl.to(q('screen'),{opacity:.4,duration:.5},A.notice);R('notice',A.notice);R('rings',A.rings);`;
      actions=["stripes：竖条与橙色按钮分别连接到说明，强调功能与身份关系。","notice / rings：公告页面和圆形视觉进入前景，保留原界面作对照。"];
    }
    const board=()=>`${sheet("manual-color",96,172,151,224,-3)}${sheet("manual-logo",263,175,170,238,2)}
      ${sheet("manual-truck",120,435,177,139,-3)}${sheet("manual-grid",319,445,156,141,1)}
      ${photo("storage",512,242,456,229,2)}${photo("starfield-landscape",610,70,300,116,-2)}
      ${photo("ark",620,525,296,125,1)}${photo("martian",1030,237,154,112,-2)}`;
    if(chapter.id==="branches"){
      body=bg()+group("examples",`${photo("martian",190,106,530,321,-2)}${tx(198,454,"THE MARTIAN / TERRITORY STUDIO",10,paper,"mono")}
        ${group("fashion",`${photo("preston",786,197,350,255,3)}${tx(784,487,"HERON PRESTON × NASA",10,paper,"mono")}`,true)}`)+
        group("board",board(),true)+group("connections",`${line("connect1","M431 292L510 329",paper,1)}${line("connect2","M299 501L512 391",paper,1)}${line("connect3","M741 473L763 519",paper,1)}${tx(443,681,"SAME ROOTS / DIFFERENT CHOICES",12,paper,"mono")}`,true);
      motion=`R('fashion',A.fashion);F('examples',A.board);R('board',A.board);R('connections',A.choices);D('connect1',A.choices+.2);D('connect2',A.choices+.6);D('connect3',A.choices+1);`;
      actions=["martian / fashion：电影与服装作为可比较的实例进入画面。","board / choices：展开关联板，连接手册、游戏与应用，说明共同规则与不同取舍。"];
    }
    if(chapter.id==="arc"){
      body=bg()+group("poster",`${photo("arc-poster",193,103,894,504,-1.5)}${tx(195,641,"ARC RAIDERS / EMBARK STUDIOS",11,paper,"mono")}`)+
        group("world",`${photo("arc-machine",133,96,1008,533,1.2)}`,true)+
        group("influence",`<g class="paper-shadow" transform="rotate(1.5 647 333)">${img("paper-texture",256,180,769,295)}
        ${tx(289,222,"ARC RAIDERS / VISUAL INFLUENCES",12,ink,"mono")}<path d="M288 239H989" stroke="${ink}"/>
        ${tx(289,293,"70s / 80s FASHION",32,ink,"",`font-weight="800"`)}${tx(289,353,"UTILITARIAN TECH",32,ink,"",`font-weight="800"`)}${tx(289,413,"TINKERED / POST-APOC",32,ink,"",`font-weight="800"`)}${line("influence-line","M289 427H901",red,2)}</g>`,true)+
        group("player",`${photo("arc-player",143,109,996,415,-1)}${label(156,568,"03","大胆的颜色 / 醒目的轮廓","BOLD COLOR / SILHOUETTES")}`,true)+
        group("graphics",`${photo("arc-bully",110,240,505,286,-2)}${photo("arc-stiletto",668,234,505,286,2)}${tx(111,200,"PROMOTIONAL GRAPHICS / EMBARK",11,paper,"mono")}`,true)+
        group("colors",`${stripe(174,566,945,8,["#aa3033","#dca740","#5b9fc3","#6ca756"])}${label(808,115,"04","旧纸 / 斜彩条 / 粗体字","WEATHERED / MANY COLORS")}`,true)+
        group("finalboard",`${board()}${photo("arc-poster",963,80,226,127,1)}${photo("arc-stiletto",963,489,225,126,-1)}`,true);
      motion=`F('poster',A.world);R('world',A.world);F('world',A.influence);R('influence',A.influence);D('influence-line',A.influence+2.4);
F('influence',A.silhouette);R('player',A.silhouette);F('player',A.graphics);R('graphics',A.graphics);
R('colors',A.colors);F('graphics',A.interpret);F('colors',A.interpret);R('finalboard',A.interpret);`;
      actions=["world：机器与旧装备解释世界状态。influence：服装、技术、拼装材料分行呈现。","silhouette：比较人物与环境色块；graphics / colors：旧纸、斜彩条、粗体字作对照。interpret：回到多案例关系板。"];
    }
    if(chapter.id==="style"){
      const names=["底材","结构","功能图案","功能标签","身份","强调","痕迹"];
      const english=["MATERIAL","STRUCTURE","PATTERN","LABEL","IDENTITY","ACCENT","WEAR"];
      const symbols=[
        `<path d="M54 94V47q0-32 17-39 17 7 17 39v47Z" fill="none" stroke="${ink}" stroke-width="1.3"/><path d="M54 59h34M54 69h34M54 79h34" stroke="#9a9b8e"/>`,
        `${grid(32,12,78,81,13)}<rect x="32" y="12" width="78" height="81" fill="none" stroke="${ink}"/>`,
        Array.from({length:6},(_,i)=>`<path d="M${27+i*12} 85l47-67" stroke="${ink}" stroke-width="6"/>`).join(""),
        `<rect x="31" y="22" width="82" height="59" fill="none" stroke="${ink}"/>${tx(46,47,"LOX",19,ink,"mono")}${tx(39,66,"TANK / 84",9,ink,"mono")}`,
        `${stripe(32,22,26,16)}${constellation(88,53,27)}`,
        `<circle cx="72" cy="52" r="9" fill="${red}"/><circle cx="72" cy="52" r="17" fill="none" stroke="${red}" stroke-width=".7"/>`,
        `<path d="M27 29l36 24-21 19 37 19M91 22l-8 32 21 22" stroke="#a5a292" fill="none"/>${tx(34,65,"别用",19,ink,"cn",`transform="rotate(-12 50 60)"`)}`
      ];
      body=bg("paper")+tx(74,69,"NASA PUNK / STANDARDS / 04",10,ink,"mono")+
        tx(72,161,"NASA 朋克",74,ink,"",`font-weight="800"`)+tx(76,202,"NASA-PUNK",21,red,"",`font-weight="800"`)+
        tx(630,131,"70 年代航天的功能美学",22,ink,"cn")+tx(630,168,"+ 复古彩条、磨损和标签",22,ink,"cn")+
        names.map((n,i)=>group(`card${i}`,`<g transform="translate(${75+i*165} 271)"><rect width="153" height="226" fill="#f6f3e8" stroke="#8e9081"/>
        <rect x="0" y="0" width="23" height="19" fill="${ink}"/>${tx(5,13,String(i+1).padStart(2,"0"),9,paper,"mono")}
        <g transform="translate(4 31)">${symbols[i]}</g>${tx(13,177,n,20,ink,"cn",`font-weight="700"`)}${tx(13,204,english[i],9,ink,"mono")}</g>`,true)).join("")+
        group("foot",`${stripe(77,555,62,8)}${tx(160,579,"把感觉说清楚，把规则带走。",25,ink,"cn",`font-weight="700"`)}${tx(162,609,"STYLE VOCABULARY / TO DESIGNERS & AI",10,ink,"mono")}`,true);
      motion=`${names.map((_,i)=>`R('card${i}',A.card+${i*.35});`).join("")}R('foot',A.vocabulary);`;
      actions=["card：七个视觉层依次进入，图标、名称、英文标签各自固定位置。","vocabulary：彩条连接到风格词汇的用途；七层结束后保持全卡可读。"];
    }
    if(chapter.id==="closing"){
      body=bg()+group("cover",`<g class="paper-shadow">${img("paper-texture",215,115,850,487)}${tx(263,237,"NASA-PUNK",77,ink,"",`font-weight="800"`)}
      ${tx(266,267,"STANDARDS MANUAL / STYLE VOCABULARY · EP.04",9,ink,"mono")}
      <circle cx="971" cy="188" r="9" fill="${red}"/>${stripe(215,408,850,9)}${worm(266,503,134)}${tx(956,571,"1975 / NOW",8,ink,"mono")}</g>`);
      motion=`tl.fromTo(q('cover'),{scale:1.52,svgOrigin:'640 350'},{scale:1,svgOrigin:'640 350',duration:4,ease:'power2.inOut'},.1);`;
      actions=["cover：封面回到整体，保留字标几何与四道身份彩条，镜头停稳至旁白结束。"];
    }
    if(chapter.id==="credits"){
      body=bg()+group("credit",`${worm(572,203,136,paper)}${tx(489,307,"NASA 朋克 · 代码重建",25,paper,"cn",`font-weight="700"`)}
      ${tx(385,361,"画面代码 / 旁白重写合成 / 程序配乐",19,"#d4d0bf","cn")}
      ${tx(341,407,"镜头参考：路北路陈 · 设计风格小课 04",19,"#d4d0bf","cn")}
      ${tx(345,454,"NASA / Bethesda / 鹰角网络 / Embark Studios",19,"#bdb9a9","cn")}
      ${tx(407,501,"素材来源与重建说明见项目 README",19,"#bdb9a9","cn")}`);
      motion=`tl.fromTo(q('credit'),{opacity:0},{opacity:1,duration:.8},.1);tl.to(q('credit'),{opacity:0,duration:1.1},${Math.max(2,chapter.duration-1.25)});`;
      actions=["credit：标注参考创作者、独立重建方式和示例素材权利方；结尾淡出。"];
    }
    if(!body) throw new Error(`No scene authored for ${chapter.id}`);
    body+=`<g data-layout-ignore>${tx(24,702,"NASA-PUNK / CODE STUDY",7,"#888779","mono")}${tx(1016,702,"04 / "+chapter.title,7,"#888779","mono")}</g>`;
    scenes.push({id,chapter,body,motion,actions});
  }
  return scenes;
}
