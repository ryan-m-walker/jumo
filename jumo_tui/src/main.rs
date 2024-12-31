use app::App;
use color_eyre::Result;
use serde::{Deserialize, Serialize};

mod app;
mod emotes;
mod events;
mod transcript;
mod websocket_client;

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type")]
enum ServerEvent {
    Emote { emote: String },
    NewMessage,
    NewTextChunk { content: String },
}

#[tokio::main]
async fn main() -> Result<()> {
    color_eyre::install()?;
    let mut app = App::new();
    app.run().await
}
