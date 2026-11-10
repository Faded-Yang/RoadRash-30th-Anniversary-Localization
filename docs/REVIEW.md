# 五语逐条审校记录

简体中文不是"翻完就算"——游戏官方在同一套字符串 ID（0–4003，1372 条）上出了
**德语 / 法语 / 西班牙语 / 意大利语**四个本地化版本，它们与英文版**逐 id 对齐**。
这是判断每条英文原文"到底什么意思"的最权威依据（尤其是俚语、双关、反讽）。

审校方法：把「英文原文 + 四语官方译文 + 当前中文」并排对照，凡四语一致而中文偏离的，即以四语为准修正。

## 被四语当场证伪的误译

| id | 英文原文 | 原译 | 四语证据 | 修正 |
|---|---|---|---|---|
| 25 | sheer cliff walls | 笔直崖壁 | FR *falaises abruptes* / DE *steiler Küstenklippen*（陡峭） | 陡峭崖壁 |
| 43 | An ex-con with a death wish | 想死的**惯犯** | FR *ancien escroc* / ES *ex convicto* | 蹲过大牢的亡命徒 |
| 145 | this pussycat | **娘炮车**（原文无侮辱） | ES *esta gatita*（小母猫） | 这只小猫 |
| 153 | HANDLING: Fidgety | 手痒 | DE *zappelig* / ES *Titubeante* | 躁动 |
| 153 | slickest | 滑溜 | DE *raffiniertesten* / FR *la plus classe* | 最靓 |
| 156 | ACCELERATION: Stomping | 跺脚 | DE *stampfend* / ES *Brusca* | 碾压 |
| 152 | Hair-raising | 竖毛（直译不通） | ES *escalofriante* | 吓破胆 |
| 575 | you ain't no fly boy | 飞行员 | DE *kein Rennfahrer* / ES *no eres un tío bueno* | 飞车好手 |
| 589 | fire up the spit | 生火架烤叉 | 四语均为烤肉架/烤叉 | 想支起烤叉 |
| 663 | even up the score | 才敢掰手腕 | 四语=扯平/平手 | 才算平手 |
| 674 | swing wide on a corner | 弯里外放油门 | 四语=走外线 | 弯道走外线 |
| 871 | make an example of you | 做个榜样 | ES/IT=以儆效尤 | 杀鸡儆猴 |
| 656 | that turns me on | 正合我意 | DE *macht mich an* / FR *me botte*（性奋） | 让我来劲 |
| 716 | You're the **dopest** rider | 最带劲 | DE *dämlichste* / FR *la pire des nouilles* / ES *más colgado* / IT *più bifolco* —— **四语一致为贬义** | 骑得最烂 |
| 917/924 | as crude a rider | 最粗的骑手 | DE=车技差 / FR *le plus naze* | 骑得最糙 |

## 一致性口径（审校中确立）

1. **行首颜色码只在 id ≥ 1000 存在**（`Y`/`G`/`O`/`-`，制作名单与结局旁白）。
   id < 1000 里以 Y/G/O 开头的是正文词首（`Go Home`、`GAME LOADING`、`Yes`、`You...`），
   跨 5 语言首字母不一致即可证明，**补前缀会把首字母当颜色码吃掉**。
2. **角色短名一律英文**（Axle / Bose / Cydney / Jon / Pearl / Rhonda / Jim / Mike）：
   它们参与人物立绘路径 `Chars/%s-F`，翻译会掉图；官方四语版也全部保留英文。
   对白中同理，否则与成绩榜显示不一致。
3. **车型号保留英文原名**（Banzai / Corsair / Kamikaze / Perro / Killer Rat / Diablo / Stiletto / DMG / …），
   官方 DE/FR/IT 基本都保留；只翻车种类名（老鼠车 / 运动车 / 超级车）。
4. **制作名单整段保留英文**（乐队名、曲名、人名、厂牌、ASCAP/BMI、`(P)` 年份行）；
   只翻章节小标题与职位名（`-Director:\tRod Gross` → `-导演:\tRod Gross`）。

## 其他修正（机翻腔 / 读不通）

`221 输几句狠话→敲几句狠话`、`412 有空的 %s 游戏→可用`、`144 这台"运动"→这台"运动车"`、
`51 a killer sports bike 能杀人→要命`、`151 平衡得好得没话说→平衡得无可挑剔`、
`523 多余的粗暴是要罚重款→无故撒野我可要收重罚的`、`548 可松不得劲→一点都不能松劲` 等约 30 处。

## 统计

- 1372 条：**983 条译成中文（71.6%）**，389 条按规则保留英文（制作名单主体 + 短名 + 乐队曲名 + 版权行）。
- 英文 58025 字符 → 中文 22305 字符（省 62%，排版比英文更宽松）。
