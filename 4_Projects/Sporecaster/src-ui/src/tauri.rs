//! Tauri Bindings - WASM to Native Bridge
//! 
//! Wraps Tauri's IPC for clean Rust-to-Rust communication.

use serde::{de::DeserializeOwned, Serialize};
use wasm_bindgen::prelude::*;
use wasm_bindgen_futures::JsFuture;

use crate::NexusNode;

#[wasm_bindgen]
extern "C" {
    #[wasm_bindgen(js_namespace = ["window", "__TAURI__", "core"])]
    async fn invoke(cmd: &str, args: JsValue) -> JsValue;

    #[wasm_bindgen(js_namespace = ["window", "__TAURI__", "event"])]
    async fn listen(event: &str, handler: &Closure<dyn Fn(JsValue)>) -> JsValue;
}

/// Call a Tauri command
async fn call<A: Serialize, R: DeserializeOwned>(
    command: &str,
    args: &A,
) -> Result<R, String> {
    let args_js = serde_wasm_bindgen::to_value(args)
        .map_err(|e| format!("Serialization error: {}", e))?;
    
    let result = invoke(command, args_js).await;
    
    serde_wasm_bindgen::from_value(result)
        .map_err(|e| format!("Deserialization error: {}", e))
}

/// Send message to Claude
pub async fn send_to_claude(message: &str) -> Result<String, String> {
    #[derive(Serialize)]
    struct Args<'a> {
        message: &'a str,
    }
    
    call("send_to_claude", &Args { message }).await
}

/// Get nexus tree
pub async fn get_nexus_tree(
    path: Option<String>,
    depth: Option<u32>,
) -> Result<NexusNode, String> {
    #[derive(Serialize)]
    struct Args {
        path: Option<String>,
        depth: Option<u32>,
    }
    
    call("get_nexus_tree", &Args { path, depth }).await
}

/// Read a file
pub async fn read_file(path: &str) -> Result<String, String> {
    #[derive(Serialize)]
    struct Args<'a> {
        path: &'a str,
    }
    
    call("read_file", &Args { path }).await
}

/// Listen for nexus change events
pub async fn listen_nexus_changes<F>(handler: F)
where
    F: Fn(NexusChangeEvent) + 'static,
{
    let closure = Closure::new(move |value: JsValue| {
        if let Ok(event) = serde_wasm_bindgen::from_value::<NexusChangeEvent>(value) {
            handler(event);
        }
    });
    
    listen("nexus-change", &closure).await;
    
    // Keep closure alive
    closure.forget();
}

/// Nexus change event from backend
#[derive(Debug, Clone, serde::Deserialize)]
pub struct NexusChangeEvent {
    pub kind: String,
    pub paths: Vec<String>,
}
