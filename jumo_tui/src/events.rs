use std::time::Duration;

use crossterm::event::{Event as CrosstermEvent, KeyEvent, MouseEvent};
use futures::{FutureExt, StreamExt};
use tokio::sync::mpsc;

#[derive(Clone, Copy, Debug)]
pub enum Event {
    Tick,
    Emote,
}

pub struct EventHandler {
    /// Event sender channel
    sender: mpsc::UnboundedSender<Event>,
    /// Event receiver channel
    receiver: mpsc::UnboundedReceiver<Event>,
    /// Event handler thread
    handler: tokio::task::JoinHandle<()>,
}

impl EventHandler {
    pub fn new(tick_rate: u64) -> Self {
        let tick_rate = Duration::from_millis(tick_rate);
        let (sender, receiver) = mpsc::unbounded_channel();

        let sender_clone = sender.clone();

        let handler = tokio::spawn(async move {
            let mut reader = crossterm::event::EventStream::new();
            let mut tick = tokio::time::interval(tick_rate);

            loop {
                let tick_delay = tick.tick();
                let _crossterm_event = reader.next().fuse();
                tokio::select! {
                    _ = sender_clone.closed() => {
                        break;
                    }
                    _ = tick_delay => {
                        sender_clone.send(Event::Tick).unwrap();
                    }
                }
            }
        });

        Self {
            sender,
            receiver,
            handler,
        }
    }
}
