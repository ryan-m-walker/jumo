use ratatui::eve

pub struct Tui {
    running: bool,
    pub events: EventHandler,
}

impl Tui {
    pub fn new() -> Self {
        Self { running: false }
    }

    pub async fn run(&mut self) -> Result<()> {
        loop {
            if !self.running {
                break;
            }

            // Do some TUI stuff here
        }

        Ok(())
    }

    pub fn quite(&mut self) {
        self.running = false;
    }
}
