use std::{borrow::BorrowMut, collections::HashMap, time::Duration};

use color_eyre::eyre::Result;
use edtui::{EditorEventHandler, EditorMode, EditorState, EditorTheme, EditorView, Index2, Lines};
use ratatui::{
    layout::{Constraint, Layout, Rect},
    style::{palette::tailwind, Style, Stylize},
    text::{Line, Span, Text},
    widgets::{List, ListItem, ListState, Padding, Paragraph, Wrap},
    DefaultTerminal, Frame,
};

use crossterm::event::{Event, EventStream, KeyCode, KeyModifiers};
use serde::Deserialize;
use tokio::sync::mpsc;
use tokio_stream::StreamExt;

use crate::{
    block::get_default_block,
    colors::{BG_COLOR, FG_COLOR},
    header::Header,
};

#[derive(Debug, Deserialize)]
pub struct ChatRes {
    pub response: String,
}

#[derive(Default, PartialEq)]
pub enum View {
    #[default]
    Chat,
    Mem,
}

#[derive(Debug, Clone)]
pub enum NetworkError {
    RequestError(String),
    ParseError(String),
}

#[derive(Debug, Deserialize, Clone)]
pub struct Message {
    pub _id: String,
    pub role: String,
    pub content: String,
}

pub struct App {
    should_quit: bool,
    active_view: View,

    mem_editor_state: EditorState,

    chat_editor_state: EditorState,
    chat_messages: Vec<Message>,
    chat_error: Option<NetworkError>,
    chat_loading: bool,

    state_update_tx: mpsc::Sender<StateUpdate>,
    state_update_rx: mpsc::Receiver<StateUpdate>,
}

pub enum StateUpdate {
    AppendChatMessage(Message),
    ChatError(NetworkError),
    SetChatLoading(bool),
    SetShouldQuit(bool),
}

impl App {
    const FRAMES_PER_SECOND: f32 = 60.0;

    pub fn new() -> Self {
        let (tx, rx) = mpsc::channel(32);

        Self {
            should_quit: false,
            active_view: View::Chat,
            chat_editor_state: EditorState::default(),
            mem_editor_state: EditorState::default(),
            chat_messages: Vec::new(),
            chat_error: None,
            chat_loading: false,
            state_update_tx: tx,
            state_update_rx: rx,
        }
    }

    pub async fn run(&mut self, mut terminal: DefaultTerminal) -> Result<()> {
        let period = Duration::from_secs_f32(1.0 / Self::FRAMES_PER_SECOND);
        let mut interval = tokio::time::interval(period);
        let mut events = EventStream::new();

        let mut event_handler = EditorEventHandler::default();

        while !self.should_quit {
            tokio::select! {
                _ = interval.tick() => { terminal.draw(|frame| self.draw(frame))?; },
                Some(Ok(event)) = events.next()  => self.handle_event(&event, &mut event_handler).await,
                Some(event) = self.state_update_rx.recv() => self.handle_state_update(&event),
            }
        }

        Ok(())
    }

    fn handle_state_update(&mut self, update: &StateUpdate) {
        match update {
            StateUpdate::AppendChatMessage(msg) => self.chat_messages.push(msg.clone()),
            StateUpdate::ChatError(err) => self.chat_error = Some(err.clone()),
            StateUpdate::SetChatLoading(loading) => self.chat_loading = *loading,
            StateUpdate::SetShouldQuit(should_quit) => self.should_quit = *should_quit,
        }
    }

    async fn handle_event(&mut self, event: &Event, editor_handler: &mut EditorEventHandler) {
        if let Event::Key(key) = event {
            if self.get_editor_state().mode == EditorMode::Normal {
                if key.code == KeyCode::Char('1') {
                    self.active_view = View::Chat;
                    return;
                }

                if key.code == KeyCode::Char('2') {
                    self.active_view = View::Mem;
                    return;
                }

                if key.code == KeyCode::Tab {
                    self.toggle_view();
                    return;
                }

                if key.code == KeyCode::Enter && !self.chat_loading {
                    let input = String::from_iter(self.get_editor_state().lines.flatten(&None));

                    let state = self.get_editor_state();
                    state.lines = Lines::default();
                    state.cursor = Index2::new(0, 0);

                    self.chat_messages.push(Message {
                        _id: String::new(),
                        role: "user".to_string(),
                        content: input.clone(),
                    });

                    self.state_update_tx
                        .send(StateUpdate::SetChatLoading(true))
                        .await
                        .unwrap();
                    self.send_chat_message(input);
                }
            }

            if key.modifiers.contains(KeyModifiers::CONTROL)
                && (key.code == KeyCode::Char('c') || key.code == KeyCode::Char('q'))
            {
                self.state_update_tx
                    .send(StateUpdate::SetShouldQuit(true))
                    .await
                    .unwrap();
                return;
            }

            editor_handler.on_key_event(*key, self.get_editor_state());
        }
    }

    fn draw(&mut self, frame: &mut Frame) {
        let layout = Layout::default()
            .constraints([
                Constraint::Length(3),
                Constraint::Percentage(75),
                Constraint::Fill(1),
            ])
            .split(frame.area());

        frame.render_widget(Header::new(&self.active_view), layout[0]);
        self.render_output_panel(frame, layout[1]);

        let theme = EditorTheme::default()
            .base(Style::default().bg(*BG_COLOR))
            .block(get_default_block());

        let state = self.get_editor_state();
        let editor = EditorView::new(state).wrap(true).theme(theme);

        frame.render_widget(editor, layout[2]);
    }

    fn render_output_panel(&mut self, frame: &mut Frame, rect: Rect) {
        if let Some(err) = &self.chat_error {
            let message = match err {
                NetworkError::RequestError(err) => err.to_string(),
                NetworkError::ParseError(err) => err.to_string(),
            };

            frame.render_widget(
                Paragraph::new(format!("Error fetching messages:\n\n{}", message))
                    .style(Style::default().fg(tailwind::RED.c500))
                    .bold()
                    .wrap(Wrap { trim: true })
                    .block(get_default_block().padding(Padding::horizontal(1))),
                rect,
            );
            return;
        }

        let messages: Vec<_> = self
            .chat_messages
            .iter()
            .map(|msg| {
                Line::from(vec![
                    Span::styled(
                        format!("[{}]: ", msg.role),
                        Style::default().fg(*FG_COLOR).bold(),
                    ),
                    Span::styled(msg.content.clone(), Style::default().fg(tailwind::WHITE)),
                ])
            })
            .collect();
        let text = Text::from(messages);
        let paragraph = Paragraph::new(text)
            .wrap(Wrap { trim: true })
            .block(get_default_block());

        frame.render_widget(paragraph, rect);
    }

    fn toggle_view(&mut self) {
        self.active_view = match self.active_view {
            View::Chat => View::Mem,
            View::Mem => View::Chat,
        };
    }

    fn get_editor_state(&mut self) -> &mut EditorState {
        match self.active_view {
            View::Chat => self.chat_editor_state.borrow_mut(),
            View::Mem => self.mem_editor_state.borrow_mut(),
        }
    }

    // async fn get_transcript(&self) -> Result<Vec<Message>, NetworkError> {
    //     let text = reqwest::get("http://10.0.0.224:8000/transcript")
    //         .await
    //         .map_err(NetworkError::RequestError)?
    //         .text()
    //         .await
    //         .map_err(NetworkError::RequestError)?;
    //
    //     serde_json::from_str(text.as_str()).map_err(NetworkError::ParseError)
    // }

    fn send_chat_message(&self, message: String) {
        let tx = self.state_update_tx.clone();

        tokio::spawn(async move {
            let mut body = HashMap::new();
            body.insert("input", message);

            let client = reqwest::Client::new();

            let res_result = client
                .post("http://10.0.0.224:8000/chat")
                .json(&body)
                .send()
                .await;

            let result = match res_result {
                Ok(res) => res,
                Err(err) => {
                    tx.send(StateUpdate::ChatError(NetworkError::RequestError(
                        err.to_string(),
                    )))
                    .await
                    .unwrap();
                    return;
                }
            };

            let text = match result.text().await {
                Ok(text) => text,
                Err(err) => {
                    tx.send(StateUpdate::ChatError(NetworkError::RequestError(
                        err.to_string(),
                    )))
                    .await
                    .unwrap();
                    return;
                }
            };

            let parsed_result = serde_json::from_str::<ChatRes>(text.as_str());

            let parsed = match parsed_result {
                Ok(parsed) => parsed,
                Err(err) => {
                    tx.send(StateUpdate::ChatError(NetworkError::ParseError(
                        err.to_string(),
                    )))
                    .await
                    .unwrap();
                    return;
                }
            };

            tx.send(StateUpdate::AppendChatMessage(Message {
                _id: String::new(),
                role: "assistant".to_string(),
                content: parsed.response,
            }))
            .await
            .unwrap();

            tx.send(StateUpdate::SetChatLoading(false)).await.unwrap();
        });
    }
}
