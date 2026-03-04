//! Chat Component - The Spore

use leptos::*;
use crate::{tauri, Message};

#[component]
pub fn Chat(
    messages: ReadSignal<Vec<Message>>,
    set_messages: WriteSignal<Vec<Message>>,
    is_loading: ReadSignal<bool>,
    set_is_loading: WriteSignal<bool>,
) -> impl IntoView {
    let (input, set_input) = create_signal(String::new());
    let input_ref = create_node_ref::<html::Textarea>();
    
    // Send message handler
    let send_message = move |_| {
        let message_text = input.get();
        if message_text.trim().is_empty() {
            return;
        }
        
        // Clear input
        set_input.set(String::new());
        
        // Add user message
        set_messages.update(|msgs| {
            msgs.push(Message {
                role: "user".to_string(),
                content: message_text.clone(),
                timestamp: "now".to_string(), // TODO: proper timestamp
            });
        });
        
        // Send to Claude
        set_is_loading.set(true);
        spawn_local(async move {
            match tauri::send_to_claude(&message_text).await {
                Ok(response) => {
                    set_messages.update(|msgs| {
                        msgs.push(Message {
                            role: "assistant".to_string(),
                            content: response,
                            timestamp: "now".to_string(),
                        });
                    });
                }
                Err(e) => {
                    set_messages.update(|msgs| {
                        msgs.push(Message {
                            role: "assistant".to_string(),
                            content: format!("Error: {}", e),
                            timestamp: "now".to_string(),
                        });
                    });
                }
            }
            set_is_loading.set(false);
        });
    };
    
    // Handle Enter key
    let on_keydown = move |ev: web_sys::KeyboardEvent| {
        if ev.key() == "Enter" && !ev.shift_key() {
            ev.prevent_default();
            send_message(());
        }
    };

    view! {
        <main class="spore">
            <div class="spore__messages">
                <Show 
                    when=move || messages.get().is_empty()
                    fallback=move || view! {
                        <For
                            each=move || messages.get()
                            key=|msg| format!("{}-{}", msg.role, msg.timestamp)
                            children=move |msg| {
                                let class = if msg.role == "user" {
                                    "message message--user"
                                } else {
                                    "message message--assistant"
                                };
                                view! {
                                    <div class=class>
                                        <div class="message__content">{msg.content}</div>
                                    </div>
                                }
                            }
                        />
                    }
                >
                    <div class="spore__welcome">
                        <h2>"🍄 Welcome to Sporecaster"</h2>
                        <p>"The sovereign interface for Planty C."</p>
                        <p class="text-muted">"Type a message or use 'p>' to wake up..."</p>
                    </div>
                </Show>
                
                <Show when=move || is_loading.get()>
                    <div class="loading">
                        <div class="loading__spinner"></div>
                        <span>"Thinking..."</span>
                    </div>
                </Show>
            </div>
            
            <div class="spore__input">
                <textarea
                    class="spore__textarea"
                    placeholder="Send a message... (Enter to send, Shift+Enter for newline)"
                    prop:value=input
                    on:input=move |ev| set_input.set(event_target_value(&ev))
                    on:keydown=on_keydown
                    node_ref=input_ref
                />
                <button 
                    class="spore__send"
                    on:click=send_message
                    disabled=move || is_loading.get() || input.get().trim().is_empty()
                >
                    "Send"
                </button>
            </div>
        </main>
    }
}
