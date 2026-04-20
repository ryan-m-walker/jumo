use tokio::sync::mpsc;

pub struct WebSocketClient {
    receiver: mpsc::Receiver<()>,
}

impl WebSocketClient {
    pub fn new(receiver: mpsc::Receiver<()>) -> Self {
        Self { receiver }
    }

    pub async fn start(&mut self) {
        while let Some(_) = self.receiver.recv().await {
            println!("Received message from WebSocket");
        }
    }
}
