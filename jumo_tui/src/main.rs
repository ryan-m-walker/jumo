use app::App;
use color_eyre::Result;

mod app;
mod emotes;
mod websocket_client;

#[tokio::main]
async fn main() -> Result<()> {
    color_eyre::install()?;
    let mut app = App::new();
    app.run().await
}
