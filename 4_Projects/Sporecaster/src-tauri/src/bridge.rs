//! The Bridge - Claude Code CLI integration
//! 
//! Pipes commands to Claude Code and captures streaming output.
//! This is where the magic happens.

use std::process::Stdio;
use tokio::io::{AsyncBufReadExt, BufReader};
use tokio::process::Command;
use tokio::sync::mpsc;

/// Message from Claude Code
#[derive(Debug, Clone, serde::Serialize)]
pub struct ClaudeMessage {
    pub content: String,
    pub is_complete: bool,
    pub is_error: bool,
}

/// Send a message to Claude Code and stream the response
pub async fn send_message(
    message: &str,
    tx: mpsc::Sender<ClaudeMessage>,
) -> Result<(), Box<dyn std::error::Error + Send + Sync>> {
    // Spawn Claude Code CLI
    // TODO: Make this configurable
    let mut child = Command::new("claude")
        .args(["--print", message])
        .stdout(Stdio::piped())
        .stderr(Stdio::piped())
        .spawn()?;

    let stdout = child.stdout.take().expect("Failed to capture stdout");
    let stderr = child.stderr.take().expect("Failed to capture stderr");

    // Stream stdout
    let tx_stdout = tx.clone();
    let stdout_handle = tokio::spawn(async move {
        let reader = BufReader::new(stdout);
        let mut lines = reader.lines();
        
        while let Ok(Some(line)) = lines.next_line().await {
            let _ = tx_stdout.send(ClaudeMessage {
                content: line,
                is_complete: false,
                is_error: false,
            }).await;
        }
    });

    // Stream stderr
    let tx_stderr = tx.clone();
    let stderr_handle = tokio::spawn(async move {
        let reader = BufReader::new(stderr);
        let mut lines = reader.lines();
        
        while let Ok(Some(line)) = lines.next_line().await {
            let _ = tx_stderr.send(ClaudeMessage {
                content: line,
                is_complete: false,
                is_error: true,
            }).await;
        }
    });

    // Wait for both streams to complete
    let _ = tokio::join!(stdout_handle, stderr_handle);

    // Wait for process to complete
    let status = child.wait().await?;
    
    // Send completion message
    tx.send(ClaudeMessage {
        content: String::new(),
        is_complete: true,
        is_error: !status.success(),
    }).await?;

    Ok(())
}

/// Check if Claude Code CLI is available
pub async fn check_claude_available() -> bool {
    Command::new("claude")
        .arg("--version")
        .output()
        .await
        .map(|o| o.status.success())
        .unwrap_or(false)
}
