//! Sporecaster - The Planty C Interface
//! 
//! A sovereign command center for Claude Code + MCP.
//! Full Rust. No JavaScript. No compromises.
//! 
//! 93

#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

mod bridge;
mod watcher;
mod crypto;
mod commands;

use tauri::Manager;

fn main() {
    tauri::Builder::default()
        .plugin(tauri_plugin_shell::init())
        .setup(|app| {
            #[cfg(debug_assertions)]
            {
                let window = app.get_webview_window("main").unwrap();
                window.open_devtools();
            }
            
            // Initialize the filesystem watcher
            let nexus_path = dirs::home_dir()
                .map(|h| h.join("files").join("holoseed_nexus"))
                .expect("Could not find home directory");
            
            println!("🍄 Sporecaster initializing...");
            println!("📁 Nexus path: {:?}", nexus_path);
            
            // Spawn the watcher in a background task
            let app_handle = app.handle().clone();
            tauri::async_runtime::spawn(async move {
                if let Err(e) = watcher::start_watching(nexus_path, app_handle).await {
                    eprintln!("Watcher error: {:?}", e);
                }
            });
            
            println!("✨ Sporecaster ready. 93 93/93");
            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            commands::send_to_claude,
            commands::get_nexus_tree,
            commands::read_file,
            commands::get_sessions,
            commands::save_session,
        ])
        .run(tauri::generate_context!())
        .expect("error while running sporecaster");
}
