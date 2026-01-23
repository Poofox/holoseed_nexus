//! Sporecaster UI - Leptos Frontend
//! 
//! Full Rust. Compiles to WASM. No JavaScript.
//! 
//! 93

use leptos::*;

mod components;
mod tauri;

use components::{Chat, Greenhouse, Header, Mycelium};

/// Main app component
#[component]
pub fn App() -> impl IntoView {
    // Global app state
    let (messages, set_messages) = create_signal(Vec::<Message>::new());
    let (nexus_tree, set_nexus_tree) = create_signal(None::<NexusNode>);
    let (is_loading, set_is_loading) = create_signal(false);

    // Load initial nexus tree
    spawn_local(async move {
        match tauri::get_nexus_tree(None, Some(3)).await {
            Ok(tree) => set_nexus_tree.set(Some(tree)),
            Err(e) => logging::error!("Failed to load nexus: {}", e),
        }
    });

    // Listen for nexus changes
    spawn_local(async move {
        tauri::listen_nexus_changes(move |_event| {
            // Refresh tree on change
            spawn_local(async move {
                if let Ok(tree) = tauri::get_nexus_tree(None, Some(3)).await {
                    set_nexus_tree.set(Some(tree));
                }
            });
        }).await;
    });

    view! {
        <div class="app">
            <Header />
            
            <Greenhouse />
            
            <Chat 
                messages=messages
                set_messages=set_messages
                is_loading=is_loading
                set_is_loading=set_is_loading
            />
            
            <Mycelium tree=nexus_tree />
        </div>
    }
}

/// Chat message
#[derive(Clone, Debug)]
pub struct Message {
    pub role: String,
    pub content: String,
    pub timestamp: String,
}

/// Nexus tree node
#[derive(Clone, Debug, serde::Deserialize)]
pub struct NexusNode {
    pub name: String,
    pub path: String,
    pub is_dir: bool,
    pub children: Vec<NexusNode>,
    pub size: Option<u64>,
    pub extension: Option<String>,
}

/// App entry point
pub fn main() {
    console_error_panic_hook::set_once();
    mount_to_body(|| view! { <App /> });
}
