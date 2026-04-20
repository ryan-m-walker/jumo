use std::{collections::HashMap, sync::Arc};

use futures::lock::Mutex;
use tokio::sync::broadcast;

pub enum SystemEvent {
    AudioRecordingStart,
}

pub struct EventBus {
    tx: broadcast::Sender<SystemEvent>,
    subscribers: Arc<Mutex<HashMap<String, broadcast::Receiver<SystemEvent>>>>,
}

impl EventBus {
    pub fn new() -> Self {
        let (tx, _) = broadcast::channel(100);
        let subscribers = Arc::new(Mutex::new(HashMap::new()));

        Self { tx, subscribers }
    }

    pub async fn subscribe(&self, id: String) -> broadcast::Receiver<SystemEvent> {
        let mut subscribers = self.subscribers.lock().await;
        let rx = self.tx.subscribe();
        subscribers.insert(id, rx);
        rx
    }
}
