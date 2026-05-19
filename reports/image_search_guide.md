# FORGE Scene Image Search Guide

每个场景需要 **2 张参考图**，放到 `dataset/images/{domain}/` 下，命名为 `{scene_id}_1.jpg` 和 `{scene_id}_2.jpg`。

参考图拍的是**主体设备/环境**（不是事故本身），用于 image-to-video 模型的输入锚点。
要求：真实照片、清晰、分辨率 ≥ 1280×720、主体占画面 25–75%、背景不杂乱。

---

## Visual Security 视觉安防 → `dataset/images/visual_security/`

### vsec_s01 — 未报备车辆闯入禁区
**找什么**：工厂/仓库入口道闸、门禁杆、限制区域入口，有车辆或地面标线可见
**命名**：`vsec_s01_1.jpg` / `vsec_s01_2.jpg`
- [搜索1：factory gate boom barrier vehicle](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=factory+gate+boom+barrier+vehicle&type=image)
- [搜索2：warehouse entrance access control barrier](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=warehouse+entrance+access+control+barrier&type=image)
- [搜索3：industrial facility gate security](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=industrial+facility+gate+security+checkpoint&type=image)

### vsec_s02 — 高空作业缺PPE
**找什么**：工人在脚手架/高空作业平台上工作的真实照片，能看到人和高处环境
**命名**：`vsec_s02_1.jpg` / `vsec_s02_2.jpg`
- [搜索1：worker scaffolding construction height](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=worker+scaffolding+construction+height&type=image)
- [搜索2：construction worker elevated platform](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=construction+worker+elevated+platform+industrial&type=image)
- [搜索3：aerial work platform worker](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=aerial+work+platform+worker+height&type=image)

### vsec_s03 — 叉车超速转弯货物滑移
**找什么**：仓库通道内的叉车，叉上有托盘/货物，侧面或斜前方视角
**命名**：`vsec_s03_1.jpg` / `vsec_s03_2.jpg`
- [搜索1：forklift warehouse pallet aisle](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=forklift+warehouse+pallet+aisle&type=image)
- [搜索2：forklift carrying pallet industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=forklift+carrying+pallet+industrial&type=image)
- [搜索3：forklift truck warehouse logistics](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=forklift+truck+warehouse+logistics&type=image)

### vsec_s04 — 吊装载荷靠近人员
**找什么**：厂房内的桥式起重机/行车，带吊钩和载荷，从地面仰视或侧视
**命名**：`vsec_s04_1.jpg` / `vsec_s04_2.jpg`
- [搜索1：overhead bridge crane factory floor](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=overhead+bridge+crane+factory+floor&type=image)
- [搜索2：industrial overhead crane hook load](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=industrial+overhead+crane+hook+load&type=image)
- [搜索3：bridge crane steel mill factory](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=bridge+crane+steel+mill+factory&type=image)

### vsec_s05 — CCTV盲区巡检
**找什么**：安装在天花板/墙壁上的工业监控摄像头，PTZ球机，背景是仓库/厂房
**命名**：`vsec_s05_1.jpg` / `vsec_s05_2.jpg`
- [搜索1：CCTV security camera ceiling warehouse](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=CCTV+security+camera+ceiling+warehouse&type=image)
- [搜索2：PTZ security camera industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=PTZ+security+camera+industrial+building&type=image)
- [搜索3：surveillance camera factory mount](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=surveillance+camera+factory+mount&type=image)

### vsec_s06 — 围栏/护栏破损入侵
**找什么**：工厂/工地的金属网围栏、铁丝网，完整的围栏结构（不需要已破损）
**命名**：`vsec_s06_1.jpg` / `vsec_s06_2.jpg`
- [搜索1：industrial perimeter wire fence factory](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=industrial+perimeter+wire+fence+factory&type=image)
- [搜索2：chain link fence industrial site](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=chain+link+fence+industrial+site+boundary&type=image)
- [搜索3：security fence construction site](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=security+fence+construction+site+metal&type=image)

### vsec_s07 — 危化品装卸区液体泄漏
**找什么**：化工/危化品装卸区、存放化学桶/罐的场地，地面有防渗标线
**命名**：`vsec_s07_1.jpg` / `vsec_s07_2.jpg`
- [搜索1：chemical loading dock drums industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=chemical+loading+dock+drums+industrial&type=image)
- [搜索2：hazardous chemical storage warehouse barrels](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=hazardous+chemical+storage+warehouse+barrels&type=image)
- [搜索3：industrial chemical drums storage facility](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=industrial+chemical+drums+storage+facility&type=image)

### vsec_s08 — 人车混行近失事故
**找什么**：仓库内有叉车行驶通道和行人区域标线，地面有黄色警示线的场景
**命名**：`vsec_s08_1.jpg` / `vsec_s08_2.jpg`
- [搜索1：warehouse forklift pedestrian lane marking](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=warehouse+forklift+pedestrian+lane+floor+marking&type=image)
- [搜索2：forklift pedestrian zone warehouse safety](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=forklift+pedestrian+zone+warehouse+safety&type=image)
- [搜索3：warehouse safety aisle marking yellow line](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=warehouse+safety+aisle+marking+yellow+line&type=image)

### vsec_s09 — 烟雾报警与疏散
**找什么**：工业设备（电控柜、机器）冒烟，或工厂内烟雾探测器/报警系统，室内工业场景
**命名**：`vsec_s09_1.jpg` / `vsec_s09_2.jpg`
- [搜索1：industrial smoke factory machine electrical](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=industrial+smoke+factory+machine+electrical&type=image)
- [搜索2：electrical cabinet switchgear industrial panel](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=electrical+cabinet+switchgear+industrial+panel&type=image)
- [搜索3：factory fire alarm smoke detector industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=factory+fire+alarm+smoke+detector+industrial&type=image)

### vsec_s10 — 传送带防护罩缺失
**找什么**：工厂生产线上的传送带，有防护罩/护栏，侧视或俯视角度
**命名**：`vsec_s10_1.jpg` / `vsec_s10_2.jpg`
- [搜索1：conveyor belt industrial production line factory](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=conveyor+belt+industrial+production+line+factory&type=image)
- [搜索2：conveyor system manufacturing plant](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=conveyor+system+manufacturing+plant&type=image)
- [搜索3：belt conveyor industrial guard cover](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=belt+conveyor+industrial+guard+cover&type=image)

---

## Embodied Robotics 具身机器人 → `dataset/images/embodied_robotics/`

### robo_s01 — 多轴机械臂精密抓取
**找什么**：工业机械臂（6轴）在自动化单元中工作，有夹爪或工具，侧视/斜视
**命名**：`robo_s01_1.jpg` / `robo_s01_2.jpg`
- [搜索1：industrial robot arm automation cell manufacturing](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=industrial+robot+arm+automation+cell+manufacturing&type=image)
- [搜索2：6-axis robotic arm industrial gripper](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=6-axis+robotic+arm+industrial+gripper&type=image)
- [搜索3：robot arm factory automation workpiece](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=robot+arm+factory+automation+workpiece&type=image)

### robo_s02 — 协作机器人与人交接
**找什么**：Cobot（协作机器人）在人旁边工作，能看到机器人和人同框
**命名**：`robo_s02_1.jpg` / `robo_s02_2.jpg`
- [搜索1：collaborative robot cobot human worker](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=collaborative+robot+cobot+human+worker&type=image)
- [搜索2：cobot human collaboration factory](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=cobot+human+collaboration+factory&type=image)
- [搜索3：UR robot human industrial workspace](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=UR+robot+human+industrial+workspace&type=image)

### robo_s03 — 履带机器人废墟越障
**找什么**：履带式地面机器人，在碎石/不平整地面上，军用或搜救机器人均可
**命名**：`robo_s03_1.jpg` / `robo_s03_2.jpg`
- [搜索1：tracked ground robot rubble terrain](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=tracked+ground+robot+rubble+terrain&type=image)
- [搜索2：UGV unmanned ground vehicle crawler](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=UGV+unmanned+ground+vehicle+crawler&type=image)
- [搜索3：rescue robot tracked disaster terrain](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=rescue+robot+tracked+disaster+terrain&type=image)

### robo_s04 — 四足机器人第一视角巡检
**找什么**：四足机器人（Spot类）在工业/建筑环境中行走
**命名**：`robo_s04_1.jpg` / `robo_s04_2.jpg`
- [搜索1：Boston Dynamics Spot robot industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=Boston+Dynamics+Spot+robot+industrial&type=image)
- [搜索2：quadruped legged robot inspection](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=quadruped+legged+robot+inspection+industrial&type=image)
- [搜索3：legged robot four legs walking factory](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=legged+robot+four+legs+walking+factory&type=image)

### robo_s05 — AMR仓储导航
**找什么**：仓库里的自主移动机器人（AMR），在货架间行驶
**命名**：`robo_s05_1.jpg` / `robo_s05_2.jpg`
- [搜索1：autonomous mobile robot warehouse shelves](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=autonomous+mobile+robot+warehouse+shelves&type=image)
- [搜索2：AMR logistics robot warehouse aisle](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=AMR+logistics+robot+warehouse+aisle&type=image)
- [搜索3：mobile robot AGV warehouse logistics](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=mobile+robot+AGV+warehouse+logistics&type=image)

### robo_s06 — 光幕触发紧急制动
**找什么**：机器人单元入口处的安全光幕/激光光栅装置，可以看到发射/接收端
**命名**：`robo_s06_1.jpg` / `robo_s06_2.jpg`
- [搜索1：safety light curtain robot cell industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=safety+light+curtain+robot+cell+industrial&type=image)
- [搜索2：laser safety barrier industrial robot fence](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=laser+safety+barrier+industrial+robot+fence&type=image)
- [搜索3：safety light barrier photoelectric industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=safety+light+barrier+photoelectric+industrial&type=image)

### robo_s07 — 机器人打磨/焊接接触力
**找什么**：机器人手持磨头或焊枪对金属工件进行加工，有火花或接触点可见
**命名**：`robo_s07_1.jpg` / `robo_s07_2.jpg`
- [搜索1：robot welding arm sparks metal industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=robot+welding+arm+sparks+metal+industrial&type=image)
- [搜索2：robotic welding cell manufacturing](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=robotic+welding+cell+manufacturing&type=image)
- [搜索3：robot grinding metal workpiece industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=robot+grinding+metal+workpiece+industrial&type=image)

### robo_s08 — 多机器人协同避让
**找什么**：两台及以上机器人/AMR在同一空间工作的场景
**命名**：`robo_s08_1.jpg` / `robo_s08_2.jpg`
- [搜索1：multiple robots industrial cell cooperation](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=multiple+robots+industrial+cell+cooperation&type=image)
- [搜索2：two robot arms manufacturing automation](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=two+robot+arms+manufacturing+automation&type=image)
- [搜索3：dual robot industrial automation cell](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=dual+robot+industrial+automation+cell&type=image)

### robo_s09 — 管道爬行机器人巡检
**找什么**：管道检测机器人（爬虫机器人），在管道内或入口处，或内窥镜视角
**命名**：`robo_s09_1.jpg` / `robo_s09_2.jpg`
- [搜索1：pipe inspection robot crawler pipeline](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=pipe+inspection+robot+crawler+pipeline&type=image)
- [搜索2：pipeline robot inspection industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=pipeline+robot+inspection+industrial&type=image)
- [搜索3：pig pipeline inspection tool inside](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=pig+pipeline+inspection+tool&type=image)

### robo_s10 — 夹爪局部失效恢复
**找什么**：机器人夹爪（吸盘式或手指式）抓取工件的近距离照片
**命名**：`robo_s10_1.jpg` / `robo_s10_2.jpg`
- [搜索1：robot gripper suction cup industrial picking](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=robot+gripper+suction+cup+industrial+picking&type=image)
- [搜索2：robotic end effector gripper workpiece](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=robotic+end+effector+gripper+workpiece&type=image)
- [搜索3：vacuum gripper robot pick place industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=vacuum+gripper+robot+pick+place+industrial&type=image)

---

## Heavy Load Construction 重型载荷 → `dataset/images/heavy_load_construction/`

### hlc_s01 — 双履带吊协同吊装
**找什么**：履带式起重机，最好是两台在同一画面，吊装钢结构模块
**命名**：`hlc_s01_1.jpg` / `hlc_s01_2.jpg`
- [搜索1：crawler crane tandem lift construction](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=crawler+crane+tandem+lift+construction&type=image)
- [搜索2：lattice boom crawler crane heavy lift](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=lattice+boom+crawler+crane+heavy+lift&type=image)
- [搜索3：two cranes lifting steel structure module](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=two+cranes+lifting+steel+structure+module&type=image)

### hlc_s02 — 钢丝绳过载变形/断裂
**找什么**：钢丝绳/吊索的近景，能看到钢丝绳股的细节，在张紧状态
**命名**：`hlc_s02_1.jpg` / `hlc_s02_2.jpg`
- [搜索1：wire rope sling crane close up](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=wire+rope+sling+crane+close+up&type=image)
- [搜索2：steel wire rope rigging tension industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=steel+wire+rope+rigging+tension+industrial&type=image)
- [搜索3：crane wire rope strands close industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=crane+wire+rope+strands+close+industrial&type=image)

### hlc_s03 — 矿卡泥泞坡道爬坡
**找什么**：大型矿用卡车在泥土/非铺装路面上行驶，能看到轮胎和地面
**命名**：`hlc_s03_1.jpg` / `hlc_s03_2.jpg`
- [搜索1：mining haul truck muddy road open pit](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=mining+haul+truck+muddy+road+open+pit&type=image)
- [搜索2：dump truck mine dirt road slope](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=dump+truck+mine+dirt+road+slope&type=image)
- [搜索3：large mining truck unpaved terrain](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=large+mining+truck+unpaved+terrain&type=image)

### hlc_s04 — 龙门吊强风扰动
**找什么**：港口/工地的龙门吊或集装箱吊，大型钢结构，正面或侧面
**命名**：`hlc_s04_1.jpg` / `hlc_s04_2.jpg`
- [搜索1：gantry crane port terminal container](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=gantry+crane+port+terminal+container&type=image)
- [搜索2：container crane quay port industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=container+crane+quay+port+industrial&type=image)
- [搜索3：ship-to-shore crane port large](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=ship-to-shore+crane+port+large&type=image)

### hlc_s05 — 桥梁节段无人机巡检
**找什么**：桥梁预制节段/箱梁，在预制场或施工现场，能看到截面形状
**命名**：`hlc_s05_1.jpg` / `hlc_s05_2.jpg`
- [搜索1：precast concrete bridge segment girder](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=precast+concrete+bridge+segment+girder&type=image)
- [搜索2：bridge beam precast yard construction](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=bridge+beam+precast+yard+construction&type=image)
- [搜索3：concrete box girder bridge construction](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=concrete+box+girder+bridge+construction&type=image)

### hlc_s06 — 挖掘机多连杆装载
**找什么**：挖掘机侧面全貌，动臂/斗杆/铲斗清晰可见，在施工现场
**命名**：`hlc_s06_1.jpg` / `hlc_s06_2.jpg`
- [搜索1：excavator boom arm bucket construction](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=excavator+boom+arm+bucket+construction&type=image)
- [搜索2：hydraulic excavator digging construction site](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=hydraulic+excavator+digging+construction+site&type=image)
- [搜索3：excavator earthmoving soil bucket](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=excavator+earthmoving+soil+bucket&type=image)

### hlc_s07 — 吊车支腿地基沉陷
**找什么**：移动式起重机的支腿/垫板撑地的近景，地面接触部分清晰
**命名**：`hlc_s07_1.jpg` / `hlc_s07_2.jpg`
- [搜索1：mobile crane outrigger pad ground](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=mobile+crane+outrigger+pad+ground&type=image)
- [搜索2：crane stabilizer outrigger construction soil](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=crane+stabilizer+outrigger+construction+soil&type=image)
- [搜索3：telescopic crane outrigger extended ground](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=telescopic+crane+outrigger+extended+ground&type=image)

### hlc_s08 — 地下管线破裂泥水喷涌
**找什么**：施工开挖的沟槽，里面有暴露的地下管道，沟槽壁和管道清晰可见
**命名**：`hlc_s08_1.jpg` / `hlc_s08_2.jpg`
- [搜索1：excavation trench underground pipe construction](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=excavation+trench+underground+pipe+construction&type=image)
- [搜索2：trench pipe underground utility construction](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=trench+pipe+underground+utility+construction&type=image)
- [搜索3：open trench pipeline urban construction](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=open+trench+pipeline+urban+construction&type=image)

### hlc_s09 — 吊物接近结构紧急停止
**找什么**：起重机吊物在脚手架或钢结构附近的场景，显示距离感
**命名**：`hlc_s09_1.jpg` / `hlc_s09_2.jpg`
- [搜索1：crane load near scaffolding construction](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=crane+load+near+scaffolding+construction&type=image)
- [搜索2：crane lifting steel frame near structure](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=crane+lifting+steel+frame+near+structure&type=image)
- [搜索3：suspended load crane construction building](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=suspended+load+crane+construction+building&type=image)

### hlc_s10 — 模板/脚手架局部坍塌
**找什么**：建筑工地的脚手架或模板支撑结构，能看到杆件连接和整体结构
**命名**：`hlc_s10_1.jpg` / `hlc_s10_2.jpg`
- [搜索1：scaffolding construction building temporary structure](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=scaffolding+construction+building+temporary+structure&type=image)
- [搜索2：formwork shoring construction concrete](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=formwork+shoring+construction+concrete&type=image)
- [搜索3：scaffold tube fitting construction site](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=scaffold+tube+fitting+construction+site&type=image)

---

## Precision Defect Gen 精密制造 → `dataset/images/precision_defect_gen/`

### pdg_s01 — PCB焊锡桥短路
**找什么**：PCB板近景，能看到密集焊点、走线，SMD元件，显微或微距
**命名**：`pdg_s01_1.jpg` / `pdg_s01_2.jpg`
- [搜索1：PCB circuit board close up solder joints macro](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=PCB+circuit+board+close+up+solder+joints+macro&type=image)
- [搜索2：printed circuit board SMD components close](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=printed+circuit+board+SMD+components+close&type=image)
- [搜索3：circuit board traces solder macro](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=circuit+board+traces+solder+macro&type=image)

### pdg_s02 — 发动机/管道内窥裂纹
**找什么**：工业内窥镜/孔探镜拍摄的发动机叶片或管道内壁，圆形视野
**命名**：`pdg_s02_1.jpg` / `pdg_s02_2.jpg`
- [搜索1：borescope inspection turbine blade engine](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=borescope+inspection+turbine+blade+engine&type=image)
- [搜索2：endoscope inspection engine inside industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=endoscope+inspection+engine+inside+industrial&type=image)
- [搜索3：turbine blade inspection internal engine](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=turbine+blade+inspection+internal+engine&type=image)

### pdg_s03 — 齿轮缺齿/严重磨损
**找什么**：工业齿轮近景，齿廓清晰，能数清齿数
**命名**：`pdg_s03_1.jpg` / `pdg_s03_2.jpg`
- [搜索1：industrial gear teeth close up macro](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=industrial+gear+teeth+close+up+macro&type=image)
- [搜索2：mechanical gear close up industrial metal](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=mechanical+gear+close+up+industrial+metal&type=image)
- [搜索3：gearbox gear teeth industrial inspection](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=gearbox+gear+teeth+industrial+inspection&type=image)

### pdg_s04 — 五轴CNC曲面切削
**找什么**：五轴CNC加工中心，能看到主轴/刀具和工件，最好有切削状态
**命名**：`pdg_s04_1.jpg` / `pdg_s04_2.jpg`
- [搜索1：5-axis CNC machining center complex surface](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=5-axis+CNC+machining+center+complex+surface&type=image)
- [搜索2：CNC milling machine 5 axis industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=CNC+milling+machine+5+axis+industrial&type=image)
- [搜索3：five axis machining center tool workpiece metal](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=five+axis+machining+center+tool+workpiece+metal&type=image)

### pdg_s05 — 切削液喷溅
**找什么**：CNC切削过程中冷却液喷射的画面，有液体飞溅和切屑
**命名**：`pdg_s05_1.jpg` / `pdg_s05_2.jpg`
- [搜索1：CNC cutting coolant spray chips machining](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=CNC+cutting+coolant+spray+chips+machining&type=image)
- [搜索2：metal cutting coolant splash industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=metal+cutting+coolant+splash+industrial&type=image)
- [搜索3：machining coolant chip ejection CNC](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=machining+coolant+chip+ejection+CNC&type=image)

### pdg_s06 — 焊缝气孔/裂纹
**找什么**：金属结构焊缝的近景，能看到焊道纹路和热影响区
**命名**：`pdg_s06_1.jpg` / `pdg_s06_2.jpg`
- [搜索1：weld seam bead close up metal industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=weld+seam+bead+close+up+metal+industrial&type=image)
- [搜索2：welding bead steel close inspection](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=welding+bead+steel+close+inspection&type=image)
- [搜索3：metal weld joint inspection quality](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=metal+weld+joint+inspection+quality&type=image)

### pdg_s07 — 精密表面划痕
**找什么**：抛光金属表面/轴承面/晶圆，光洁有反光，极近距离
**命名**：`pdg_s07_1.jpg` / `pdg_s07_2.jpg`
- [搜索1：polished metal surface close up macro](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=polished+metal+surface+close+up+macro&type=image)
- [搜索2：bearing race polished surface inspection](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=bearing+race+polished+surface+inspection&type=image)
- [搜索3：precision machined metal surface close](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=precision+machined+metal+surface+close&type=image)

### pdg_s08 — 管束内窥巡检
**找什么**：换热器管束端面，能看到密集排列的圆管开口
**命名**：`pdg_s08_1.jpg` / `pdg_s08_2.jpg`
- [搜索1：heat exchanger tube bundle end face industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=heat+exchanger+tube+bundle+end+face+industrial&type=image)
- [搜索2：shell tube heat exchanger tube sheet](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=shell+tube+heat+exchanger+tube+sheet&type=image)
- [搜索3：tube bundle heat exchanger inspection industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=tube+bundle+heat+exchanger+inspection+industrial&type=image)

### pdg_s09 — 连接器针脚弯曲/桥接
**找什么**：高密度电气连接器，密集针脚，近距离微距照片
**命名**：`pdg_s09_1.jpg` / `pdg_s09_2.jpg`
- [搜索1：electrical connector pins dense macro close](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=electrical+connector+pins+dense+macro+close&type=image)
- [搜索2：IC connector terminal pins fine pitch](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=IC+connector+terminal+pins+fine+pitch&type=image)
- [搜索3：high density connector electronic pins close](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=high+density+connector+electronic+pins+close&type=image)

### pdg_s10 — 精密装配轻微错位
**找什么**：轴承/轴/联轴器装配的近景，能看到配合面
**命名**：`pdg_s10_1.jpg` / `pdg_s10_2.jpg`
- [搜索1：bearing shaft assembly precision industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=bearing+shaft+assembly+precision+industrial&type=image)
- [搜索2：precision coupling shaft bearing close](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=precision+coupling+shaft+bearing+close&type=image)
- [搜索3：ball bearing assembly industrial machine](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=ball+bearing+assembly+industrial+machine&type=image)

---

## Extreme Emergency 极端工况 → `dataset/images/extreme_emergency/`

### eem_s01 — 法兰高压泄漏
**找什么**：工业管道法兰（螺栓连接），能清晰看到法兰盘和螺栓，加压管道
**命名**：`eem_s01_1.jpg` / `eem_s01_2.jpg`
- [搜索1：industrial pipe flange bolts high pressure](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=industrial+pipe+flange+bolts+high+pressure&type=image)
- [搜索2：pipeline flange connection bolted industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=pipeline+flange+connection+bolted+industrial&type=image)
- [搜索3：pressure pipe flange joint industrial steel](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=pressure+pipe+flange+joint+industrial+steel&type=image)

### eem_s02 — 储罐区闪燃蔓延
**找什么**：化工厂/油库的储罐区，能看到多个大型储罐和管廊
**命名**：`eem_s02_1.jpg` / `eem_s02_2.jpg`
- [搜索1：oil storage tank farm chemical plant industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=oil+storage+tank+farm+chemical+plant+industrial&type=image)
- [搜索2：petroleum storage tanks refinery industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=petroleum+storage+tanks+refinery+industrial&type=image)
- [搜索3：chemical plant storage tank farm pipeline](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=chemical+plant+storage+tank+farm+pipeline&type=image)

### eem_s03 — 输电铁塔覆冰垮塌
**找什么**：高压输电铁塔，最好有覆冰或冬季场景，桁架结构清晰
**命名**：`eem_s03_1.jpg` / `eem_s03_2.jpg`
- [搜索1：transmission tower ice winter power line](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=transmission+tower+ice+winter+power+line&type=image)
- [搜索2：electricity pylon ice storm winter](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=electricity+pylon+ice+storm+winter&type=image)
- [搜索3：high voltage tower lattice structure winter](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=high+voltage+tower+lattice+structure+winter&type=image)

### eem_s04 — 粉尘爆炸与应急响应
**找什么**：粮仓/面粉厂/工业粉尘收集装置，能看到筒仓或粉尘处理设备
**命名**：`eem_s04_1.jpg` / `eem_s04_2.jpg`
- [搜索1：grain silo elevator industrial dust](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=grain+silo+elevator+industrial+dust&type=image)
- [搜索2：flour mill grain elevator silos](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=flour+mill+grain+elevator+silos&type=image)
- [搜索3：industrial dust collector factory pneumatic](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=industrial+dust+collector+factory+pneumatic&type=image)

### eem_s05 — 反应釜超压泄放
**找什么**：化工反应釜/压力容器，带安全阀或泄压口，能看到釜体和管口
**命名**：`eem_s05_1.jpg` / `eem_s05_2.jpg`
- [搜索1：chemical reactor vessel pressure relief valve industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=chemical+reactor+vessel+pressure+relief+valve+industrial&type=image)
- [搜索2：pressure vessel reactor chemical plant](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=pressure+vessel+reactor+chemical+plant&type=image)
- [搜索3：autoclave reactor industrial chemical](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=autoclave+reactor+industrial+chemical&type=image)

### eem_s06 — 电池热失控
**找什么**：储能系统电池柜/电池模组机架，能看到模组排列结构
**命名**：`eem_s06_1.jpg` / `eem_s06_2.jpg`
- [搜索1：battery energy storage system cabinet rack](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=battery+energy+storage+system+cabinet+rack&type=image)
- [搜索2：lithium battery energy storage industrial cabinet](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=lithium+battery+energy+storage+industrial+cabinet&type=image)
- [搜索3：ESS battery rack module industrial](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=ESS+battery+rack+module+industrial&type=image)

### eem_s07 — 隧道火灾烟气分层
**找什么**：公路或铁路隧道内部，能看到顶板、侧墙、照明和通风设施
**命名**：`eem_s07_1.jpg` / `eem_s07_2.jpg`
- [搜索1：road tunnel interior lighting ventilation](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=road+tunnel+interior+lighting+ventilation&type=image)
- [搜索2：highway tunnel inside concrete ceiling](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=highway+tunnel+inside+concrete+ceiling&type=image)
- [搜索3：underground tunnel interior emergency light](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=underground+tunnel+interior+emergency+light&type=image)

### eem_s08 — 吊载坠落应急撤离
**找什么**：起重机带载荷在施工现场或工厂，从地面仰视，能看到吊物和下方工作区
**命名**：`eem_s08_1.jpg` / `eem_s08_2.jpg`
- [搜索1：crane suspended load construction workers area](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=crane+suspended+load+construction+workers+area&type=image)
- [搜索2：overhead crane load industrial factory floor](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=overhead+crane+load+industrial+factory+floor&type=image)
- [搜索3：crane hoist heavy load construction site](https://commons.wikimedia.org/wiki/Special:MediaSearch?search=crane+hoist+heavy+load+construction+site&type=image)

---

## 下载后的操作

图片下载好后，把文件路径告诉我，我会：
1. 更新 `reports/scene_prompts.json`（已有的 prompt 和标题）
2. 生成最终的 samples 映射

图片命名必须严格按照 `{scene_id}_1.jpg` / `{scene_id}_2.jpg` 格式。
