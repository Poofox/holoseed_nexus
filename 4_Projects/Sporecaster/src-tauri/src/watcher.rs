//! Filesystem Watcher - The Mycelium's Eyes
//! 
//! Watches the nexus for changes and emits events to the frontend.
//! Uses notify crate for now - REPLACE WITH CUSTOM IMPL LATER.

use notify::{Config, Event, RecommendedWatcher, RecursiveMode, Watcher};
use std::path::PathBuf;
use std::sync::mpsc::channel;
use std::time::Duration;
use tauri::{AppHandle, Emitter};

/// Event emitted when the nexus changes
#[derive(Debug, Clone, serde::Serialize)]
pub struct NexusChangeEvent {
    pub kind: String,
    pub paths: Vec<String>,
}

/// Start watching the nexus directory
pub async fn start_watching(
    nexus_path: PathBuf,
    app_handle: AppHandle,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    let (tx, rx) = channel::<Result<Event, notify::Error>>();

    // Create watcher with debounce
    let mut watcher = RecommendedWatcher::new(
        tx,
        Config::default().with_poll_interval(Duration::from_secs(1)),
    )?;

    // Watch the nexus
    watcher.watch(&nexus_path, RecursiveMode::Recursive)?;
    
    println!("👁️ Watching nexus at {:?}", nexus_path);

    // Process events
    loop {
        match rx.recv() {
            Ok(Ok(event)) => {
                let kind = format!("{:?}", event.kind);
                let paths: Vec<String> = event
                    .paths
                    .iter()
                    .map(|p| p.to_string_lossy().to_string())
                    .collect();

                // Don't spam events for hidden/temp files
                if paths.iter().any(|p| {
                    p.contains(".git") || 
                    p.contains(".sync") || 
                    p.ends_with(".tmp") ||
                    p.ends_with("~")
                }) {
                    continue;
                }

                let change_event = NexusChangeEvent { kind, paths };
                
                // Emit to frontend
                if let Err(e) = app_handle.emit("nexus-change", &change_event) {
                    eprintln!("Failed to emit nexus change: {:?}", e);
                }
            }
            Ok(Err(e)) => {
                eprintln!("Watch error: {:?}", e);
            }
            Err(e) => {
                eprintln!("Channel error: {:?}", e);
                break;
            }
        }
    }

    Ok(())
}
