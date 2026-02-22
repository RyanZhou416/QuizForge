#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod commands;
mod db;
mod watcher;

use commands::AppState;
use parking_lot::Mutex;
use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_dialog::init())
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            let app_data = app.path().app_data_dir().expect("No app data dir");
            std::fs::create_dir_all(&app_data).ok();
            let settings_path = app_data.join("watch_folders.json");
            let folders = commands::load_settings(&settings_path);

            let state = AppState {
                current_bank: Mutex::new(None),
                watch_folders: Mutex::new(folders.clone()),
                settings_path,
            };
            app.manage(state);

            if !folders.is_empty() {
                watcher::start_watcher(app.handle().clone(), folders);
            }
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::open_bank,
            commands::close_bank,
            commands::get_bank_meta,
            commands::get_questions,
            commands::get_question_detail,
            commands::get_topics,
            commands::save_progress,
            commands::get_progress,
            commands::reset_progress,
            commands::get_bank_list,
            commands::add_watch_folder,
            commands::remove_watch_folder,
            commands::remove_bank_by_path,
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}
