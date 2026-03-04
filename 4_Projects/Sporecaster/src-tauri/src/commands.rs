//! Tauri Commands - IPC Bridge
//! 
//! These are the functions the frontend can call.

use crate::bridge;
use serde::{Deserialize, Serialize};
use std::path::PathBuf;
use tauri::State;
use tokio::sync::Mutex;

/// Nexus tree node
#[derive(Debug, Clone, Serialize)]
pub struct NexusNode {
    pub name: String,
    pub path: String,
    pub is_dir: bool,
    pub children: Vec<NexusNode>,
    pub size: Option<u64>,
    pub extension: Option<String>,
}

/// Session data
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Session {
    pub id: String,
    pub title: String,
    pub messages: Vec<ChatMessage>,
    pub created_at: String,
    pub updated_at: String,
}

/// Chat message
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ChatMessage {
    pub role: String, // "user" or "assistant"
    pub content: String,
    pub timestamp: String,
}

/// App state
pub struct AppState {
    pub nexus_path: PathBuf,
    pub sessions: Mutex<Vec<Session>>,
}

/// Send a message to Claude Code
#[tauri::command]
pub async fn send_to_claude(message: String) -> Result<String, String> {
    // For now, just check if Claude is available and return a placeholder
    // Full streaming implementation will come later
    if !bridge::check_claude_available().await {
        return Err("Claude Code CLI not found. Is it installed?".to_string());
    }
    
    // TODO: Implement proper streaming via events
    Ok(format!("🍄 Message received: {}\n\nStreaming implementation coming soon...", message))
}

/// Get the nexus directory tree
#[tauri::command]
pub async fn get_nexus_tree(path: Option<String>, depth: Option<u32>) -> Result<NexusNode, String> {
    let nexus_path = path
        .map(PathBuf::from)
        .or_else(|| dirs::home_dir().map(|h| h.join("files").join("holoseed_nexus")))
        .ok_or("Could not determine nexus path")?;
    
    let max_depth = depth.unwrap_or(3);
    
    build_tree(&nexus_path, 0, max_depth).ok_or("Failed to read nexus".to_string())
}

/// Build a tree recursively
fn build_tree(path: &PathBuf, current_depth: u32, max_depth: u32) -> Option<NexusNode> {
    let metadata = std::fs::metadata(path).ok()?;
    let name = path.file_name()?.to_string_lossy().to_string();
    
    // Skip hidden files/dirs and common noise
    if name.starts_with('.') || name == "node_modules" || name == "__pycache__" {
        return None;
    }
    
    let is_dir = metadata.is_dir();
    let size = if is_dir { None } else { Some(metadata.len()) };
    let extension = path.extension().map(|e| e.to_string_lossy().to_string());
    
    let children = if is_dir && current_depth < max_depth {
        std::fs::read_dir(path)
            .ok()?
            .filter_map(|entry| {
                let entry = entry.ok()?;
                build_tree(&entry.path(), current_depth + 1, max_depth)
            })
            .collect()
    } else {
        vec![]
    };
    
    Some(NexusNode {
        name,
        path: path.to_string_lossy().to_string(),
        is_dir,
        children,
        size,
        extension,
    })
}

/// Read a file from the nexus
#[tauri::command]
pub async fn read_file(path: String) -> Result<String, String> {
    std::fs::read_to_string(&path).map_err(|e| format!("Failed to read file: {}", e))
}

/// Get all sessions
#[tauri::command]
pub async fn get_sessions() -> Result<Vec<Session>, String> {
    // TODO: Load from disk
    Ok(vec![])
}

/// Save a session
#[tauri::command]
pub async fn save_session(session: Session) -> Result<(), String> {
    // TODO: Persist to disk
    println!("Saving session: {}", session.title);
    Ok(())
}
