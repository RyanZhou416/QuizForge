use rusqlite::{Connection, params};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::Path;

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct QuestionSummary {
    pub id: i64,
    #[serde(rename = "type")]
    pub q_type: String,
    pub topic: Option<String>,
    pub difficulty: Option<String>,
    pub question_zh: String,
    pub question_en: Option<String>,
    pub image_path: Option<String>,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct OptionItem {
    pub id: i64,
    pub question_id: i64,
    pub label: String,
    pub text_zh: String,
    pub text_en: Option<String>,
    pub is_correct: bool,
    pub explanation_zh: Option<String>,
    pub explanation_en: Option<String>,
    pub sort_order: i32,
}

#[derive(Debug, Serialize, Deserialize, Clone)]
pub struct QuestionDetail {
    pub id: i64,
    #[serde(rename = "type")]
    pub q_type: String,
    pub topic: Option<String>,
    pub difficulty: Option<String>,
    pub question_zh: String,
    pub question_en: Option<String>,
    pub image_path: Option<String>,
    pub explanation_zh: Option<String>,
    pub explanation_en: Option<String>,
    pub options: Vec<OptionItem>,
}

#[derive(Debug, Serialize, Deserialize, Default)]
pub struct Filters {
    pub topic: Option<String>,
    #[serde(rename = "type")]
    pub q_type: Option<String>,
    pub difficulty: Option<String>,
}

#[derive(Debug, Serialize, Deserialize)]
pub struct ProgressEntry {
    pub question_id: i64,
    pub answered: i32,
    pub correct: i32,
    pub last_answer: Option<String>,
}

pub struct QuizBank {
    conn: Connection,
}

impl QuizBank {
    pub fn open(path: &Path) -> Result<Self, String> {
        let conn = Connection::open(path).map_err(|e| e.to_string())?;
        conn.execute_batch("PRAGMA foreign_keys = ON;").map_err(|e| e.to_string())?;
        // Ensure progress table exists
        conn.execute_batch(
            "CREATE TABLE IF NOT EXISTS progress (
                question_id INTEGER PRIMARY KEY,
                answered INTEGER DEFAULT 0,
                correct INTEGER DEFAULT 0,
                last_answer TEXT,
                updated_at TEXT DEFAULT (datetime('now'))
            );"
        ).map_err(|e| e.to_string())?;
        Ok(Self { conn })
    }

    pub fn get_meta(&self) -> Result<HashMap<String, String>, String> {
        let mut stmt = self.conn.prepare("SELECT key, value FROM meta")
            .map_err(|e| e.to_string())?;
        let rows = stmt.query_map([], |row| {
            Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?))
        }).map_err(|e| e.to_string())?;

        let mut map = HashMap::new();
        for row in rows {
            if let Ok((k, v)) = row { map.insert(k, v); }
        }
        Ok(map)
    }

    pub fn list_questions(&self, filters: &Filters) -> Result<Vec<QuestionSummary>, String> {
        let mut sql = String::from(
            "SELECT id, type, topic, difficulty, question_zh, question_en, image_path FROM questions WHERE 1=1"
        );
        let mut bind_values: Vec<String> = Vec::new();
        if let Some(ref t) = filters.topic {
            sql.push_str(" AND topic = ?");
            bind_values.push(t.clone());
        }
        if let Some(ref t) = filters.q_type {
            sql.push_str(" AND type = ?");
            bind_values.push(t.clone());
        }
        if let Some(ref d) = filters.difficulty {
            sql.push_str(" AND difficulty = ?");
            bind_values.push(d.clone());
        }
        sql.push_str(" ORDER BY id");

        let mut stmt = self.conn.prepare(&sql).map_err(|e| e.to_string())?;
        let params: Vec<&dyn rusqlite::types::ToSql> = bind_values.iter()
            .map(|v| v as &dyn rusqlite::types::ToSql).collect();

        let rows = stmt.query_map(params.as_slice(), |row| {
            Ok(QuestionSummary {
                id: row.get(0)?,
                q_type: row.get(1)?,
                topic: row.get(2)?,
                difficulty: row.get(3)?,
                question_zh: row.get(4)?,
                question_en: row.get(5)?,
                image_path: row.get(6)?,
            })
        }).map_err(|e| e.to_string())?;

        rows.collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())
    }

    pub fn get_question(&self, id: i64) -> Result<QuestionDetail, String> {
        let q = self.conn.query_row(
            "SELECT id, type, topic, difficulty, question_zh, question_en, image_path, explanation_zh, explanation_en FROM questions WHERE id = ?",
            params![id],
            |row| Ok(QuestionDetail {
                id: row.get(0)?,
                q_type: row.get(1)?,
                topic: row.get(2)?,
                difficulty: row.get(3)?,
                question_zh: row.get(4)?,
                question_en: row.get(5)?,
                image_path: row.get(6)?,
                explanation_zh: row.get(7)?,
                explanation_en: row.get(8)?,
                options: Vec::new(),
            })
        ).map_err(|e| e.to_string())?;

        let mut stmt = self.conn.prepare(
            "SELECT id, question_id, label, text_zh, text_en, is_correct, explanation_zh, explanation_en, sort_order FROM options WHERE question_id = ? ORDER BY sort_order, id"
        ).map_err(|e| e.to_string())?;

        let options = stmt.query_map(params![id], |row| {
            Ok(OptionItem {
                id: row.get(0)?,
                question_id: row.get(1)?,
                label: row.get(2)?,
                text_zh: row.get(3)?,
                text_en: row.get(4)?,
                is_correct: row.get(5)?,
                explanation_zh: row.get(6)?,
                explanation_en: row.get(7)?,
                sort_order: row.get(8)?,
            })
        }).map_err(|e| e.to_string())?
        .collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())?;

        Ok(QuestionDetail { options, ..q })
    }

    pub fn get_topics(&self) -> Result<Vec<String>, String> {
        let mut stmt = self.conn.prepare(
            "SELECT DISTINCT topic FROM questions WHERE topic IS NOT NULL ORDER BY topic"
        ).map_err(|e| e.to_string())?;
        let rows = stmt.query_map([], |row| row.get(0))
            .map_err(|e| e.to_string())?;
        rows.collect::<Result<Vec<_>, _>>().map_err(|e| e.to_string())
    }

    pub fn save_progress(&self, question_id: i64, answer: &str, correct: bool) -> Result<(), String> {
        self.conn.execute(
            "INSERT INTO progress (question_id, answered, correct, last_answer, updated_at)
             VALUES (?1, 1, ?2, ?3, datetime('now'))
             ON CONFLICT(question_id) DO UPDATE SET
                answered = answered + 1,
                correct = correct + ?2,
                last_answer = ?3,
                updated_at = datetime('now')",
            params![question_id, correct as i32, answer],
        ).map_err(|e| e.to_string())?;
        Ok(())
    }

    pub fn get_progress(&self) -> Result<HashMap<i64, ProgressEntry>, String> {
        let mut stmt = self.conn.prepare(
            "SELECT question_id, answered, correct, last_answer FROM progress"
        ).map_err(|e| e.to_string())?;
        let rows = stmt.query_map([], |row| {
            Ok(ProgressEntry {
                question_id: row.get(0)?,
                answered: row.get(1)?,
                correct: row.get(2)?,
                last_answer: row.get(3)?,
            })
        }).map_err(|e| e.to_string())?;

        let mut map = HashMap::new();
        for row in rows {
            if let Ok(p) = row { map.insert(p.question_id, p); }
        }
        Ok(map)
    }
}
