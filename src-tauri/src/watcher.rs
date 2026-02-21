use notify::{Watcher, RecursiveMode, Event, EventKind};
use notify::event::{CreateKind, ModifyKind, RemoveKind};
use std::path::{Path, PathBuf};
use std::sync::mpsc;
use std::time::Duration;
use tauri::{AppHandle, Emitter};

pub fn start_watcher(app: AppHandle, folders: Vec<PathBuf>) {
    std::thread::spawn(move || {
        let (tx, rx) = mpsc::channel();
        let mut watcher = notify::recommended_watcher(move |res: Result<Event, _>| {
            if let Ok(event) = res {
                let _ = tx.send(event);
            }
        }).expect("Failed to create watcher");

        for folder in &folders {
            if folder.exists() {
                let _ = watcher.watch(folder, RecursiveMode::NonRecursive);
            }
        }

        loop {
            match rx.recv_timeout(Duration::from_secs(1)) {
                Ok(event) => {
                    let dominated = event.paths.iter().any(|p| {
                        p.extension().map_or(false, |e| e == "db")
                    });
                    if !dominated { continue; }
                    match event.kind {
                        EventKind::Create(_) | EventKind::Modify(_) | EventKind::Remove(_) => {
                            let _ = app.emit("banks-changed", ());
                        }
                        _ => {}
                    }
                }
                Err(mpsc::RecvTimeoutError::Timeout) => {}
                Err(mpsc::RecvTimeoutError::Disconnected) => break,
            }
        }
    });
}

pub fn scan_folder(folder: &Path) -> Vec<PathBuf> {
    let mut results = Vec::new();
    if let Ok(entries) = std::fs::read_dir(folder) {
        for entry in entries.flatten() {
            let path = entry.path();
            if path.extension().map_or(false, |e| e == "db") {
                results.push(path);
            }
        }
    }
    results
}
