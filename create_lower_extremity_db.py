#!/usr/bin/env python3
"""Generate a bilingual lower extremity injuries quiz bank from CSI3131 Module 2."""

import sqlite3, os

DB_PATH = os.path.join(os.path.dirname(__file__), "lower_extremity_injuries.db")

SCHEMA = """
CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT, type TEXT NOT NULL, topic TEXT,
    difficulty TEXT, question_zh TEXT NOT NULL, question_en TEXT,
    image_path TEXT, explanation_zh TEXT, explanation_en TEXT
);
CREATE TABLE IF NOT EXISTS options (
    id INTEGER PRIMARY KEY AUTOINCREMENT, question_id INTEGER NOT NULL REFERENCES questions(id),
    label TEXT NOT NULL, text_zh TEXT NOT NULL, text_en TEXT,
    is_correct INTEGER NOT NULL DEFAULT 0, explanation_zh TEXT, explanation_en TEXT,
    sort_order INTEGER NOT NULL DEFAULT 0
);
"""

META = {
    "title": "下肢损伤 (Lower Extremity Injuries)",
    "description": "CSI3131 Module 2 - 踝、膝、髋部损伤类型、机制、临床特征、特殊检查、风险因素、解剖结构和康复指南",
    "author": "QuizForge (from Prof. Cournoyer's lecture)",
    "version": "2.0",
}

QUESTIONS = [
    # ═══════════════════════════════════════════════════════════
    # TOPIC: Ankle & Lower Leg
    # ═══════════════════════════════════════════════════════════
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "easy",
        "question_zh": "最常见的运动损伤是什么？",
        "question_en": "What is the MOST common sport injury?",
        "explanation_zh": "踝关节外侧扭伤（Lateral ankle sprain）是运动中最常见的损伤，由强力内翻（inversion）引起。",
        "explanation_en": "Lateral ankle sprains are the single most common injury in sport, caused by forceful inversion.",
        "options": [
            ("A", "前交叉韧带撕裂（ACL tear）", "ACL tear", False, None, None),
            ("B", "踝关节外侧扭伤（Lateral ankle sprain）", "Lateral ankle sprain", True,
             "这是最常见的运动损伤", "This is the most common sport injury overall"),
            ("C", "腘绳肌拉伤（Hamstring strain）", "Hamstring strain", False, None, None),
            ("D", "脑震荡（Concussion）", "Concussion", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "easy",
        "question_zh": "踝关节外侧扭伤（Lateral ankle sprain）的受伤机制（MOI）是什么？",
        "question_en": "What is the mechanism of injury (MOI) for a lateral ankle sprain?",
        "explanation_zh": "踝关节外侧扭伤是由踝关节强力内翻（inversion）引起，拉伸外侧韧带。",
        "explanation_en": "Lateral ankle sprains result from forceful inversion of the ankle, stretching the lateral ligaments.",
        "options": [
            ("A", "强力外翻（Forceful eversion）", "Forceful eversion", False,
             "外翻会损伤内侧（三角）韧带（deltoid ligament）", "Eversion would injure the medial (deltoid) ligament"),
            ("B", "强力内翻（Forceful inversion）", "Forceful inversion", True, None, None),
            ("C", "背屈加外翻（Dorsiflexion and eversion）", "Dorsiflexion and eversion", False,
             "此机制导致下胫腓联合扭伤（syndesmosis/high ankle sprain）", "This MOI causes a syndesmosis (high ankle) sprain"),
            ("D", "轴向压缩（Axial compression）", "Axial compression", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "下胫腓联合扭伤（Syndesmosis/high ankle sprain）的受伤机制（MOI）是什么？",
        "question_en": "What is the MOI for a syndesmosis (high ankle) sprain?",
        "explanation_zh": "下胫腓联合扭伤涉及远端胫腓联合（distal tibiofibular syndesmosis），由背屈（dorsiflexion）和外翻（eversion）的组合力引起。",
        "explanation_en": "A syndesmosis sprain involves the distal tibiofibular syndesmosis and is caused by combined dorsiflexion and eversion.",
        "options": [
            ("A", "强力内翻（Forceful inversion）", "Forceful inversion", False,
             "这会导致踝关节外侧扭伤", "This causes a lateral ankle sprain"),
            ("B", "跖屈加内翻（Plantar flexion and inversion）", "Plantar flexion and inversion", False, None, None),
            ("C", "背屈加外翻（Dorsiflexion and eversion）", "Dorsiflexion and eversion", True, None, None),
            ("D", "单纯强力外翻（Forceful eversion only）", "Forceful eversion only", False,
             "单纯外翻导致内侧踝扭伤", "Pure eversion causes a medial ankle sprain"),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "踝关节内侧扭伤（Medial ankle sprain）的受伤机制（MOI）是什么？",
        "question_en": "What is the MOI for a medial ankle sprain?",
        "explanation_zh": "踝关节内侧扭伤涉及三角韧带复合体（deltoid ligament complex），由强力外翻（eversion）引起。",
        "explanation_en": "Medial ankle sprains involve the deltoid ligament complex and result from forceful eversion.",
        "options": [
            ("A", "强力内翻（Forceful inversion）", "Forceful inversion", False, None, None),
            ("B", "强力外翻（Forceful eversion）", "Forceful eversion", True, None, None),
            ("C", "背屈加外翻（Dorsiflexion and eversion）", "Dorsiflexion and eversion", False,
             "此机制针对下胫腓联合（syndesmosis）", "This MOI targets the syndesmosis"),
            ("D", "跖屈（Plantar flexion）", "Plantar flexion", False, None, None),
        ],
    },
    {
        "type": "multiple", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "踝关节外侧扭伤涉及哪些韧带？（选择所有正确答案）",
        "question_en": "Which ligaments are involved in a lateral ankle sprain? (Select all that apply)",
        "explanation_zh": "踝关节外侧韧带复合体由跟腓韧带（CFL）、距腓前韧带（ATFL）和距腓后韧带（PTFL）组成。",
        "explanation_en": "The lateral ankle ligament complex consists of the calcaneofibular (CFL), anterior talofibular (ATFL), and posterior talofibular (PTFL) ligaments.",
        "options": [
            ("A", "跟腓韧带（Calcaneofibular ligament, CFL）", "Calcaneofibular ligament (CFL)", True, None, None),
            ("B", "距腓前韧带（Anterior talofibular ligament, ATFL）", "Anterior talofibular ligament (ATFL)", True, None, None),
            ("C", "三角韧带（Deltoid ligament）", "Deltoid ligament", False,
             "三角韧带位于内侧", "The deltoid ligament is on the medial side"),
            ("D", "距腓后韧带（Posterior talofibular ligament, PTFL）", "Posterior talofibular ligament (PTFL)", True, None, None),
        ],
    },
    {
        "type": "multiple", "topic": "Ankle & Lower Leg", "difficulty": "hard",
        "question_zh": "三角韧带复合体（Deltoid ligament complex）由哪些结构组成？（选择所有正确答案）",
        "question_en": "Which structures make up the deltoid ligament complex? (Select all that apply)",
        "explanation_zh": "三角韧带由四个部分组成：胫距前韧带（anterior tibiotalar）、胫距后韧带（posterior tibiotalar）、胫跟韧带（tibiocalcanean）和胫舟韧带（tibionavicular）。",
        "explanation_en": "The deltoid ligament has four components: anterior tibiotalar, posterior tibiotalar, tibiocalcanean, and tibionavicular ligaments.",
        "options": [
            ("A", "胫距前韧带（Anterior tibiotalar）", "Anterior tibiotalar", True, None, None),
            ("B", "胫距后韧带（Posterior tibiotalar）", "Posterior tibiotalar", True, None, None),
            ("C", "胫跟韧带（Tibiocalcanean）", "Tibiocalcanean", True, None, None),
            ("D", "跟腓韧带（Calcaneofibular）", "Calcaneofibular", False,
             "这是外侧韧带", "This is a lateral ligament"),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "easy",
        "question_zh": "足底筋膜炎（Plantar fasciitis）的标志性症状是什么？",
        "question_en": "What is the hallmark symptom of plantar fasciitis?",
        "explanation_zh": "足底筋膜炎的典型表现为晨起第一步时疼痛（first step pain），位于内侧足跟或足底。",
        "explanation_en": "Plantar fasciitis classically presents with pain at the first step in the morning, located on the medial heel or underside of the foot.",
        "options": [
            ("A", "晨起第一步时疼痛（Pain at first step in the morning）", "Pain at first step in the morning", True, None, None),
            ("B", "足跟夜间痛", "Night pain in the heel", False, None, None),
            ("C", "足背肿胀", "Swelling of the dorsum of the foot", False, None, None),
            ("D", "脚趾麻木", "Numbness in the toes", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "一名运动员报告听到'砰'的一声、可见肌腱缺损，感觉像被'枪击中了腿'。最可能的损伤是什么？",
        "question_en": "An athlete reports hearing a 'pop', sees a visible defect in the tendon, and feels like being 'shot in the leg.' What is the most likely injury?",
        "explanation_zh": "跟腱断裂（Achilles tendon rupture）表现为可闻及的弹响、可见肌腱缺损、无法跖屈或踮脚走路、感觉像被枪击中腿部。",
        "explanation_en": "Achilles tendon rupture presents with an audible pop, visible tendon defect, inability to plantar flex or walk on toes, and feeling of being shot in the leg.",
        "options": [
            ("A", "腓肠肌拉伤（Gastrocnemius strain）", "Gastrocnemius strain", False, None, None),
            ("B", "跟腱断裂（Achilles tendon rupture）", "Achilles tendon rupture", True, None, None),
            ("C", "踝关节外侧扭伤（Lateral ankle sprain）", "Lateral ankle sprain", False, None, None),
            ("D", "胫骨应力性骨折（Tibial stress fracture）", "Tibial stress fracture", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "一名跑步者出现胫骨内侧疼痛，跑步时加重。触诊发现胫骨内侧比目鱼肌止点处有触发点（trigger points）。最可能的诊断是什么？",
        "question_en": "A runner presents with pain on the medial side of the tibia that increases with running. Palpation reveals trigger points at the soleus insertion on the medial tibia. What is the most likely diagnosis?",
        "explanation_zh": "胫骨内侧应力综合征（MTSS，即胫骨骨膜炎/shin splints）涉及胫骨内侧比目鱼肌（soleus）止点处骨膜的炎症。",
        "explanation_en": "MTSS (shin splints) involves inflammation of the periosteum along the soleus insertion on the medial tibia.",
        "options": [
            ("A", "胫骨应力性骨折（Tibial stress fracture）", "Tibial stress fracture", False,
             "应力性骨折表现为点状压痛（point tenderness），而非弥漫性/触发点疼痛",
             "Stress fractures show point tenderness, not diffuse/trigger point pain"),
            ("B", "胫骨内侧应力综合征（Medial tibial stress syndrome, MTSS）", "Medial tibial stress syndrome (MTSS)", True, None, None),
            ("C", "骨筋膜室综合征（Compartment syndrome）", "Compartment syndrome", False, None, None),
            ("D", "踝关节内侧扭伤（Medial ankle sprain）", "Medial ankle sprain", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "hard",
        "question_zh": "哪个特征最能区分应力性骨折（Stress fracture）和胫骨内侧应力综合征（MTSS）？",
        "question_en": "Which feature best differentiates a stress fracture from MTSS?",
        "explanation_zh": "MTSS 的疼痛是弥漫性的（diffuse），休息后减轻或消失；应力性骨折的疼痛深沉、持续，即使在休息时也存在（包括夜间痛）。",
        "explanation_en": "MTSS pain is diffuse and decreases with rest, while stress fracture pain is deep, nagging, and present even at rest (including night pain).",
        "options": [
            ("A", "活动时疼痛加重", "Pain increases with activity", False,
             "两种情况都可能在活动时疼痛", "Both conditions can have pain with activity"),
            ("B", "夜间痛和静息痛（Night pain and pain at rest）", "Presence of night pain and pain at rest", True,
             "夜间痛是应力性骨折的特征，MTSS 没有", "Night pain is characteristic of stress fracture, not MTSS"),
            ("C", "逐渐起病", "Gradual onset", False,
             "两种情况都是逐渐起病", "Both have gradual onset"),
            ("D", "过度使用引起", "Caused by overuse", False,
             "两者都是过度使用损伤", "Both are overuse injuries"),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "触诊时，MTSS 通常表现为_____压痛，而应力性骨折表现为_____压痛。",
        "question_en": "On palpation, MTSS typically shows _____ tenderness, while a stress fracture shows _____ tenderness.",
        "explanation_zh": "MTSS = 弥漫性压痛（diffuse tenderness），伴比目鱼肌止点处的触发点。应力性骨折 = 局限性点状压痛（point tenderness）。",
        "explanation_en": "MTSS = diffuse tenderness with trigger points along the soleus insertion. Stress fracture = localized point tenderness.",
        "options": [
            ("A", "点状（Point）; 弥漫性（Diffuse）", "Point; diffuse", False, None, None),
            ("B", "弥漫性（Diffuse）; 点状（Point）", "Diffuse; point", True, None, None),
            ("C", "无压痛; 弥漫性（Diffuse）", "No; diffuse", False, None, None),
            ("D", "点状（Point）; 无压痛", "Point; no", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "用于评估踝关节外侧扭伤的特殊检查（Special tests）有哪些？",
        "question_en": "Which special tests are used to assess a lateral ankle sprain?",
        "explanation_zh": "前抽屉试验（Anterior drawer test）评估 ATFL，内侧（内翻）距骨倾斜试验（Medial/inversion talar tilt test）评估 CFL。",
        "explanation_en": "The anterior drawer test assesses the ATFL, and the medial (inversion) talar tilt test assesses the CFL.",
        "options": [
            ("A", "内侧距骨倾斜和前抽屉试验（Medial talar tilt and anterior drawer）", "Medial talar tilt and anterior drawer", True, None, None),
            ("B", "外侧距骨倾斜和后抽屉试验（Lateral talar tilt and posterior drawer）", "Lateral talar tilt and posterior drawer", False,
             "外侧距骨倾斜用于检查三角韧带（内侧）",
             "Lateral talar tilt tests the deltoid (medial) ligament"),
            ("C", "Lachman 试验和 McMurray 试验", "Lachman test and McMurray test", False,
             "这些是膝关节检查", "These are knee tests"),
            ("D", "Thompson 试验", "Thompson test", False,
             "用于检查跟腱（Achilles tendon）", "This tests the Achilles tendon"),
        ],
    },
    {
        "type": "multiple", "topic": "Ankle & Lower Leg", "difficulty": "hard",
        "question_zh": "根据渥太华踝关节规则（Ottawa Ankle Rules），哪些发现提示需要进行踝关节 X 线检查？（选择所有正确答案）",
        "question_en": "According to the Ottawa Ankle Rules, which findings indicate the need for an ankle X-ray? (Select all that apply)",
        "explanation_zh": "渥太华踝关节规则指出，以下情况需要踝关节 X 线：胫骨远端后方 6 cm 处有触诊疼痛、腓骨远端后方 6 cm 处有触诊疼痛、或无法负重行走四步。",
        "explanation_en": "The Ottawa Ankle Rules state ankle X-rays are needed for: pain over the distal posterior 6 cm of the tibia or fibula, or inability to bear weight for 4 steps.",
        "options": [
            ("A", "胫骨远端后方 6 cm 处触诊疼痛", "Pain with palpation of the distal posterior 6 cm of the tibia", True, None, None),
            ("B", "腓骨远端后方 6 cm 处触诊疼痛", "Pain with palpation of the distal posterior 6 cm of the fibula", True, None, None),
            ("C", "无法负重行走四步（Inability to bear weight for four steps）", "Inability to bear weight for four steps", True, None, None),
            ("D", "外踝周围肿胀", "Swelling around the lateral malleolus", False,
             "单独的肿胀不是渥太华踝关节规则的标准",
             "Swelling alone is not an Ottawa Ankle Rule criterion"),
        ],
    },
    {
        "type": "multiple", "topic": "Ankle & Lower Leg", "difficulty": "hard",
        "question_zh": "根据渥太华踝关节规则（Ottawa Ankle Rules），哪些发现提示需要进行中足 X 线检查？（选择所有正确答案）",
        "question_en": "According to the Ottawa Ankle Rules, which findings indicate the need for MIDFOOT X-rays? (Select all that apply)",
        "explanation_zh": "中足 X 线检查指征：第五跖骨基底（base of 5th metatarsal）触诊疼痛、舟骨（navicular bone）触诊疼痛、或无法负重行走四步。",
        "explanation_en": "Midfoot X-rays are indicated for: pain on the base of the 5th metatarsal, pain on the navicular bone, or inability to bear weight for 4 steps.",
        "options": [
            ("A", "第五跖骨基底触诊疼痛（Pain on base of 5th metatarsal）", "Pain with palpation of the base of the 5th metatarsal", True, None, None),
            ("B", "舟骨触诊疼痛（Pain on navicular bone）", "Pain with palpation of the navicular bone", True, None, None),
            ("C", "无法负重行走四步", "Inability to bear weight for four steps", True, None, None),
            ("D", "跟骨（Calcaneus）疼痛", "Pain on the calcaneus", False, None, None),
        ],
    },
    {
        "type": "truefalse", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "渥太华踝关节规则（Ottawa Ankle Rules）检查结果为阴性意味着可以 98% 确定没有骨折。",
        "question_en": "A negative Ottawa Ankle Rules test means you can be 98% sure there is no fracture.",
        "explanation_zh": "阴性结果有 98% 的把握排除骨折。阳性结果不能确认骨折——仅提示需要进行 X 线检查。",
        "explanation_en": "A negative test gives 98% certainty of no fracture. A positive test does NOT confirm a fracture—it only indicates the need for X-rays.",
        "options": [
            ("True", "正确（True）", "True", True, None, None),
            ("False", "错误（False）", "False", False,
             "阴性结果有 98% 的把握排除骨折",
             "A negative result gives 98% confidence of no fracture"),
        ],
    },
    {
        "type": "multiple", "topic": "Ankle & Lower Leg", "difficulty": "hard",
        "question_zh": "以下哪些是踝关节扭伤（Ankle sprains）的已知预测因素/风险因素？（选择所有正确答案）",
        "question_en": "Which are known predictors/risk factors for ankle sprains? (Select all that apply)",
        "explanation_zh": "风险因素包括：既往扭伤史、姿势摇摆（postural sway）、踝关节僵硬（<34° 跖屈 ROM）、腓骨肌反应延迟（delayed peroneal reaction time）以及 Y-balance + BMI。",
        "explanation_en": "Risk factors include previous sprains, postural sway, inflexible ankles (<34° PF ROM), delayed peroneal reaction time, and Y-balance + BMI.",
        "options": [
            ("A", "既往踝扭伤史（Previous ankle sprains）", "Previous ankle sprains", True, None, None),
            ("B", "踝关节僵硬（<34° 跖屈 ROM）", "Inflexible ankles (<34° plantar flexion ROM)", True,
             "风险是普通柔韧性（>45°）的近 5 倍",
             "Nearly 5x the risk compared to average flexibility (>45°)"),
            ("C", "腓骨肌反应时间延迟（Delayed peroneal reaction time）", "Delayed peroneal reaction time", True, None, None),
            ("D", "小腿肌肉力量强", "Strong calf muscles", False,
             "强壮的肌肉通常具有保护作用", "Strong muscles are generally protective"),
        ],
    },
    {
        "type": "multiple", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "以下哪些是足底筋膜炎（Plantar fasciitis）的风险因素？（选择所有正确答案）",
        "question_en": "Which are risk factors for plantar fasciitis? (Select all that apply)",
        "explanation_zh": "风险因素包括：高弓足或扁平足（pes cavus or planus）、不合适的鞋子、足底肌肉和小腿柔韧性降低、不正确的跑步模式。",
        "explanation_en": "Risk factors include pes cavus or planus, improper footwear, reduced flexibility of plantar muscles and calf, and improper running pattern.",
        "options": [
            ("A", "高弓足或扁平足（Pes cavus or pes planus）", "Pes cavus or pes planus", True, None, None),
            ("B", "不合适的鞋子（Improper footwear）", "Improper footwear", True, None, None),
            ("C", "足底肌肉和小腿柔韧性降低", "Reduced flexibility of plantar muscles and calf", True, None, None),
            ("D", "踝关节过度背屈活动度", "Excessive ankle dorsiflexion ROM", False, None, None),
        ],
    },
    {
        "type": "multiple", "topic": "Ankle & Lower Leg", "difficulty": "hard",
        "question_zh": "以下哪些是应力性骨折（Stress fractures）的风险因素？（选择所有正确答案）",
        "question_en": "Which are risk factors for stress fractures? (Select all that apply)",
        "explanation_zh": "风险因素包括：突然增加跑量/训练负荷、改变跑步表面或鞋类、女性运动员三联征（闭经 amenorrhea/月经稀少 oligomenorrhea）。",
        "explanation_en": "Risk factors include sudden increases in mileage/training load, change in surface/shoe type, and the female athlete triad (amenorrhea/oligomenorrhea).",
        "options": [
            ("A", "突然增加跑量（Sudden increase in mileage）", "Sudden increase in mileage", True, None, None),
            ("B", "改变跑步表面或鞋类", "Change in running surface or shoe type", True, None, None),
            ("C", "女性运动员三联征（Female athlete triad）", "Female athlete triad (amenorrhea/oligomenorrhea)", True, None, None),
            ("D", "高体质指数（High BMI）", "High body mass index", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "easy",
        "question_zh": "踝关节背屈（Dorsiflexion）的正常活动范围是多少？",
        "question_en": "What is the normal range of motion for ankle dorsiflexion?",
        "explanation_zh": "踝关节正常 ROM：背屈（dorsiflexion）约 20°，跖屈（plantar flexion）约 50°，内翻（inversion）45-60°，外翻（eversion）15-30°。",
        "explanation_en": "Normal ankle ROM: dorsiflexion ~20°, plantar flexion ~50°, inversion 45-60°, eversion 15-30°.",
        "options": [
            ("A", "50 度", "50 degrees", False,
             "50° 是跖屈（plantar flexion）", "50° is plantar flexion"),
            ("B", "20 度", "20 degrees", True, None, None),
            ("C", "45 度", "45 degrees", False,
             "45° 是内翻（inversion）", "45° is inversion"),
            ("D", "30 度", "30 degrees", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "足部应力性骨折最常见的部位是：",
        "question_en": "The most common site for a stress fracture in the foot is the:",
        "explanation_zh": "第二跖骨头（head of 2nd metatarsal）是足部应力性骨折最常见的位置。",
        "explanation_en": "The head of the 2nd metatarsal is the most common location for foot stress fractures.",
        "options": [
            ("A", "跟骨（Calcaneus）", "Calcaneus", False, None, None),
            ("B", "舟骨（Navicular）", "Navicular", False,
             "常见于跳跃运动员和芭蕾舞者，但不是最常见的",
             "Common in jumpers and ballet dancers but not the most common overall"),
            ("C", "第二跖骨头（Head of 2nd metatarsal）", "Head of the 2nd metatarsal", True, None, None),
            ("D", "第五跖骨基底（5th metatarsal base）", "5th metatarsal base", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "踝关节外侧扭伤合并撕脱骨折（Avulsion fracture）最常涉及哪块骨骼？",
        "question_en": "A lateral ankle sprain with an avulsion fracture most commonly involves which bone?",
        "explanation_zh": "踝关节外侧扭伤可导致腓骨短肌腱（peroneus brevis tendon）从第五跖骨基底的撕脱。",
        "explanation_en": "Lateral ankle sprains can cause avulsion of the peroneus brevis tendon from the base of the 5th metatarsal.",
        "options": [
            ("A", "内踝（Medial malleolus）", "Medial malleolus", False,
             "内踝撕脱与内侧踝扭伤相关", "Medial malleolus avulsion is associated with medial ankle sprains"),
            ("B", "第五跖骨基底（Base of 5th metatarsal）", "Base of the 5th metatarsal", True,
             "腓骨短肌腱附着处撕脱", "Avulsion of the peroneus brevis tendon attachment"),
            ("C", "距骨（Talus）", "Talus", False, None, None),
            ("D", "跟骨（Calcaneus）", "Calcaneus", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "哪些肌肉的柔韧性有助于预防胫骨内侧应力综合征（MTSS/shin splints）？",
        "question_en": "Which muscles' flexibility helps prevent MTSS (shin splints)?",
        "explanation_zh": "小腿肌肉（calf muscles）和腘绳肌（hamstrings）的适当柔韧性有助于预防 MTSS。",
        "explanation_en": "Proper flexibility of the calf muscles and hamstrings helps prevent MTSS.",
        "options": [
            ("A", "股四头肌和髋屈肌（Quadriceps and hip flexors）", "Quadriceps and hip flexors", False, None, None),
            ("B", "小腿肌肉和腘绳肌（Calf muscles and hamstrings）", "Calf muscles and hamstrings", True, None, None),
            ("C", "内收肌和外展肌（Adductors and abductors）", "Adductors and abductors", False, None, None),
            ("D", "胫前肌和腓骨肌（Tibialis anterior and peroneals）", "Tibialis anterior and peroneals", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Ankle & Lower Leg", "difficulty": "medium",
        "question_zh": "腓肠肌拉伤（Gastrocnemius strain）的受伤机制（MOI）是什么？",
        "question_en": "What is the MOI for a gastrocnemius strain?",
        "explanation_zh": "腓肠肌拉伤可由伸膝时强力背屈、背屈踝时强力伸膝、或因疲劳/电解质不足导致的肌肉痉挛引起。",
        "explanation_en": "Gastrocnemius strain can result from forced dorsiflexion with extended knee, forced knee extension with dorsiflexed ankle, or muscle cramps from fatigue/electrolyte depletion.",
        "options": [
            ("A", "伸膝时强力背屈（Forced dorsiflexion with extended knee）", "Forced dorsiflexion with extended knee", True, None, None),
            ("B", "强力内翻（Forceful inversion）", "Forceful inversion", False,
             "这会导致踝扭伤", "This causes ankle sprains"),
            ("C", "小腿直接撞击", "Direct blow to the calf", False,
             "这会导致挫伤（contusion）", "This would cause a contusion"),
            ("D", "过度跖屈（Excessive plantar flexion）", "Excessive plantar flexion", False, None, None),
        ],
    },

    # ═══════════════════════════════════════════════════════════
    # TOPIC: Knee
    # ═══════════════════════════════════════════════════════════
    {
        "type": "single", "topic": "Knee", "difficulty": "medium",
        "question_zh": "前交叉韧带（ACL）损伤中有多少比例是非接触性机制？",
        "question_en": "What percentage of ACL injuries occur through non-contact mechanisms?",
        "explanation_zh": "70% 的 ACL 损伤是非接触性的（变向、转身、着地、急停减速）。30% 是接触性损伤。",
        "explanation_en": "70% of ACL injuries are non-contact (cutting, turning, landing, sudden deceleration). 30% are contact injuries.",
        "options": [
            ("A", "30%", "30%", False,
             "30% 是接触性损伤", "30% are contact injuries"),
            ("B", "50%", "50%", False, None, None),
            ("C", "70%", "70%", True, None, None),
            ("D", "90%", "90%", False, None, None),
        ],
    },
    {
        "type": "multiple", "topic": "Knee", "difficulty": "medium",
        "question_zh": "以下哪些是 ACL 损伤的常见非接触性机制？（选择所有正确答案）",
        "question_en": "Which are common non-contact mechanisms for ACL injury? (Select all that apply)",
        "explanation_zh": "非接触性 ACL 损伤通常发生在变向/转身（cutting/turning）、跳跃着地（landing）和急停减速（sudden deceleration）时。",
        "explanation_en": "Non-contact ACL injuries typically occur during cutting/turning maneuvers, landing from jumps, and sudden deceleration.",
        "options": [
            ("A", "变向和转身动作（Cutting and turning maneuvers）", "Cutting and turning maneuvers", True, None, None),
            ("B", "跳跃着地（Landing from a jump）", "Landing from a jump", True, None, None),
            ("C", "急停减速（Sudden deceleration）", "Sudden deceleration", True, None, None),
            ("D", "膝前直接撞击", "Direct blow to the anterior knee", False,
             "这更多与 PCL 损伤相关", "This is more associated with PCL injury"),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "medium",
        "question_zh": "后交叉韧带（PCL）扭伤的典型受伤机制（MOI）是什么？",
        "question_en": "What is the typical MOI for a PCL sprain?",
        "explanation_zh": "PCL 损伤由胫骨后向平移引起，如屈膝跌倒（dashboard injury）或过度屈曲（hyperflexion）。",
        "explanation_en": "PCL injuries result from posterior tibial translation, such as falling on a flexed knee (dashboard injury) or hyperflexion.",
        "options": [
            ("A", "足部着地时受外翻应力（Valgus stress）", "Valgus stress with foot planted", False,
             "这是 MCL 的受伤机制", "This is MCL mechanism"),
            ("B", "跌倒在膝上/胫骨后向平移/过度屈曲", "Fall on knee / posterior tibial translation / hyperflexion", True, None, None),
            ("C", "变向和旋转（Cutting and pivoting）", "Cutting and pivoting", False,
             "这更多与 ACL 相关", "This is more ACL-related"),
            ("D", "内翻应力（Varus stress）", "Varus stress", False,
             "这是 LCL 的受伤机制", "This is LCL mechanism"),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "easy",
        "question_zh": "内侧副韧带（MCL）扭伤由哪种类型的应力引起？",
        "question_en": "MCL sprains are caused by which type of stress?",
        "explanation_zh": "MCL 扭伤由外翻应力（valgus stress）引起（足部着地时，力作用于膝外侧）。",
        "explanation_en": "MCL sprains result from valgus stress (force applied to the outside of the knee with the foot planted).",
        "options": [
            ("A", "内翻应力（Varus stress）", "Varus stress", False,
             "内翻应力影响 LCL", "Varus stress affects the LCL"),
            ("B", "外翻应力（Valgus stress）", "Valgus stress", True, None, None),
            ("C", "前向平移力（Anterior translation）", "Anterior translation", False,
             "这用于检测 ACL", "This tests the ACL"),
            ("D", "后向平移力（Posterior translation）", "Posterior translation", False,
             "这用于检测 PCL", "This tests the PCL"),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "medium",
        "question_zh": "半月板损伤（Meniscal injuries）的受伤机制（MOI）是什么？",
        "question_en": "What is the MOI for meniscal injuries?",
        "explanation_zh": "半月板损伤通常由扭转伴压缩和屈曲（twisting with compression and flexion）引起，或与 MCL 损伤相关。",
        "explanation_en": "Meniscal injuries typically result from twisting with compression and flexion, or can be associated with MCL injuries.",
        "options": [
            ("A", "扭转伴压缩和屈曲（Twisting with compression and flexion）", "Twisting with compression and flexion", True, None, None),
            ("B", "髌骨直接撞击", "Direct blow to the patella", False, None, None),
            ("C", "过伸（Hyperextension）", "Hyperextension", False, None, None),
            ("D", "单纯内翻应力", "Varus stress only", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "easy",
        "question_zh": "与 ACL 损伤最相关的听觉/感觉信号是什么？",
        "question_en": "What auditory/sensory sign is most associated with an ACL injury?",
        "explanation_zh": "ACL 损伤的运动员通常在受伤时听到或感觉到'砰'的一声（pop）。",
        "explanation_en": "Athletes with ACL injuries typically hear or feel a 'pop' at the time of injury.",
        "options": [
            ("A", "弹响/咔嗒声（Click）", "A click", False,
             "弹响更多与半月板损伤相关", "Clicking is more associated with meniscal injuries"),
            ("B", "砰声（Pop）", "A pop", True, None, None),
            ("C", "折断声（Snap）", "A snap", False, None, None),
            ("D", "磨擦感/捻发音（Grinding/Crepitus）", "Grinding", False,
             "磨擦感与髌股关节问题相关", "Grinding/crepitus is associated with patellofemoral issues"),
        ],
    },
    {
        "type": "multiple", "topic": "Knee", "difficulty": "medium",
        "question_zh": "以下哪些症状最常与半月板损伤（Meniscal injuries）相关？（选择所有正确答案）",
        "question_en": "Which symptoms are most commonly associated with meniscal injuries? (Select all that apply)",
        "explanation_zh": "半月板损伤表现为肿胀（swelling）、弹响（snapping）、打软腿（giving way）、间歇性卡锁（intermittent catching and locking）。",
        "explanation_en": "Meniscal injuries present with swelling, snapping, giving way, and intermittent catching and locking.",
        "options": [
            ("A", "肿胀（Swelling）", "Swelling", True, None, None),
            ("B", "间歇性卡锁（Intermittent catching and locking）", "Intermittent catching and locking", True, None, None),
            ("C", "打软腿（Giving way）", "Giving way", True, None, None),
            ("D", "持续性麻木", "Constant numbness", False,
             "麻木不是典型的半月板症状", "Numbness is not a typical meniscal symptom"),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "medium",
        "question_zh": "髌股应力综合征（Patellofemoral stress syndrome, PFSS）的表现是：",
        "question_en": "Patellofemoral stress syndrome presents with:",
        "explanation_zh": "PFSS 表现为膝盖骨下方钝性隐痛（dull, aching pain），活动时加重（跑步、深蹲），伴有捻发音（crepitus）。",
        "explanation_en": "PFSS presents with dull, aching pain under the knee cap that increases with activity (running, squats), along with crepitus.",
        "options": [
            ("A", "仅跑步时的尖锐膝外侧痛", "Sharp lateral knee pain with running only", False, None, None),
            ("B", "膝盖骨下方钝性隐痛，活动时加重（Dull, aching pain under knee cap）", "Dull, aching pain under the knee cap that increases with activity", True, None, None),
            ("C", "膝关节卡锁和绞锁", "Locking and catching of the knee", False,
             "这更多提示半月板损伤", "This is more indicative of meniscal injury"),
            ("D", "膝后方肿胀", "Posterior knee swelling", False, None, None),
        ],
    },
    {
        "type": "truefalse", "topic": "Knee", "difficulty": "medium",
        "question_zh": "后交叉韧带（PCL）损伤最初可能无症状，随后逐渐恶化。",
        "question_en": "A PCL injury may initially be asymptomatic and worsen over time.",
        "explanation_zh": "PCL 损伤可以最初无症状，后续症状逐渐加重。其表现也可能类似于腓肠肌拉伤（gastrocnemius strain）。",
        "explanation_en": "PCL injuries can be initially asymptomatic and symptoms worsen progressively. They may also present like a gastrocnemius strain.",
        "options": [
            ("True", "正确（True）", "True", True, None, None),
            ("False", "错误（False）", "False", False,
             "PCL 损伤可以最初无症状然后逐渐恶化",
             "PCL injuries can be initially asymptomatic and worsen over time"),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "medium",
        "question_zh": "膝关节抵抗胫骨前向平移（Anterior tibial translation）的主要约束是什么？",
        "question_en": "What is the primary restraint against anterior tibial translation at the knee?",
        "explanation_zh": "ACL 是抵抗胫骨前向平移的主要约束。次要约束包括 MCL、LCL 和髂胫束（IT band）。",
        "explanation_en": "The ACL is the primary restraint against anterior tibial translation. Secondary restraints include MCL, LCL, and IT band.",
        "options": [
            ("A", "后交叉韧带（PCL）", "PCL", False,
             "PCL 抵抗胫骨后向平移", "The PCL restrains posterior tibial translation"),
            ("B", "前交叉韧带（ACL）", "ACL", True, None, None),
            ("C", "内侧副韧带（MCL）", "MCL", False,
             "MCL 是抵抗外翻应力的主要约束", "MCL is the primary restraint against valgus stress"),
            ("D", "外侧副韧带（LCL）", "LCL", False,
             "LCL 是抵抗内翻应力的主要约束", "LCL is the primary restraint against varus stress"),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "medium",
        "question_zh": "膝关节抵抗外翻应力（Valgus stress）的主要约束是什么？",
        "question_en": "What is the primary restraint against valgus stress at the knee?",
        "explanation_zh": "MCL 是抵抗外翻应力的主要约束。ACL 和 PCL 是次要约束。",
        "explanation_en": "The MCL is the primary restraint against valgus stress. ACL and PCL serve as secondary restraints.",
        "options": [
            ("A", "前交叉韧带（ACL）", "ACL", False, None, None),
            ("B", "后交叉韧带（PCL）", "PCL", False, None, None),
            ("C", "内侧副韧带（MCL）", "MCL", True, None, None),
            ("D", "外侧副韧带（LCL）", "LCL", False,
             "LCL 是抵抗内翻应力的主要约束", "LCL is the primary restraint against varus stress"),
        ],
    },
    {
        "type": "multiple", "topic": "Knee", "difficulty": "hard",
        "question_zh": "半月板（Menisci）的功能有哪些？（选择所有正确答案）",
        "question_en": "What are the functions of the menisci? (Select all that apply)",
        "explanation_zh": "半月板可加深关节面、辅助润滑、减少摩擦、增加接触面积以分散负荷、吸收冲击、并帮助防止过伸（hyperextension）。",
        "explanation_en": "Menisci deepen the joint, aid lubrication, reduce friction, increase contact area for weight distribution, absorb shock, and help prevent hyperextension.",
        "options": [
            ("A", "吸收冲击（Shock absorption）", "Shock absorption", True, None, None),
            ("B", "增加接触面积以分散负荷", "Increase contact area for weight distribution", True, None, None),
            ("C", "辅助关节润滑和营养", "Aid in lubrication and nutrition of the joint", True, None, None),
            ("D", "抵抗前向平移的主要稳定结构", "Primary stabilizer against anterior translation", False,
             "ACL 是前向稳定的主要结构", "The ACL is the primary anterior stabilizer"),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "hard",
        "question_zh": "内侧半月板（Medial meniscus）与内侧关节囊紧密连接。这在临床上有什么意义？",
        "question_en": "The medial meniscus has a firm attachment to the medial joint capsule. Why does this matter clinically?",
        "explanation_zh": "由于内侧半月板与 MCL/关节囊紧密相连，MCL 扭伤有时会伴随内侧半月板损伤。",
        "explanation_en": "Because the medial meniscus is firmly attached to the MCL/joint capsule, MCL sprains are sometimes accompanied by medial meniscus injuries.",
        "options": [
            ("A", "它使外侧半月板更容易受伤", "It makes the lateral meniscus more injury-prone", False, None, None),
            ("B", "MCL 扭伤可因此牵连内侧半月板", "MCL sprains can involve the medial meniscus due to this attachment", True, None, None),
            ("C", "它增加了 ACL 撕裂的风险", "It increases the risk of ACL tears", False, None, None),
            ("D", "没有临床意义", "It has no clinical significance", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "easy",
        "question_zh": "深蹲时作用于髌股关节（Patellofemoral joint）的压缩力大约是多少？",
        "question_en": "Approximately what compressive force acts on the patellofemoral joint during squatting?",
        "explanation_zh": "深蹲 = 3-7 倍体重；行走 = <1 倍体重；上楼梯 = 2-3 倍体重。",
        "explanation_en": "Squatting = 3-7x body weight; walking = <1x BW; climbing stairs = 2-3x BW.",
        "options": [
            ("A", "小于 1 倍体重", "Less than 1x body weight", False,
             "这是行走（walking）时的力", "This is walking"),
            ("B", "2-3 倍体重", "2-3x body weight", False,
             "这是上楼梯（climbing stairs）时的力", "This is climbing stairs"),
            ("C", "3-7 倍体重", "3-7x body weight", True, None, None),
            ("D", "10-15 倍体重", "10-15x body weight", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "medium",
        "question_zh": "髌腱炎（Patellar tendinitis / Jumper's knee）推荐的强化方法是什么？",
        "question_en": "What is the recommended strengthening approach for patellar tendinitis (jumper's knee)?",
        "explanation_zh": "离心性股四头肌强化（Eccentric quadriceps strengthening）是髌腱炎康复的主要方法。",
        "explanation_en": "Eccentric quadriceps strengthening is the primary rehabilitation approach for patellar tendinitis.",
        "options": [
            ("A", "向心性腘绳肌训练（Concentric hamstring exercises）", "Concentric hamstring exercises", False, None, None),
            ("B", "离心性股四头肌强化（Eccentric quadriceps strengthening）", "Eccentric quadriceps strengthening", True, None, None),
            ("C", "等长小腿提踵（Isometric calf raises）", "Isometric calf raises", False, None, None),
            ("D", "仅被动拉伸", "Passive stretching only", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "hard",
        "question_zh": "半月板修复术（Meniscal repair）后，典型的重返运动时间是多久？",
        "question_en": "After meniscal repair surgery, what is the typical return-to-play timeline?",
        "explanation_zh": "半月板修复：4-6 个月（前 4-6 周不负重）。部分半月板切除术（Partial meniscectomy）：4-6 周重返运动，且再损伤率低于修复术。",
        "explanation_en": "Meniscal repair: 4-6 months (no WB 4-6 weeks). Partial meniscectomy: 4-6 weeks RTP. Partial meniscectomy has fewer re-injuries compared to repairs.",
        "options": [
            ("A", "2-3 周", "2-3 weeks", False, None, None),
            ("B", "4-6 周", "4-6 weeks", False,
             "这是部分半月板切除术（partial meniscectomy）的时间线，不是修复术",
             "This is the timeline for partial meniscectomy, not repair"),
            ("C", "4-6 个月", "4-6 months", True, None, None),
            ("D", "12 个月", "12 months", False, None, None),
        ],
    },
    {
        "type": "truefalse", "topic": "Knee", "difficulty": "medium",
        "question_zh": "外侧副韧带（LCL）扭伤在运动中很常见。",
        "question_en": "LCL sprains are common in sports.",
        "explanation_zh": "LCL 扭伤在运动中很罕见（rare）。需要内翻应力（varus stress，即膝内侧受到撞击且足部着地）。",
        "explanation_en": "LCL sprains are RARE in sports. They require varus stress (impact to the inside of the knee with foot grounded).",
        "options": [
            ("True", "正确（True）", "True", False, None, None),
            ("False", "错误（False）", "False", True,
             "LCL 扭伤在运动中很罕见", "LCL sprains are rare in sports"),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "hard",
        "question_zh": "III 级 LCL 扭伤患者中有多少比例会发展为骨关节炎（Osteoarthritis, OA）？",
        "question_en": "What percentage of Grade III LCL sprain patients will develop osteoarthritis?",
        "explanation_zh": "I 级和 II 级 LCL 扭伤功能预后良好，OA 发生率低。III 级：50% 的患者会发展为 OA（Kannus, 1989; Krukhaug, 1998）。",
        "explanation_en": "Grade I and II LCL sprains have good functional prognosis with low OA incidence. Grade III: 50% of patients will develop OA (Kannus, 1989; Krukhaug, 1998).",
        "options": [
            ("A", "10%", "10%", False, None, None),
            ("B", "25%", "25%", False, None, None),
            ("C", "50%", "50%", True, None, None),
            ("D", "80%", "80%", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "medium",
        "question_zh": "哪个膝关节滑囊（Bursa）最浅表，最容易被直接撞击损伤？",
        "question_en": "Which knee bursa is most superficial and most commonly injured by a direct blow?",
        "explanation_zh": "髌前滑囊（Prepatellar bursa）是膝关节最浅表的滑囊，最常被直接外伤损伤。",
        "explanation_en": "The prepatellar bursa is the most superficial knee bursa and is most commonly injured by direct trauma.",
        "options": [
            ("A", "鹅足滑囊（Pes anserine bursa）", "Pes anserine bursa", False, None, None),
            ("B", "髌前滑囊（Prepatellar bursa）", "Prepatellar bursa", True, None, None),
            ("C", "髌下深层滑囊（Deep infrapatellar bursa）", "Deep infrapatellar bursa", False,
             "通常由过度使用/股四头肌摩擦损伤", "This is typically injured by overuse/quadriceps friction"),
            ("D", "髌上滑囊（Suprapatellar bursa）", "Suprapatellar bursa", False, None, None),
        ],
    },
    {
        "type": "multiple", "topic": "Knee", "difficulty": "hard",
        "question_zh": "为什么女性比男性有更高的 ACL 损伤风险？（选择所有正确答案）",
        "question_en": "Why are women at higher risk for ACL injuries compared to men? (Select all that apply)",
        "explanation_zh": "女性 ACL 损伤率更高，原因包括激素因素（月经周期影响韧带松弛度）和解剖因素（更大的 Q 角）。",
        "explanation_en": "Women have a higher ACL injury rate due to hormonal factors (menstrual cycle influence on ligament laxity) and anatomical factors (higher Q angle).",
        "options": [
            ("A", "月经周期对韧带松弛度的影响（Menstrual cycle influence on ligament laxity）", "Influence of the menstrual cycle on ligament laxity", True, None, None),
            ("B", "更大的 Q 角（Higher Q angle）", "Higher Q angle", True, None, None),
            ("C", "更强的股四头肌", "Stronger quadriceps", False, None, None),
            ("D", "更宽的胫骨平台", "Wider tibial plateau", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "medium",
        "question_zh": "髂胫束摩擦综合征（Iliotibial band friction syndrome）在哪个部位引起疼痛？",
        "question_en": "Iliotibial band friction syndrome causes pain at which location?",
        "explanation_zh": "ITB 摩擦综合征涉及紧张的 ITB/TFL 在股骨外侧髁（lateral femoral condyle）上的摩擦。常见于跑步者、骑自行车者和举重者。",
        "explanation_en": "ITB friction syndrome involves friction of the tight ITB/TFL over the lateral femoral condyle. Common in runners, cyclists, and weightlifters.",
        "options": [
            ("A", "膝内侧关节线", "Medial knee joint line", False, None, None),
            ("B", "股骨外侧髁（Lateral femoral condyle）", "Lateral femoral condyle", True, None, None),
            ("C", "髌骨下极（Inferior pole of patella）", "Inferior pole of the patella", False,
             "这是髌腱炎（patellar tendinitis）的位置", "This is patellar tendinitis"),
            ("D", "鹅足区（Pes anserine area）", "Pes anserine area", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Knee", "difficulty": "hard",
        "question_zh": "鹅足滑囊炎（Pes anserine bursitis）常见于哪些运动员？",
        "question_en": "Pes anserine bursitis is commonly seen in which athletes?",
        "explanation_zh": "鹅足滑囊炎常见于跑步者、游泳者和骑自行车者（过度使用、腘绳肌紧张）或直接外伤。",
        "explanation_en": "Pes anserine bursitis is common in runners, swimmers, and cyclists (overuse, tight hamstrings) or from direct trauma.",
        "options": [
            ("A", "跑步者、游泳者和骑自行车者（Runners, swimmers, cyclists）", "Runners, swimmers, and cyclists", True, None, None),
            ("B", "举重和投掷运动员", "Weightlifters and throwers", False, None, None),
            ("C", "仅接触性运动运动员", "Only contact sport athletes", False, None, None),
            ("D", "主要是体操运动员", "Predominantly gymnasts", False, None, None),
        ],
    },
    {
        "type": "truefalse", "topic": "Knee", "difficulty": "medium",
        "question_zh": "对于 ACL 重建术，患者术前的功能状态会影响术后恢复。",
        "question_en": "For ACL reconstruction, a patient's pre-surgery functional status affects their post-surgery recovery.",
        "explanation_zh": "患者术前功能越好（控制炎症、恢复功能、正常步态），术后恢复越快越好。",
        "explanation_en": "The better the patient's function before surgery (managing inflammation, reestablishing function, normal gait), the faster and better they will recover after surgery.",
        "options": [
            ("True", "正确（True）", "True", True, None, None),
            ("False", "错误（False）", "False", False,
             "术前状态越好，术后恢复越快越好",
             "Better pre-surgery status leads to faster and better recovery"),
        ],
    },

    # ═══════════════════════════════════════════════════════════
    # TOPIC: Hip & Thigh
    # ═══════════════════════════════════════════════════════════
    {
        "type": "single", "topic": "Hip & Thigh", "difficulty": "easy",
        "question_zh": "人体中最常拉伤的肌肉是什么？",
        "question_en": "What is the most frequently strained muscle in the body?",
        "explanation_zh": "腘绳肌（Hamstrings）是人体中最常拉伤的肌肉，常在冲刺时受伤（两端均为离心收缩）。",
        "explanation_en": "The hamstrings are the most frequently strained muscle in the body, commonly injured during sprinting (eccentric contraction at both ends).",
        "options": [
            ("A", "股四头肌（Quadriceps）", "Quadriceps", False, None, None),
            ("B", "腘绳肌（Hamstrings）", "Hamstrings", True, None, None),
            ("C", "腓肠肌（Gastrocnemius）", "Gastrocnemius", False, None, None),
            ("D", "内收肌（Adductors）", "Adductors", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Hip & Thigh", "difficulty": "easy",
        "question_zh": "什么是髋部撞伤（Hip pointer）？",
        "question_en": "What is a hip pointer?",
        "explanation_zh": "髋部撞伤是髂嵴（iliac crest）的挫伤，可能涉及阔筋膜张肌（TFL）和腹外斜肌（external oblique），由钝性外力引起。",
        "explanation_en": "A hip pointer is a contusion of the iliac crest, possibly involving the TFL and external oblique muscle, caused by blunt trauma.",
        "options": [
            ("A", "股骨颈骨折（Femoral neck fracture）", "Fracture of the femoral neck", False, None, None),
            ("B", "髂嵴挫伤（Contusion of the iliac crest）", "Contusion of the iliac crest", True, None, None),
            ("C", "髋关节脱位（Hip dislocation）", "Dislocation of the hip joint", False, None, None),
            ("D", "髋屈肌拉伤（Hip flexor strain）", "Strain of the hip flexors", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Hip & Thigh", "difficulty": "medium",
        "question_zh": "骨化性肌炎（Myositis ossificans）最常与哪种类型的损伤相关？",
        "question_en": "Myositis ossificans is most commonly associated with which type of injury?",
        "explanation_zh": "骨化性肌炎（肌肉组织内异常骨形成）通常由钝性外伤（3 度）或股四头肌反复受击引起，通常在受击时肌肉处于放松状态。",
        "explanation_en": "Myositis ossificans (abnormal bone formation within muscle tissue) typically results from blunt trauma (3rd degree) or repeated impacts to the quadriceps muscle, usually when the muscle is in a relaxed state at impact.",
        "options": [
            ("A", "腘绳肌拉伤（Hamstring strain）", "Hamstring strain", False, None, None),
            ("B", "股四头肌挫伤（Quadriceps contusion）", "Quadriceps contusion", True, None, None),
            ("C", "髋屈肌拉伤（Hip flexor strain）", "Hip flexor strain", False, None, None),
            ("D", "腹股沟拉伤（Groin strain）", "Groin strain", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Hip & Thigh", "difficulty": "medium",
        "question_zh": "股四头肌中最容易拉伤的肌肉是哪一块？",
        "question_en": "Which quadriceps muscle is most often injured in a strain?",
        "explanation_zh": "股直肌（Rectus femoris）是最常拉伤的股四头肌，因为它跨越两个关节（髋关节和膝关节）。",
        "explanation_en": "The rectus femoris is the most commonly strained quadriceps muscle because it crosses two joints (hip and knee).",
        "options": [
            ("A", "股外侧肌（Vastus lateralis）", "Vastus lateralis", False, None, None),
            ("B", "股内侧肌（Vastus medialis）", "Vastus medialis", False, None, None),
            ("C", "股直肌（Rectus femoris）", "Rectus femoris", True, None, None),
            ("D", "股中间肌（Vastus intermedius）", "Vastus intermedius", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Hip & Thigh", "difficulty": "hard",
        "question_zh": "为什么股骨骨折（Femoral fracture）可能危及生命？",
        "question_en": "Why is a femoral fracture potentially life-threatening?",
        "explanation_zh": "股骨骨折可能危及生命，因为股动脉（femoral artery）邻近，可能被损伤导致大量出血。",
        "explanation_en": "A femoral fracture is potentially life-threatening because of the proximity of the femoral artery, which can be damaged and cause massive hemorrhage.",
        "options": [
            ("A", "感染风险", "Risk of infection", False, None, None),
            ("B", "股动脉损伤（Damage to the femoral artery）", "Damage to the femoral artery", True, None, None),
            ("C", "骨筋膜室综合征风险", "Risk of compartment syndrome", False, None, None),
            ("D", "坐骨神经损伤（Sciatic nerve injury）", "Sciatic nerve injury", False, None, None),
        ],
    },
    {
        "type": "multiple", "topic": "Hip & Thigh", "difficulty": "hard",
        "question_zh": "以下哪些是移位性股骨骨折（Displaced femoral fracture）的体征？（选择所有正确答案）",
        "question_en": "Which are signs of a displaced femoral fracture? (Select all that apply)",
        "explanation_zh": "移位性股骨骨折表现为肢体短缩畸形（shortened limb deformity）、严重成角（外旋）、肿胀、剧痛、完全丧失功能和神经血管功能丧失。",
        "explanation_en": "Displaced femoral fractures present with shortened limb deformity, severe angulation (external rotation), swelling, severe pain, total loss of function, and loss of neurovascular function.",
        "options": [
            ("A", "肢体短缩畸形（Shortened limb deformity）", "Shortened limb deformity", True, None, None),
            ("B", "严重成角伴外旋（Severe angulation with external rotation）", "Severe angulation with external rotation", True, None, None),
            ("C", "完全丧失功能（Total loss of function）", "Total loss of function", True, None, None),
            ("D", "步态正常", "Normal gait pattern", False,
             "移位性骨折无法正常行走", "A displaced fracture prevents normal gait"),
        ],
    },
    {
        "type": "single", "topic": "Hip & Thigh", "difficulty": "medium",
        "question_zh": "大转子滑囊炎（Greater trochanteric bursitis）在哪个人群中更常见？",
        "question_en": "Greater trochanteric bursitis is more common in which population?",
        "explanation_zh": "大转子滑囊炎在女性跑步者（因骨盆较宽）、越野滑雪者和芭蕾舞者中更常见。",
        "explanation_en": "Greater trochanteric bursitis is more common in female runners (due to larger hips), cross-country skiers, and ballet dancers.",
        "options": [
            ("A", "男性举重运动员", "Male weightlifters", False, None, None),
            ("B", "女性跑步者（Female runners）", "Female runners", True, None, None),
            ("C", "男性篮球运动员", "Male basketball players", False, None, None),
            ("D", "年轻体操运动员", "Young gymnasts", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Hip & Thigh", "difficulty": "medium",
        "question_zh": "Trendelenburg 试验评估的是哪块肌肉的能力？",
        "question_en": "The Trendelenburg test assesses the capacity of which muscle?",
        "explanation_zh": "Trendelenburg 试验评估臀中肌（Gluteus medius）在单腿站立时稳定骨盆的能力。阳性结果表现为对侧骨盆下沉。",
        "explanation_en": "The Trendelenburg test assesses the gluteus medius' ability to stabilize the pelvis during single-leg stance. A positive test shows contralateral pelvic drop.",
        "options": [
            ("A", "臀大肌（Gluteus maximus）", "Gluteus maximus", False, None, None),
            ("B", "臀中肌（Gluteus medius）", "Gluteus medius", True, None, None),
            ("C", "髂腰肌（Iliopsoas）", "Iliopsoas", False, None, None),
            ("D", "梨状肌（Piriformis）", "Piriformis", False, None, None),
        ],
    },
    {
        "type": "multiple", "topic": "Hip & Thigh", "difficulty": "hard",
        "question_zh": "25 岁以下运动员中，常见的髋部撕脱骨折（Avulsion fracture）部位有哪些？（选择所有正确答案）",
        "question_en": "Which are common avulsion fracture sites at the hip in athletes under 25? (Select all that apply)",
        "explanation_zh": "常见撕脱部位：ASIS（缝匠肌 sartorius）、AIIS（股直肌 rectus femoris）、小转子（髂腰肌 iliopsoas）、坐骨结节（腘绳肌 hamstring）。25 岁以下运动员因骨骺板（epiphyseal plates）未闭合而有风险。",
        "explanation_en": "Common avulsion sites: ASIS (sartorius), AIIS (rectus femoris), lesser trochanter (iliopsoas), ischial tuberosity (hamstring). Athletes <25 are at risk because epiphyseal plates are not closed.",
        "options": [
            ("A", "ASIS — 缝匠肌（Sartorius）", "ASIS — sartorius", True, None, None),
            ("B", "AIIS — 股直肌（Rectus femoris）", "AIIS — rectus femoris", True, None, None),
            ("C", "坐骨结节 — 腘绳肌（Ischial tuberosity — Hamstrings）", "Ischial tuberosity — hamstrings", True, None, None),
            ("D", "大转子 — 臀大肌（Greater trochanter — Gluteus maximus）", "Greater trochanter — gluteus maximus", False, None, None),
        ],
    },
    {
        "type": "multiple", "topic": "Hip & Thigh", "difficulty": "medium",
        "question_zh": "股四头肌挫伤后，应如何预防骨化性肌炎（Myositis ossificans）？（选择所有正确答案）",
        "question_en": "What should be done to prevent myositis ossificans after a quadriceps contusion? (Select all that apply)",
        "explanation_zh": "预防措施：将运动员撤出比赛，伤后 72 小时内不按摩/不热敷/不拉伸，在屈膝位冰敷，不要急于康复或重返运动。",
        "explanation_en": "Prevention: pull athlete from game, no massage/heat/stretching for 72 hrs post-injury, apply ice in flexion, don't rush rehab or RTP.",
        "options": [
            ("A", "伤后 72 小时内不按摩、不热敷、不拉伸", "No massage, heat, or stretching for 72 hours post-injury", True, None, None),
            ("B", "屈膝位冰敷（Apply ice with knee in flexion）", "Apply ice with the knee in flexion", True, None, None),
            ("C", "逐步重返运动，配合功能性拉伸", "Progressive RTP with functional stretches", True, None, None),
            ("D", "立即进行深层组织按摩", "Immediate deep tissue massage", False,
             "72 小时内按摩会增加骨化性肌炎风险",
             "Massage within 72 hours increases myositis ossificans risk"),
        ],
    },
    {
        "type": "multiple", "topic": "Hip & Thigh", "difficulty": "medium",
        "question_zh": "使用稳定球的'腘绳肌三重威胁'（Hamstring triple threat）训练包括哪些组成部分？（选择所有正确答案）",
        "question_en": "The 'hamstring triple threat' exercise on a stability ball includes which components? (Select all that apply)",
        "explanation_zh": "腘绳肌三重威胁包括：臀桥（glute bridge）、腘绳肌弯举（hamstring curl）和髋抬升配合伸膝（离心腘绳肌训练）。",
        "explanation_en": "The hamstring triple threat includes: glute bridge, hamstring curl, and hip lift (maintaining hip lift with knee extension for eccentric hamstring work).",
        "options": [
            ("A", "臀桥（Glute bridge）", "Glute bridge", True, None, None),
            ("B", "腘绳肌弯举（Hamstring curl）", "Hamstring curl", True, None, None),
            ("C", "髋抬升配合伸膝（离心训练）", "Hip lift with knee extension (eccentric)", True, None, None),
            ("D", "腿举（Leg press）", "Leg press", False, None, None),
        ],
    },
    {
        "type": "single", "topic": "Hip & Thigh", "difficulty": "medium",
        "question_zh": "内收肌（腹股沟）拉伤（Adductor/groin strains）最常由什么引起？",
        "question_en": "Adductor (groin) strains are most commonly caused by:",
        "explanation_zh": "内收肌拉伤由快速变向、爆发性推进（常见于冰球）和内收肌与外展肌之间的力量失衡引起。",
        "explanation_en": "Adductor strains result from quick changes of direction, explosive propulsion (common in hockey), and strength imbalances between adductors and abductors.",
        "options": [
            ("A", "腹股沟直接撞击", "Direct blow to the groin", False, None, None),
            ("B", "快速变向和爆发性推进（Quick change of direction and explosive propulsion）", "Quick change of direction and explosive propulsion", True, None, None),
            ("C", "过度髋屈", "Excessive hip flexion", False, None, None),
            ("D", "久坐", "Prolonged sitting", False, None, None),
        ],
    },

    # ═══════════════════════════════════════════════════════════
    # TOPIC: General Injury Concepts
    # ═══════════════════════════════════════════════════════════
    {
        "type": "single", "topic": "General Injury Concepts", "difficulty": "easy",
        "question_zh": "当组织在应力去除后无法恢复正常状态时，发生的是什么类型的组织变形？",
        "question_en": "What type of tissue deformation occurs when a tissue cannot return to its normal state after stress is removed?",
        "explanation_zh": "塑性变形（Plastic deformation）= 组织永久变形（无法恢复正常）。弹性变形（Elastic deformation）= 恢复正常状态。",
        "explanation_en": "Plastic deformation = tissue permanently deformed (cannot return to normal). Elastic deformation = returns to normal state.",
        "options": [
            ("A", "弹性变形（Elastic deformation）", "Elastic deformation", False,
             "弹性变形意味着组织可以恢复正常", "Elastic deformation means the tissue returns to normal"),
            ("B", "塑性变形（Plastic deformation）", "Plastic deformation", True, None, None),
            ("C", "屈服点（Yield point）", "Yield point", False,
             "屈服点是弹性和塑性变形之间的阈值", "The yield point is the threshold between elastic and plastic deformation"),
            ("D", "断裂点（Rupture point）", "Rupture point", False,
             "断裂点是组织完全破坏", "The rupture point is complete tissue failure"),
        ],
    },
    {
        "type": "single", "topic": "General Injury Concepts", "difficulty": "medium",
        "question_zh": "哪种机械力涉及扭转（twisting），导致沿长轴旋转？",
        "question_en": "Which mechanical force involves twisting that causes rotation along the long axis?",
        "explanation_zh": "扭转力（Torsion）= 扭转机制导致沿长轴旋转（如扭转骨折）。其他力：压缩力（compression）、张力（tension）、剪切力（shear）、弯曲力（bending）。",
        "explanation_en": "Torsion = twisting mechanism causing rotation along the long axis (e.g., torsion fractures). Other forces: compression (squeezing), tension (stretching), shear (sliding), bending (convex/concave).",
        "options": [
            ("A", "压缩力（Compression）", "Compression", False, None, None),
            ("B", "剪切力（Shear）", "Shear", False,
             "剪切力导致组织在相邻表面上滑动", "Shear causes tissue to slide over adjoining surfaces"),
            ("C", "扭转力（Torsion）", "Torsion", True, None, None),
            ("D", "张力（Tension）", "Tension", False,
             "张力导致拉伸/延长", "Tension causes stretching/lengthening"),
        ],
    },
    {
        "type": "single", "topic": "General Injury Concepts", "difficulty": "easy",
        "question_zh": "II 级扭伤（Grade 2 sprain）涉及：",
        "question_en": "A Grade 2 sprain involves:",
        "explanation_zh": "I 级 = 轻度过度拉伸，无松弛。II 级 = 韧带部分断裂，有松弛（laxity）但可触及终点（endpoint）。III 级 = 完全断裂，明显不稳定。",
        "explanation_en": "Grade 1 = mild overstretching, no laxity. Grade 2 = partial disruption, with laxity but a felt endpoint. Grade 3 = complete disruption, significant instability.",
        "options": [
            ("A", "轻度过度拉伸，无松弛", "Mild overstretching with no laxity", False,
             "这是 I 级", "This is Grade 1"),
            ("B", "韧带部分断裂，有松弛（Partial disruption with laxity）", "Partial disruption of the ligament with laxity", True, None, None),
            ("C", "韧带完全断裂（Complete disruption）", "Complete disruption of the ligament", False,
             "这是 III 级", "This is Grade 3"),
            ("D", "肌纤维撕裂（Muscle fiber tearing）", "Muscle fiber tearing", False,
             "这描述的是拉伤（strain），不是扭伤（sprain）", "This describes a strain, not a sprain"),
        ],
    },
    {
        "type": "truefalse", "topic": "General Injury Concepts", "difficulty": "medium",
        "question_zh": "III 级扭伤（Grade 3 sprain）在检查时通常比 II 级扭伤更痛。",
        "question_en": "A Grade 3 sprain is typically MORE painful to test than a Grade 2 sprain.",
        "explanation_zh": "III 级扭伤在检查时往往不如 II 级痛，因为韧带已完全断裂，施加应力时不再产生疼痛信号。",
        "explanation_en": "Grade 3 sprains are often LESS painful to test than Grade 2 because the ligament is completely torn and no longer generates pain signals when stressed.",
        "options": [
            ("True", "正确（True）", "True", False, None, None),
            ("False", "错误（False）", "False", True,
             "III 级扭伤检查时可能不如 II 级痛，因为韧带已完全断裂",
             "Grade 3 sprains can be less painful to test than Grade 2 because the ligament is completely disrupted"),
        ],
    },
    {
        "type": "single", "topic": "General Injury Concepts", "difficulty": "medium",
        "question_zh": "肌腱炎（Tendinitis）和肌腱变性（Tendinosis）有什么区别？",
        "question_en": "What is the difference between tendinitis and tendinosis?",
        "explanation_zh": "肌腱炎（Tendinitis）= 肌腱的炎症。肌腱变性（Tendinosis）= 肌腱的微撕裂和退行性变（慢性、非炎症性）。",
        "explanation_en": "Tendinitis = inflammation of the tendon. Tendinosis = microtearing and degeneration of the tendon (chronic, non-inflammatory).",
        "options": [
            ("A", "肌腱炎是慢性的；肌腱变性是急性的", "Tendinitis is chronic; tendinosis is acute", False, None, None),
            ("B", "肌腱炎是炎症；肌腱变性是微撕裂和退行性变", "Tendinitis is inflammation; tendinosis is microtearing and degeneration", True, None, None),
            ("C", "两者是同一种疾病", "They are the same condition", False, None, None),
            ("D", "肌腱变性是腱鞘的炎症", "Tendinosis is inflammation of the tendon sheath", False,
             "那描述的是腱鞘炎（tenosynovitis）", "That describes tenosynovitis"),
        ],
    },
    {
        "type": "single", "topic": "General Injury Concepts", "difficulty": "hard",
        "question_zh": "撕脱骨折（Avulsion fracture）由哪种机械力引起？",
        "question_en": "An avulsion fracture is caused by which type of mechanical force?",
        "explanation_zh": "撕脱骨折由张力（Tension）引起——附着的韧带、肌腱或肌肉将一块骨拉离。",
        "explanation_en": "Avulsion fractures result from tension forces — the pulling away of bone by an attaching ligament, tendon, or muscle.",
        "options": [
            ("A", "压缩力（Compression）", "Compression", False,
             "压缩力导致嵌入/压缩骨折", "Compression causes impacted/compression fractures"),
            ("B", "扭转力（Torsion）", "Torsion", False,
             "扭转力导致螺旋骨折", "Torsion causes spiral fractures"),
            ("C", "张力（Tension）", "Tension", True,
             "附着结构将一块骨拉离", "The attached structure pulls a piece of bone away"),
            ("D", "弯曲力（Bending）", "Bending", False,
             "弯曲力导致直接撞击骨折", "Bending causes fractures from direct blows"),
        ],
    },
]


def main():
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(SCHEMA)

    for k, v in META.items():
        conn.execute("INSERT INTO meta (key, value) VALUES (?, ?)", (k, v))

    for q in QUESTIONS:
        cur = conn.execute(
            "INSERT INTO questions (type, topic, difficulty, question_zh, question_en, image_path, explanation_zh, explanation_en) VALUES (?,?,?,?,?,?,?,?)",
            (q["type"], q.get("topic"), q.get("difficulty"),
             q["question_zh"], q.get("question_en"), q.get("image_path"),
             q.get("explanation_zh"), q.get("explanation_en")),
        )
        qid = cur.lastrowid
        for idx, opt in enumerate(q["options"]):
            label, text_zh, text_en, correct, exp_zh, exp_en = opt
            conn.execute(
                "INSERT INTO options (question_id, label, text_zh, text_en, is_correct, explanation_zh, explanation_en, sort_order) VALUES (?,?,?,?,?,?,?,?)",
                (qid, label, text_zh, text_en, int(correct), exp_zh, exp_en, idx),
            )

    conn.commit()

    count = conn.execute("SELECT COUNT(*) FROM questions").fetchone()[0]
    topics = conn.execute("SELECT topic, COUNT(*) FROM questions GROUP BY topic ORDER BY topic").fetchall()
    conn.close()

    print(f"Created {DB_PATH} with {count} questions:")
    for t, c in topics:
        print(f"  {t}: {c}")


if __name__ == "__main__":
    main()
