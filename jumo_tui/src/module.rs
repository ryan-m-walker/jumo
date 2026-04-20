use std::sync::Arc;

use tokio::sync::broadcast;

use crate::events::{EventBus, SystemEvent};

pub trait Module {
    async fn handle_event(&mut self, event: SystemEvent);
    async fn run(&mut self, rx: broadcast::Receiver<SystemEvent>, bus: Arc<EventBus>);
}
