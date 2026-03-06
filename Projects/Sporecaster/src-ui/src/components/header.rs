//! Header Component

use leptos::*;

#[component]
pub fn Header() -> impl IntoView {
    let (status, _set_status) = create_signal("Connected to Nexus");

    view! {
        <header class="header">
            <div class="header__title">
                <span>"🍄"</span>
                <span>"Sporecaster"</span>
            </div>
            <div class="header__status">
                {status}
            </div>
        </header>
    }
}
