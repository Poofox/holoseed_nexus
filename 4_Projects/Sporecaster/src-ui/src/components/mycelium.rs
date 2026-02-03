//! Mycelium Component - Nexus Tree Navigator

use leptos::*;
use crate::NexusNode;

#[component]
pub fn Mycelium(tree: ReadSignal<Option<NexusNode>>) -> impl IntoView {
    view! {
        <aside class="mycelium">
            <h3 class="mycelium__title">"📁 Nexus Map"</h3>
            
            <Show 
                when=move || tree.get().is_some()
                fallback=|| view! {
                    <div class="loading">
                        <div class="loading__spinner"></div>
                        <span>"Loading nexus..."</span>
                    </div>
                }
            >
                {move || tree.get().map(|node| view! { <TreeNode node=node depth=0 /> })}
            </Show>
        </aside>
    }
}

#[component]
fn TreeNode(node: NexusNode, depth: usize) -> impl IntoView {
    let (expanded, set_expanded) = create_signal(depth < 1);
    
    // Get icon based on file type
    let icon = if node.is_dir {
        if expanded.get() { "📂" } else { "📁" }
    } else {
        match node.extension.as_deref() {
            Some("md") => "📝",
            Some("lua") => "🌙",
            Some("html") => "🌐",
            Some("json") => "📋",
            Some("py") => "🐍",
            Some("rs") => "🦀",
            Some("css") => "🎨",
            Some("svg") => "🖼️",
            Some("txt") => "📄",
            _ => "📄",
        }
    };
    
    let icon_class = if node.is_dir {
        "tree-node__icon tree-node__icon--dir"
    } else {
        match node.extension.as_deref() {
            Some("md") => "tree-node__icon tree-node__icon--md",
            Some("lua") => "tree-node__icon tree-node__icon--lua",
            Some("html") => "tree-node__icon tree-node__icon--html",
            Some("json") => "tree-node__icon tree-node__icon--json",
            Some("py") => "tree-node__icon tree-node__icon--py",
            _ => "tree-node__icon tree-node__icon--file",
        }
    };
    
    let has_children = !node.children.is_empty();
    let children = node.children.clone();
    let name = node.name.clone();
    
    let on_click = move |_| {
        if has_children {
            set_expanded.update(|e| *e = !*e);
        }
        // TODO: Open file in preview
    };

    view! {
        <div class="tree-node">
            <div class="tree-node__item" on:click=on_click>
                <span class=icon_class>{icon}</span>
                <span>{name}</span>
            </div>
            
            <Show when=move || expanded.get() && has_children>
                <div class="tree-node__children">
                    <For
                        each=move || children.clone()
                        key=|child| child.path.clone()
                        children=move |child| {
                            view! { <TreeNode node=child depth=depth+1 /> }
                        }
                    />
                </div>
            </Show>
        </div>
    }
}
