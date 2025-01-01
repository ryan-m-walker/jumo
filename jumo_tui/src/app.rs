use std::time::Duration;

use color_eyre::eyre::Result;
use crossterm::event::{Event, EventStream, KeyCode};
use ratatui::{
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{palette::tailwind, Color, Style, Stylize},
    widgets::{
        Block, BorderType, Padding, Paragraph, Scrollbar, ScrollbarOrientation, ScrollbarState,
        Wrap,
    },
    Frame,
};
use serde::{Deserialize, Serialize};
use tokio_stream::StreamExt;

use crate::{
    emotes::get_emote,
    websocket_client::{create_ws_stream, WebSocketMessage},
};

#[derive(Serialize, Deserialize, Debug)]
#[serde(tag = "type")]
enum ServerEvent {
    Emote { emote: String },
    NewMessage,
    NewTextChunk { content: String },
}

pub struct App {
    scroll: usize,
    scroll_state: ScrollbarState,
    transcript: Vec<String>,
    should_quit: bool,
    emote: String,
    connected: bool,
}

impl App {
    const FRAMES_PER_SECOND: f32 = 60.0;

    pub fn new() -> Self {
        Self {
            scroll: 0,
            scroll_state: ScrollbarState::default(),
            transcript: vec![],
            should_quit: false,
            emote: "NEUTRAL".to_string(),
            connected: true,
        }
    }

    pub async fn run(&mut self) -> Result<()> {
        let mut terminal = ratatui::init();

        let mut ws_stream = create_ws_stream("ws://localhost:8000/ws/jumo".to_string()).await;

        self.scroll_state = self
            .scroll_state
            .content_length(self.transcript.join("\n").len());

        let period = Duration::from_secs_f32(1.0 / Self::FRAMES_PER_SECOND);
        let mut interval = tokio::time::interval(period);
        let mut events = EventStream::new();

        while !self.should_quit {
            tokio::select! {
                _ = interval.tick() => { terminal.draw(|frame| self.draw(frame)).unwrap(); },
                Some(Ok(event)) = events.next() => self.handle_event(&event),
                Some(message) = ws_stream.next() => self.handle_ws_event(&message).await,
            }
        }

        ratatui::restore();

        Ok(())
    }

    fn draw(&mut self, frame: &mut Frame) {
        let layout = Layout::default()
            .direction(Direction::Vertical)
            .constraints(vec![
                Constraint::Length(3),
                Constraint::Max(32),
                Constraint::Fill(0),
            ])
            .split(frame.area());

        self.render_header(frame, layout[0]);
        self.render_face(frame, layout[1]);
        self.render_transcript(frame, layout[2]);
    }

    async fn handle_ws_event(&mut self, message: &WebSocketMessage) {
        match message {
            WebSocketMessage::Text(text) => {
                if let Ok(server_event) = serde_json::from_str::<ServerEvent>(text.as_str()) {
                    self.handle_server_event(&server_event);
                }
            }
            WebSocketMessage::Disconnected => {
                self.connected = false;
            }
            WebSocketMessage::Reconnected => {
                self.connected = true;
            }
        }
    }

    fn handle_server_event(&mut self, event: &ServerEvent) {
        match event {
            ServerEvent::Emote { emote } => {
                self.emote = emote.to_string();
            }
            ServerEvent::NewMessage => {
                self.transcript = vec![];
            }
            ServerEvent::NewTextChunk { content } => {
                self.transcript.push(content.to_string());
            }
        }
    }

    fn handle_event(&mut self, event: &Event) {
        if let Event::Key(key) = event {
            match key.code {
                KeyCode::Char('q') | KeyCode::Esc => {
                    self.should_quit = true;
                }
                KeyCode::Char('j') | KeyCode::Down => {
                    self.scroll = self.scroll.saturating_add(1);
                    self.scroll_state = self.scroll_state.position(self.scroll);
                }
                KeyCode::Char('k') | KeyCode::Up => {
                    self.scroll = self.scroll.saturating_sub(1);
                    self.scroll_state = self.scroll_state.position(self.scroll);
                }
                _ => {}
            }
        }
    }

    fn get_bg_color(&self) -> Color {
        // tailwind::SLATE.c800
        // tailwind::YELLOW.c300
        // Color::Rgb(100, 111, 139)
        // Color::Rgb(31, 35, 61)
        Color::Rgb(39, 49, 56)
    }

    fn get_fg_color(&self) -> Color {
        if self.connected {
            // tailwind::YELLOW.c300
            // tailwind::SLATE.c800
            // Color::Rgb(139, 252, 253)
            // Color::Rgb(112, 208, 184)
            Color::Rgb(180, 234, 227)
        } else {
            tailwind::SLATE.c500
        }
    }

    fn get_emote(&self) -> &str {
        if self.connected {
            get_emote(&self.emote)
        } else {
            get_emote("EXPRESSIONLESS")
        }
    }

    fn render_header(&self, frame: &mut Frame, rect: Rect) {
        frame.render_widget(
            Paragraph::new(format!(" JUMO - v0.1.0 - Connected: {}", self.connected))
                .style(Style::new().fg(self.get_fg_color()).bold())
                .block(self.get_block()),
            rect,
        );
    }

    fn render_face(&self, frame: &mut Frame, rect: Rect) {
        let face_padding = Padding::new(0, 0, rect.height / 2 - 5, 0);

        frame.render_widget(
            Paragraph::new(self.get_emote())
                .block(self.get_block().padding(face_padding))
                .alignment(Alignment::Center),
            rect,
        );
    }

    fn render_transcript(&self, frame: &mut Frame, rect: Rect) {
        frame.render_widget(
            Paragraph::new(self.transcript.join(""))
                .style(Style::new().fg(self.get_fg_color()).bold())
                .block(self.get_block().padding(Padding::uniform(1)))
                .wrap(Wrap { trim: true })
                .scroll((self.scroll as u16, 0)),
            rect,
        );

        frame.render_stateful_widget(
            Scrollbar::new(ScrollbarOrientation::VerticalRight)
                .begin_symbol(Some("↑"))
                .end_symbol(Some("↓"))
                .style(Style::new().fg(self.get_fg_color()).bg(self.get_bg_color())),
            rect,
            &mut self.scroll_state.clone(),
        );
    }

    fn get_block(&self) -> Block {
        Block::bordered()
            .style(Style::new().fg(self.get_fg_color()).bg(self.get_bg_color()))
            .border_type(BorderType::Rounded)
    }
}
