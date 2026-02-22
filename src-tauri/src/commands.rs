use crate::db::{QuizBank, QuestionSummary, QuestionDetail, Filters, ProgressEntry};
use crate::watcher;
use parking_lot::Mutex;
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::path::PathBuf;
use tauri::State;

pub struct AppState {
    pub current_bank: Mutex<Option<QuizBank>>,
    pub watch_folders: Mutex<Vec<PathBuf>>,
    pub settings_path: PathBuf,
}

#[derive(Serialize)]
pub struct BankInfo {
    pub path: String,
    pub title: String,
}

#[tauri::command]
pub fn open_bank(path: String, state: State<AppState>) -> Result<(), String> {
    let bank = QuizBank::open(std::path::Path::new(&path))?;
    *state.current_bank.lock() = Some(bank);
    Ok(())
}

#[tauri::command]
pub fn close_bank(state: State<AppState>) -> Result<(), String> {
    *state.current_bank.lock() = None;
    Ok(())
}

#[tauri::command]
pub fn get_bank_meta(state: State<AppState>) -> Result<HashMap<String, String>, String> {
    let guard = state.current_bank.lock();
    let bank = guard.as_ref().ok_or("No bank loaded")?;
    bank.get_meta()
}

#[tauri::command]
pub fn get_questions(filters: Filters, state: State<AppState>) -> Result<Vec<QuestionSummary>, String> {
    let guard = state.current_bank.lock();
    let bank = guard.as_ref().ok_or("No bank loaded")?;
    bank.list_questions(&filters)
}

#[tauri::command]
pub fn get_question_detail(id: i64, state: State<AppState>) -> Result<QuestionDetail, String> {
    let guard = state.current_bank.lock();
    let bank = guard.as_ref().ok_or("No bank loaded")?;
    bank.get_question(id)
}

#[tauri::command]
pub fn get_topics(state: State<AppState>) -> Result<Vec<String>, String> {
    let guard = state.current_bank.lock();
    let bank = guard.as_ref().ok_or("No bank loaded")?;
    bank.get_topics()
}

#[tauri::command]
pub fn save_progress(
    question_id: i64,
    answer: String,
    correct: bool,
    state: State<AppState>,
) -> Result<(), String> {
    let guard = state.current_bank.lock();
    let bank = guard.as_ref().ok_or("No bank loaded")?;
    bank.save_progress(question_id, &answer, correct)
}

#[tauri::command]
pub fn get_progress(state: State<AppState>) -> Result<HashMap<i64, ProgressEntry>, String> {
    let guard = state.current_bank.lock();
    let bank = guard.as_ref().ok_or("No bank loaded")?;
    bank.get_progress()
}

#[tauri::command]
pub fn reset_progress(state: State<AppState>) -> Result<(), String> {
    let guard = state.current_bank.lock();
    let bank = guard.as_ref().ok_or("No bank loaded")?;
    bank.clear_progress()
}

#[tauri::command]
pub fn get_bank_list(state: State<AppState>) -> Result<Vec<BankInfo>, String> {
    let folders = state.watch_folders.lock();
    let mut banks = Vec::new();
    for folder in folders.iter() {
        for path in watcher::scan_folder(folder) {
            let title = path.file_stem()
                .map(|s| s.to_string_lossy().to_string())
                .unwrap_or_default();
            banks.push(BankInfo {
                path: path.to_string_lossy().to_string(),
                title,
            });
        }
    }
    Ok(banks)
}

#[tauri::command]
pub fn add_watch_folder(path: String, state: State<AppState>) -> Result<(), String> {
    let mut folders = state.watch_folders.lock();
    let pb = PathBuf::from(&path);
    if !folders.contains(&pb) {
        folders.push(pb);
    }
    save_settings(&state);
    Ok(())
}

#[tauri::command]
pub fn remove_watch_folder(path: String, state: State<AppState>) -> Result<(), String> {
    let mut folders = state.watch_folders.lock();
    folders.retain(|f| f.to_string_lossy() != path);
    save_settings(&state);
    Ok(())
}

#[tauri::command]
pub fn remove_bank_by_path(bank_path: String, state: State<AppState>) -> Result<(), String> {
    let bp = PathBuf::from(&bank_path);
    if let Some(parent) = bp.parent() {
        let mut folders = state.watch_folders.lock();
        folders.retain(|f| f != parent);
        drop(folders);
        save_settings(&state);
    }
    Ok(())
}

fn save_settings(state: &AppState) {
    let folders = state.watch_folders.lock();
    let paths: Vec<String> = folders.iter().map(|p| p.to_string_lossy().to_string()).collect();
    if let Ok(json) = serde_json::to_string_pretty(&paths) {
        let _ = std::fs::write(&state.settings_path, json);
    }
}

pub fn load_settings(settings_path: &std::path::Path) -> Vec<PathBuf> {
    if let Ok(data) = std::fs::read_to_string(settings_path) {
        if let Ok(paths) = serde_json::from_str::<Vec<String>>(&data) {
            return paths.into_iter().map(PathBuf::from).collect();
        }
    }
    Vec::new()
}
