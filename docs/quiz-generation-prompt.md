# QuizForge 题库生成魔咒

将本文件和你的学习资料（PDF/文档/笔记）一起发送给 AI，即可生成标准 JSON 题库。然后用 `json_to_db.py`（位于 `c:\Project\QuizForge\`）转换为 `.db` 文件。**禁止从零重写转换脚本**，必须使用 QuizForge 项目自带的版本。

工作目录应该是学习资料的目录，图片放在images/<项目名>，不要把文件放入c:\Project\QuizForge\

---

## 使用方法

### 基础版（纯文字题库）

1. 将本文件 + 学习资料发给 AI（如 ChatGPT / Claude / Gemini）
2. AI 生成 JSON 文件
3. 保存为 `xxx.json`
4. 运行 `python json_to_db.py xxx.json`，生成 `xxx.db`
5. 将 `.db` 文件拖入 QuizForge 即可使用

### 带图片版（针对 Cursor AI）

1. 先从 PDF 提取图片：
   ```bash
   python extract_pdf_images.py "你的资料.pdf" images
   ```
2. 在 Cursor 中打开项目，确保 `images/` 文件夹在工作区内
3. 将下方 **带图片版魔咒** 连同学习资料发给 Cursor AI，并 **@images** 文件夹
4. Cursor AI 会看到所有提取的图片，生成带 `image_path` 的 JSON
5. 保存为 `xxx.json`
6. 运行（`-i` 指定图片目录）：
   ```bash
   python json_to_db.py xxx.json -i images
   ```
7. 图片会自动嵌入为 base64 data URI，生成的 `.db` 文件自包含，无需额外图片文件

---

## 基础版魔咒（纯文字，复制以下全部内容）

```
请根据我提供的学习资料，生成一套双语（中英文）题库，严格按照以下 JSON 格式输出。

【输出要求】
1. 输出一个完整的 JSON 对象，不要输出其他内容
2. 中文版本中，所有专业术语必须在中文后用英文括号标注，例如：
   - "前交叉韧带（ACL）"
   - "塑性变形（Plastic deformation）"
   - "背屈（Dorsiflexion）"
3. 英文版本保持纯英文
4. 字符串内不要使用未转义的双引号，用单引号替代

【题型分布】
- single（单选题）：约 60%，4 个选项 A/B/C/D
- multiple（多选题）：约 25%，4 个选项 A/B/C/D，2-3 个正确答案
- truefalse（判断题）：约 15%，2 个选项 True/False

【难度分布】
- easy：约 30%（定义、基本概念）
- medium：约 45%（应用、比较、机制）
- hard：约 25%（鉴别诊断、综合分析、数据记忆）

【内容要求】
- 按照资料中的主题/章节分类，设置 topic 字段
- 每个 topic 至少 5 道题
- 总题数不少于 30 道
- 每道题必须有解析（explanation），解释为什么正确答案是对的
- 错误选项尽量附带解析，说明为什么是错的
- 题目应覆盖：关键概念、机制/原因、临床表现、鉴别诊断、风险因素、治疗/康复

【JSON 格式】

{
  "meta": {
    "title": "题库标题（中英双语）",
    "description": "题库描述",
    "author": "作者/来源",
    "version": "1.0"
  },
  "questions": [
    {
      "type": "single",
      "topic": "主题名称",
      "difficulty": "easy|medium|hard",
      "question_zh": "中文题干（专业术语带英文括号）",
      "question_en": "English question stem",
      "explanation_zh": "中文整体解析",
      "explanation_en": "English overall explanation",
      "options": [
        {
          "label": "A",
          "text_zh": "中文选项（术语带英文括号）",
          "text_en": "English option text",
          "is_correct": false,
          "explanation_zh": "中文错误原因（可选，null 表示无）",
          "explanation_en": "English explanation (optional, null if none)"
        },
        {
          "label": "B",
          "text_zh": "中文选项",
          "text_en": "English option text",
          "is_correct": true,
          "explanation_zh": null,
          "explanation_en": null
        },
        {
          "label": "C",
          "text_zh": "中文选项",
          "text_en": "English option text",
          "is_correct": false,
          "explanation_zh": "为什么这个选项是错的",
          "explanation_en": "Why this option is wrong"
        },
        {
          "label": "D",
          "text_zh": "中文选项",
          "text_en": "English option text",
          "is_correct": false,
          "explanation_zh": null,
          "explanation_en": null
        }
      ]
    },
    {
      "type": "multiple",
      "topic": "主题名称",
      "difficulty": "medium",
      "question_zh": "中文题干（选择所有正确答案）",
      "question_en": "English stem (Select all that apply)",
      "explanation_zh": "中文解析",
      "explanation_en": "English explanation",
      "options": [
        {"label": "A", "text_zh": "...", "text_en": "...", "is_correct": true, "explanation_zh": null, "explanation_en": null},
        {"label": "B", "text_zh": "...", "text_en": "...", "is_correct": true, "explanation_zh": null, "explanation_en": null},
        {"label": "C", "text_zh": "...", "text_en": "...", "is_correct": false, "explanation_zh": "...", "explanation_en": "..."},
        {"label": "D", "text_zh": "...", "text_en": "...", "is_correct": true, "explanation_zh": null, "explanation_en": null}
      ]
    },
    {
      "type": "truefalse",
      "topic": "主题名称",
      "difficulty": "medium",
      "question_zh": "中文判断题题干",
      "question_en": "English true/false statement",
      "explanation_zh": "中文解析",
      "explanation_en": "English explanation",
      "options": [
        {"label": "True", "text_zh": "正确（True）", "text_en": "True", "is_correct": true, "explanation_zh": null, "explanation_en": null},
        {"label": "False", "text_zh": "错误（False）", "text_en": "False", "is_correct": false, "explanation_zh": "解释为什么是错的", "explanation_en": "Why it is wrong"}
      ]
    }
  ]
}

请直接输出 JSON，不要包裹在 markdown 代码块中。
```

---

## 带图片版魔咒（针对 Cursor AI，复制以下全部内容）

使用前请先执行 `python extract_pdf_images.py "你的资料.pdf" images` 提取图片，然后在 Cursor 中 **@images** 文件夹让 AI 看到所有图片。

```
请根据我提供的学习资料，生成一套双语（中英文）题库，严格按照以下 JSON 格式输出。

【重要：图片支持】
我已经从 PDF 中提取了图片到 images/ 文件夹。请你：
1. 查看 @images 文件夹中的所有图片
2. 识别每张图片的内容（解剖图、示意图、检查方法图、X光片、流程图等）
3. 在出题时，如果某道题与某张图片相关，在该题的 "image_path" 字段填写图片的相对路径
4. 同时在题干中引导考生观察图片，例如：
   - "观察下图所示的解剖结构（Anatomical structure），..."
   - "根据下图所示的检查方法（Special test），..."
   - "下图展示的影像学表现（Imaging finding）最可能提示..."
5. 没有相关图片的题目，"image_path" 设为 null
6. 同一张图片可以用于多道不同角度的题目
7. 请尽量多利用图片出题，图片题应占总题数的 30-50%

【输出要求】
1. 输出一个完整的 JSON 对象，不要输出其他内容
2. 中文版本中，所有专业术语必须在中文后用英文括号标注，例如：
   - "前交叉韧带（ACL）"
   - "塑性变形（Plastic deformation）"
   - "背屈（Dorsiflexion）"
3. 英文版本保持纯英文
4. 字符串内不要使用未转义的双引号，用单引号替代

【题型分布】
- single（单选题）：约 60%，4 个选项 A/B/C/D
- multiple（多选题）：约 25%，4 个选项 A/B/C/D，2-3 个正确答案
- truefalse（判断题）：约 15%，2 个选项 True/False

【难度分布】
- easy：约 30%（定义、基本概念）
- medium：约 45%（应用、比较、机制）
- hard：约 25%（鉴别诊断、综合分析、数据记忆）

【内容要求】
- 按照资料中的主题/章节分类，设置 topic 字段
- 每个 topic 至少 5 道题
- 总题数不少于 30 道
- 每道题必须有解析（explanation），解释为什么正确答案是对的
- 错误选项尽量附带解析，说明为什么是错的
- 题目应覆盖：关键概念、机制/原因、临床表现、鉴别诊断、风险因素、治疗/康复
- 图片题（有 image_path 的题目）应覆盖：
  - 看图识别结构/部位
  - 看图判断检查方法
  - 看图分析病理/损伤
  - 看图选择正确描述

【JSON 格式】

{
  "meta": {
    "title": "题库标题（中英双语）",
    "description": "题库描述",
    "author": "作者/来源",
    "version": "1.0"
  },
  "questions": [
    {
      "type": "single",
      "topic": "主题名称",
      "difficulty": "easy|medium|hard",
      "question_zh": "中文题干（专业术语带英文括号）",
      "question_en": "English question stem",
      "image_path": "images/page5_img1.png",
      "explanation_zh": "中文整体解析",
      "explanation_en": "English overall explanation",
      "options": [
        {
          "label": "A",
          "text_zh": "中文选项（术语带英文括号）",
          "text_en": "English option text",
          "is_correct": false,
          "explanation_zh": "中文错误原因",
          "explanation_en": "English explanation"
        },
        {
          "label": "B",
          "text_zh": "中文选项",
          "text_en": "English option text",
          "is_correct": true,
          "explanation_zh": null,
          "explanation_en": null
        },
        {
          "label": "C",
          "text_zh": "中文选项",
          "text_en": "English option text",
          "is_correct": false,
          "explanation_zh": "为什么错",
          "explanation_en": "Why wrong"
        },
        {
          "label": "D",
          "text_zh": "中文选项",
          "text_en": "English option text",
          "is_correct": false,
          "explanation_zh": null,
          "explanation_en": null
        }
      ]
    },
    {
      "type": "single",
      "topic": "主题名称",
      "difficulty": "medium",
      "question_zh": "这道题没有关联图片（无 image_path 或设为 null）",
      "question_en": "This question has no associated image",
      "image_path": null,
      "explanation_zh": "中文解析",
      "explanation_en": "English explanation",
      "options": [
        {"label": "A", "text_zh": "...", "text_en": "...", "is_correct": true, "explanation_zh": null, "explanation_en": null},
        {"label": "B", "text_zh": "...", "text_en": "...", "is_correct": false, "explanation_zh": "...", "explanation_en": "..."},
        {"label": "C", "text_zh": "...", "text_en": "...", "is_correct": false, "explanation_zh": null, "explanation_en": null},
        {"label": "D", "text_zh": "...", "text_en": "...", "is_correct": false, "explanation_zh": null, "explanation_en": null}
      ]
    },
    {
      "type": "multiple",
      "topic": "主题名称",
      "difficulty": "medium",
      "question_zh": "观察下图所示结构，选择所有正确描述（Select all that apply）",
      "question_en": "Observe the structure shown in the image. Select all correct descriptions.",
      "image_path": "images/page12_img2.png",
      "explanation_zh": "中文解析",
      "explanation_en": "English explanation",
      "options": [
        {"label": "A", "text_zh": "...", "text_en": "...", "is_correct": true, "explanation_zh": null, "explanation_en": null},
        {"label": "B", "text_zh": "...", "text_en": "...", "is_correct": true, "explanation_zh": null, "explanation_en": null},
        {"label": "C", "text_zh": "...", "text_en": "...", "is_correct": false, "explanation_zh": "...", "explanation_en": "..."},
        {"label": "D", "text_zh": "...", "text_en": "...", "is_correct": true, "explanation_zh": null, "explanation_en": null}
      ]
    },
    {
      "type": "truefalse",
      "topic": "主题名称",
      "difficulty": "medium",
      "question_zh": "中文判断题题干",
      "question_en": "English true/false statement",
      "image_path": null,
      "explanation_zh": "中文解析",
      "explanation_en": "English explanation",
      "options": [
        {"label": "True", "text_zh": "正确（True）", "text_en": "True", "is_correct": true, "explanation_zh": null, "explanation_en": null},
        {"label": "False", "text_zh": "错误（False）", "text_en": "False", "is_correct": false, "explanation_zh": "解释为什么是错的", "explanation_en": "Why it is wrong"}
      ]
    }
  ]
}

请直接输出 JSON，不要包裹在 markdown 代码块中。
```

---

## 重点领域提示（可选，追加在魔咒后面）

如果你想让 AI 聚焦特定重点，可以在魔咒后追加：

```
请重点覆盖以下领域：
- [填写重点 1]
- [填写重点 2]
- [填写重点 3]
```

## 仅英文版本提示（可选）

如果资料是英文且不需要中文翻译，将魔咒中的双语要求替换为：

```
仅输出英文版本。question_zh 和 text_zh 字段直接填写英文内容（与 _en 字段相同）。
explanation_zh 也填写英文。
```

---

## QuizForge SQLite 数据库 Schema（重要）

`json_to_db.py` 转换脚本位于 QuizForge 项目目录（`c:\Project\QuizForge\json_to_db.py`）。如果当前工作目录没有此脚本，**必须从 QuizForge 项目复制，禁止从零重写**。

以下是 QuizForge 要求的 `.db` 表结构，生成的数据库**必须严格遵守**：

```sql
CREATE TABLE IF NOT EXISTS meta (
    key   TEXT PRIMARY KEY,
    value TEXT
);

CREATE TABLE IF NOT EXISTS questions (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    type           TEXT NOT NULL,       -- 'single' | 'multiple' | 'truefalse'
    topic          TEXT,
    difficulty     TEXT,                -- 'easy' | 'medium' | 'hard'
    question_zh    TEXT NOT NULL,
    question_en    TEXT,
    image_path     TEXT,                -- base64 data URI 或 null，列名必须是 image_path
    explanation_zh TEXT,
    explanation_en TEXT
);

CREATE TABLE IF NOT EXISTS options (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id    INTEGER NOT NULL REFERENCES questions(id),
    label          TEXT NOT NULL,       -- 'A'/'B'/'C'/'D' 或 'True'/'False'
    text_zh        TEXT NOT NULL,
    text_en        TEXT,
    is_correct     INTEGER NOT NULL DEFAULT 0,
    explanation_zh TEXT,
    explanation_en TEXT,
    sort_order     INTEGER NOT NULL DEFAULT 0   -- 选项排序，从 0 开始
);
```

**易错点提醒：**
- `questions.image_path` 列名**必须**是 `image_path`（不是 `image_data`、`image` 或其他名称）
- `options` 表**必须**包含 `sort_order` 列
- 图片通过 `json_to_db.py` 自动转换为 base64 data URI 存入 `image_path` 列

---

## 完整工作流速查

### 纯文字题库

```bash
# 1. 将学习资料 + 基础版魔咒发给 AI -> 得到 quiz.json
# 2. 转换（脚本位于 QuizForge 项目目录）
python c:\Project\QuizForge\json_to_db.py quiz.json
# 3. 拖入 QuizForge
```

### 带图片题库（Cursor AI）

```bash
# 1. 提取 PDF 图片
python c:\Project\QuizForge\extract_pdf_images.py "你的资料.pdf" images

# 2. 在 Cursor 中: 带图片版魔咒 + @资料文件 + @images 文件夹 -> 得到 quiz.json

# 3. 转换（-i 指定图片目录，图片自动嵌入为 base64）
python c:\Project\QuizForge\json_to_db.py quiz.json -i images

# 4. 拖入 QuizForge（.db 自包含所有图片，无需额外文件）
```
