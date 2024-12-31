use serde::Deserialize;
use std::fmt;

#[derive(Debug)]
pub enum TranscriptError {
    NetworkError(reqwest::Error),
    JsonParseError(serde_json::Error),
}

impl std::error::Error for TranscriptError {}

impl fmt::Display for TranscriptError {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            TranscriptError::NetworkError(e) => write!(f, "Network error: {}", e),
            TranscriptError::JsonParseError(e) => write!(f, "JSON parsing error: {}", e),
        }
    }
}

#[derive(Deserialize)]
pub struct TranscriptMessage {
    pub user_id: String,
    pub role: String,
    pub content: String,
    pub created_at: String,
}

pub async fn get_transcript() -> Result<Vec<TranscriptMessage>, TranscriptError> {
    let response = reqwest::get("http://localhost:8000/transcript")
        .await
        .map_err(TranscriptError::NetworkError)?;

    let messages = response
        .text()
        .await
        .map_err(TranscriptError::NetworkError)?;

    serde_json::from_str(&messages).map_err(TranscriptError::JsonParseError)
}
