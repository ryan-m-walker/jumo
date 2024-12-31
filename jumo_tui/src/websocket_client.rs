use futures_util::{Stream, StreamExt};
use std::{
    pin::Pin,
    task::{Context, Poll},
};
use tokio::sync::mpsc;
use tokio_tungstenite::{connect_async, tungstenite::Message};

// Your custom message type
#[derive(Debug)]
pub enum WebSocketMessage {
    Text(String),
    Disconnected,
    Reconnected,
}

pub struct WebSocketStream {
    receiver: mpsc::Receiver<WebSocketMessage>,
    _shutdown: mpsc::Sender<()>, // Keep sender alive to prevent channel closure
}

impl Stream for WebSocketStream {
    type Item = WebSocketMessage;

    fn poll_next(mut self: Pin<&mut Self>, cx: &mut Context<'_>) -> Poll<Option<Self::Item>> {
        self.receiver.poll_recv(cx)
    }
}

pub async fn create_ws_stream(url: String) -> WebSocketStream {
    let (msg_tx, msg_rx) = mpsc::channel(100);
    let (shutdown_tx, mut shutdown_rx) = mpsc::channel(1);

    // Spawn connection handler
    tokio::spawn(async move {
        let mut reconnect_interval = tokio::time::interval(std::time::Duration::from_secs(5));

        loop {
            tokio::select! {
                _ = shutdown_rx.recv() => break,
                _ = reconnect_interval.tick() => {
                    match connect_async(&url).await {
                        Ok((ws_stream, _)) => {
                            let (_, mut read) = ws_stream.split();
                            let msg_tx = msg_tx.clone();

                            // Notify of successful connection
                            let _ = msg_tx.send(WebSocketMessage::Reconnected).await;

                            // Handle incoming messages
                            while let Some(msg_result) = read.next().await {
                                match msg_result {
                                    Ok(msg) => {
                                        let ws_msg = match msg {
                                            Message::Text(text) => Some(WebSocketMessage::Text(text.to_string())),
                                            Message::Close(_) => {
                                                let _ = msg_tx.send(WebSocketMessage::Disconnected).await;
                                                break;
                                            }
                                            _ => None,
                                        };

                                        if let Some(ws_msg) = ws_msg {
                                            if msg_tx.send(ws_msg).await.is_err() {
                                                break;
                                            }
                                        }
                                    }
                                    Err(_) => {
                                        let _ = msg_tx.send(WebSocketMessage::Disconnected).await;
                                        break;
                                    }
                                }
                            }
                        }
                        Err(_) => {
                            let _ = msg_tx.send(WebSocketMessage::Disconnected).await;
                        }
                    }
                }
            }
        }
    });

    WebSocketStream {
        receiver: msg_rx,
        _shutdown: shutdown_tx,
    }
}
