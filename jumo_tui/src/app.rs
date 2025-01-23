use std::{fmt::format, rc::Rc, time::Duration};

use textwrap::{wrap, Options};

use color_eyre::eyre::Result;
use crossterm::event::{Event, EventStream, KeyCode};
use ratatui::{
    layout::{Alignment, Constraint, Direction, Layout, Rect},
    style::{palette::tailwind, Color, Style, Stylize},
    text::Line,
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
    ModeChange { mode: String },
}

enum Mode {
    Chat,
    Debug,
}

pub struct App {
    scroll: usize,
    scroll_state: ScrollbarState,
    transcript: String,
    should_quit: bool,
    emote: String,
    connected: bool,
    transcript_dimensions: Rect,
    autoscroll: bool,
    mode: Mode,
}

impl App {
    const FRAMES_PER_SECOND: f32 = 60.0;

    pub fn new() -> Self {
        Self {
            scroll: 0,
            scroll_state: ScrollbarState::default(),
            transcript: String::new(),
            should_quit: false,
            emote: "NEUTRAL".to_string(),
            connected: true,
            transcript_dimensions: Rect::default(),
            autoscroll: true,
            mode: Mode::Chat,
        }
    }

    pub async fn run(&mut self) -> Result<()> {
        let mut terminal = ratatui::init();

        let mut ws_stream = create_ws_stream("ws://10.0.0.37:8000/ws/jumo".to_string()).await;

        let period = Duration::from_secs_f32(1.0 / Self::FRAMES_PER_SECOND);
        let mut interval = tokio::time::interval(period);
        let mut events = EventStream::new();

        while !self.should_quit {
            tokio::select! {
                _ = interval.tick() => { terminal.draw(|frame| self.draw(frame))?; },
                Some(Ok(event)) = events.next() => self.handle_event(&event),
                Some(message) = ws_stream.next() => self.handle_ws_event(&message).await,
            }
        }

        ratatui::restore();

        Ok(())
    }

    fn get_layout(&self, rect: &Rect) -> Rc<[Rect]> {
        Layout::default()
            .direction(Direction::Vertical)
            .constraints(vec![
                Constraint::Length(3),
                Constraint::Max(20),
                Constraint::Fill(0),
            ])
            .split(*rect)
    }

    fn draw(&mut self, frame: &mut Frame) {
        match self.mode {
            Mode::Chat => self.render_chat(frame),
            Mode::Debug => self.render_debug(frame),
        }
    }

    fn render_chat(&mut self, frame: &mut Frame) {
        let layout = self.get_layout(&frame.area());

        if self.transcript_dimensions == Rect::default() {
            self.transcript_dimensions = layout[2];
        }

        self.render_header(frame, layout[0]);
        self.render_face(frame, layout[1]);
        self.render_transcript(frame, layout[2]);
    }

    fn render_debug(&self, frame: &mut Frame) {
        let lines = vec![
            Line::from("Transcript:").style(Style::new().bold()),
            Line::from("-----------"),
            Line::from(format!(
                "Transcript Dimensions: {}x{}",
                self.transcript_dimensions.width, self.transcript_dimensions.height
            )),
            Line::from(format!("Scroll: {}", self.scroll)),
            Line::from(format!("Autoscroll: {}", self.autoscroll)),
            Line::from(format!("Line Count: {}", self.get_transcript_line_count())),
        ];

        let layout = Layout::default()
            .direction(Direction::Vertical)
            .constraints(vec![Constraint::Length(3), Constraint::Fill(0)])
            .split(frame.area());

        frame.render_widget(
            Paragraph::new("Debug Info")
                .style(Style::new().fg(self.get_fg_color()).bold())
                .block(self.get_block().padding(Padding::horizontal(1))),
            layout[0],
        );

        frame.render_widget(
            Paragraph::new(lines)
                .style(Style::new().fg(self.get_fg_color()).bold())
                .block(self.get_block().padding(Padding::horizontal(1))),
            layout[1],
        );
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
            ServerEvent::ModeChange { mode } => match mode.as_str() {
                "default" => self.mode = Mode::Chat,
                "debug" => self.mode = Mode::Debug,
                _ => {}
            },
            ServerEvent::Emote { emote } => {
                self.emote = emote.to_string();
            }
            ServerEvent::NewMessage => {
                self.transcript = String::new();
                self.autoscroll = true;
                self.scroll = 0;
                self.scroll_state = self.scroll_state.position(self.scroll);
            }
            ServerEvent::NewTextChunk { content } => {
                self.transcript.push_str(content);

                let visible_lines = self.transcript_dimensions.height as usize - 4;
                let total_lines = self.get_transcript_line_count();
                let has_overflow = total_lines > visible_lines;

                if has_overflow && self.autoscroll {
                    self.scroll = total_lines.saturating_sub(visible_lines);
                    self.scroll_state = self.scroll_state.position(self.scroll);
                }
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
                    self.autoscroll = false;
                    // TODO: reset autoscroll if at bottom of transcript
                }
                KeyCode::Char('k') | KeyCode::Up => {
                    self.scroll = self.scroll.saturating_sub(1);
                    self.scroll_state = self.scroll_state.position(self.scroll);
                    self.autoscroll = false;
                }
                KeyCode::Char('d') => {
                    if let Mode::Chat = self.mode {
                        self.mode = Mode::Debug;
                    } else {
                        self.mode = Mode::Chat;
                    }
                }
                _ => {}
            }
        }

        if let Event::Resize(width, height) = event {
            let frame_area = Rect::new(0, 0, *width, *height);
            let layout = self.get_layout(&frame_area);
            let dimensions = &layout[2];
            self.transcript_dimensions = *dimensions;
        }
    }

    fn get_bg_color(&self) -> Color {
        // tailwind::SLATE.c800
        tailwind::ZINC.c950
        // tailwind::YELLOW.c300
        // Color::Rgb(100, 111, 139)
        // Color::Rgb(31, 35, 61)
        // Color::Rgb(39, 49, 56)
    }

    fn get_fg_color(&self) -> Color {
        if self.connected {
            tailwind::YELLOW.c300
            // tailwind::SLATE.c800
            // Color::Rgb(139, 252, 253)
            // Color::Rgb(112, 208, 184)
            // Color::Rgb(180, 234, 227)
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

    fn get_status(&self) -> &str {
        if self.connected {
            "Online"
        } else {
            "Offline"
        }
    }

    fn render_header(&self, frame: &mut Frame, rect: Rect) {
        frame.render_widget(
            Paragraph::new(format!(" JUMO - v0.1.0 - Status: {}", self.get_status()))
                .style(Style::new().fg(self.get_fg_color()).bold())
                .block(self.get_block()),
            rect,
        );
    }

    fn render_face(&self, frame: &mut Frame, rect: Rect) {
        let face_padding = Padding::new(0, 0, rect.height.saturating_sub(10).saturating_div(2), 0);

        frame.render_widget(
            Paragraph::new(self.get_emote())
                .block(self.get_block().padding(face_padding))
                .alignment(Alignment::Center),
            rect,
        );
    }

    fn render_transcript(&mut self, frame: &mut Frame, rect: Rect) {
        frame.render_widget(
            Paragraph::new(self.transcript.clone())
                .style(Style::new().fg(self.get_fg_color()).bold())
                .block(self.get_block().padding(Padding::horizontal(1)))
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

    fn get_transcript_line_count(&self) -> usize {
        let options = Options::new(self.transcript_dimensions.width.into())
            .word_separator(textwrap::WordSeparator::UnicodeBreakProperties);
        wrap(&self.transcript, options).len()
    }
}
