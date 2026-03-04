//! Greenhouse Component - Quick Access Sidebar

use leptos::*;

#[component]
pub fn Greenhouse() -> impl IntoView {
    // Pinned items - will be configurable later
    let pinned = vec![
        ("📜", "nexus_state.json"),
        ("🌱", "holoseeds/"),
        ("⚙️", "Scripts/Reaper/"),
        ("📋", "TheRitual/"),
    ];
    
    let recent_sessions = vec![
        "Sporecaster Dev",
        "HATE Lyrics Analysis",
        "Colorado Planning",
    ];

    view! {
        <aside class="greenhouse">
            <section class="greenhouse__section">
                <h3 class="greenhouse__title">"Pinned"</h3>
                <For
                    each=move || pinned.clone()
                    key=|(_, name)| name.to_string()
                    children=move |(icon, name)| {
                        view! {
                            <div class="greenhouse__item">
                                <span>{icon}</span>
                                <span>{name}</span>
                            </div>
                        }
                    }
                />
            </section>
            
            <section class="greenhouse__section">
                <h3 class="greenhouse__title">"Recent Sessions"</h3>
                <For
                    each=move || recent_sessions.clone()
                    key=|name| name.to_string()
                    children=move |name| {
                        view! {
                            <div class="greenhouse__item">
                                <span>"💬"</span>
                                <span>{name}</span>
                            </div>
                        }
                    }
                />
            </section>
            
            <section class="greenhouse__section">
                <h3 class="greenhouse__title">"Quick Actions"</h3>
                <div class="greenhouse__item">
                    <span>"🔄"</span>
                    <span>"Refresh Nexus"</span>
                </div>
                <div class="greenhouse__item">
                    <span>"📝"</span>
                    <span>"New Session"</span>
                </div>
                <div class="greenhouse__item">
                    <span>"⚡"</span>
                    <span>"Wake Up (p>)"</span>
                </div>
            </section>
        </aside>
    }
}
