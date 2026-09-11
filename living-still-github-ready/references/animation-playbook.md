# 动画元素手册 Animation Playbook

核心原则有两条，按优先级：

1. **自然而然**：动效必须是该场景里自然界/现实中本来就随时在发生的现象——风、重力、热量、光线驱动的那些（落叶纷飞、水面涟漪、蒸汽升腾、火苗跳动、灯光明灭、风吹毛发、云在天上飘）。优先选这个场景最有代表性的自然现象：秋天的树就是落叶，水面就是涟漪，热饮就是蒸汽。**禁止**拟人化、机械感、需要人为解释的动作（"点头""鞠躬""挥手"这类），那不是自然发生的事。
2. **符合常理，因果一致**：选直接可见的"因"，不选派生的"果"。云在天上飘是人眼看到的因，地上影子动是果——只动影子而云不动，就违反常理。同理：只动炊烟上方的光影而不动炊烟、只动水面反光而不动水，都不行。影子/反光要动，前提是其源头也在动。
3. **原地微动**：一动带活全图，其余画面纹丝不动；元素不改大小、不出画。两类合法的例外：(a) 小规模自然飘移的微粒元素——落叶、雪花、蒸汽、火星、花瓣会离开原位短距离飘动；(b) 天空区域的慢速元素——云、炊烟、雾可以在天空区域缓慢漂移变形（幅度小、速度慢），这是云天然的运动方式，不受"面积过大淘汰"限制，但地面场景必须纹丝不动。

## 候选元素规则

合格：
- 运动来自自然力（风、重力、热、光），是该场景自然而然会发生的现象
- 位置大体固定（火焰在灶眼上、窗帘在窗边），或只是微粒的局部自然飘移（落叶、蒸汽、雪）
- 运动是自身形态变化（跳、飘、闪、摆、漾、冒泡、旋落）
- 符合情景逻辑（该场景里它本来就在动）

淘汰：
- 拟人化/机械感动作（枝条"点头"、物体"鞠躬"——不是自然现象）
- 只动"果"不动"因"（影子/反光动而源头不动——违反常理）
- 人脸、眼睛、表情（帧间漂移会恐怖谷）
- 需要大幅位移的元素（走路的人、行驶的车、飞鸟）
- 画面主主体的大动作（弹吉他的人挥手——会抢戏且易穿帮）
- 面积过大（整面墙、整片地面）或过小（看不清动效）的元素；但天空区域的云/炊烟/雾气除外，它们可以整体缓慢漂移

## 场景速查表

| 场景 | 首选候选 |
|---|---|
| 厨房 | 煤气灶火苗、锅里蒸汽、水壶嘴蒸汽、水龙头滴水、窗帘、挂钟摆锤 |
| 咖啡/餐桌 | 咖啡热气、蜡烛火苗、吊灯微晃、杯里气泡、窗外树影 |
| 街道/城市 | 红绿灯切换、霓虹灯闪烁、旗帜飘、晾衣绳衣服摆、屋檐雨滴 |
| 自然/户外 | 篝火、水面涟漪、草叶摇曳、落叶打转、雪花/雨丝飘落、炊烟、云缓慢漂移 |
| 室内/书房 | 壁炉火焰、台灯闪烁、鱼缸气泡、风扇摇头、猫尾巴尖、窗帘 |
| 商店/招牌 | 招牌灯闪烁、灯串明暗、门口风铃、收银机小票 |

## 三帧运动状态写法（第 4 步提示词里 [该帧的运动状态描述] 用）

按"点燃→高峰→回落"节奏写，英文，具体写形态：

- 火焰：`small flame just ignited, low and round` → `flame leaping tall and lively, flickering tips` → `flame settling lower, gentle sway`
- 蒸汽：`first thin wisp of steam rising` → `steam billowing up in a full curl` → `steam thinning and drifting sideways`
- 灯光闪烁：`light dimmed, faint glow` → `light flaring bright, slight halo` → `light back to soft steady glow`
- 窗帘/旗：`fabric hanging still with a slight lift at the edge` → `fabric billowing inward, mid-sway` → `fabric falling back, gentle settle`
- 涟漪：`water surface calm with first ripple ring` → `ripples spreading wide, concentric rings` → `ripples fading, surface nearly calm`
- 尾巴/植物尖：`tail tip curled low` → `tail tip flicked high` → `tail tip easing back down`
- 落叶/花瓣/雪：`a gentle gust lifts a few golden leaves off the branch, beginning to swirl near the canopy` → `several leaves dancing and tumbling in mid-air at different heights` → `the breeze easing, a couple of leaves still drifting low, settling`

- 云：`the white clouds drift slowly and begin to change shape, edges softening, a few new small wisps forming` → `the clouds have drifted further and reshaped, some clouds stretched and merged, new positions in the sky` → `the clouds settling into their new shapes, drifting gently, nearly still again`

**飘落/打转类元素的循环兼容**：帧描述写成"在空中不同高度翻飞舞动"，不要写成单向匀速下坠——乒乓回放时读起来是随风打转而不像倒放。云的写法同理：强调"漂移+变形"，幅度小，乒乓回放时才像云在自然变化而不是倒带。

其他元素照此仿写：幅度小、三个阶段、只描述该元素。
