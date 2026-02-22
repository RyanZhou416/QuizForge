# QuizForge — SQLite Schema

Each quiz bank is a standalone `.db` file with the following tables.

## `meta`

Key-value metadata for the quiz bank.

| Column | Type | Notes |
|--------|------|-------|
| key    | TEXT | PRIMARY KEY |
| value  | TEXT | |

Common keys: `title`, `description`, `author`, `version`.

## `questions`

| Column          | Type    | Notes |
|-----------------|---------|-------|
| id              | INTEGER | PRIMARY KEY AUTOINCREMENT |
| type            | TEXT    | `single` / `multiple` / `truefalse` |
| topic           | TEXT    | nullable, free-form category |
| difficulty      | TEXT    | nullable, `easy` / `medium` / `hard` |
| question_zh     | TEXT    | Chinese stem (required) |
| question_en     | TEXT    | English stem (optional) |
| image_path      | TEXT    | optional image reference |
| explanation_zh  | TEXT    | overall explanation (Chinese) |
| explanation_en  | TEXT    | overall explanation (English) |

## `options`

| Column          | Type    | Notes |
|-----------------|---------|-------|
| id              | INTEGER | PRIMARY KEY AUTOINCREMENT |
| question_id     | INTEGER | FK → questions.id |
| label           | TEXT    | `A` / `B` / `C` / `D` or `True` / `False` |
| text_zh         | TEXT    | Chinese option text |
| text_en         | TEXT    | English option text (optional) |
| is_correct      | INTEGER | 0 or 1 |
| explanation_zh  | TEXT    | per-option explanation (Chinese) |
| explanation_en  | TEXT    | per-option explanation (English) |
| sort_order      | INTEGER | display order |

## `progress`

Auto-created by the application on first open.

| Column      | Type    | Notes |
|-------------|---------|-------|
| question_id | INTEGER | PRIMARY KEY, FK → questions.id |
| answered    | INTEGER | times answered |
| correct     | INTEGER | times correct |
| last_answer | TEXT    | last selected labels (comma-separated) |
| updated_at  | TEXT    | ISO datetime |
