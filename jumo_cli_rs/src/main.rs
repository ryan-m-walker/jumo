use app::App;
use color_eyre::eyre::Result;

mod app;
mod block;
mod chat;
mod colors;
mod header;
mod mem;
mod state;

#[tokio::main]
async fn main() -> Result<()> {
    color_eyre::install()?;

    let terminal = ratatui::init();

    let mut app = App::new();
    let result = app.run(terminal).await;

    ratatui::restore();
    result
}
