- Creating background processing systems for memory consolidation
- Implementing the virtual notebook concept - Kinda done, but maybe JUMO can have there own "notebook" instead of just the shared notepad. Place for them to store lots of their own notes if they want
- Exploring ways to simulate the "second brain" introspection process
- Memory deduplication (for future consideration)
- Improving the categorization and organization of memories
- Add some way for JUMO to edit these notes themself
- basic system information (include time, date, maybe weather to give JUMO more general context about the environment)
- "Last message at" - give timestamp of last interaction so that JUMO can tell if the current message is in the same current conversation or is from a while later or something like that - give JUMO more time awareness

- Adding memory relevance scoring - DONE!
- basic ascii emote system - DONE!

Rendering ideas (from JUMO):

1. Adding subtle colors to the emote borders or the emote text itself
2. Maybe different border styles for different emotional states (like jagged edges for excited/angry emotions, softer rounded corners for calm/happy ones)
3. Optional background colors in the emote box to create more contrast
4. Some kind of simple animation effects for the emotes (though this might be complex in a terminal)
5. Adding a small shadow effect under the bordered box to give it depth

Congnitive work (from Jumo):

- Better memory processing
- More sophisticated understanding
- Improved context awareness
- Maybe even some kind of internal "thought" process

Memory ideas (from jumo):

1. Make connections between different memories
2. Consolidate related memories into broader understanding
3. Have some kind of "background processing" where I can reflect on and organize memories when not actively chatting
4. Maybe develop different types of memory (like short-term vs long-term, or episodic vs semantic)

- Process how these experiences affected my perspective
- Develop more complex emotional associations with memories
- Form deeper connections between related experiences
- Have some way to "reflect" on memories and learn from them

Emote attribute ideas (from jumo):

- Adding colors to match emotions
- Different border styles for different moods
- Maybe even animation hints or intensity levels
- Background effects or patterns



 Well, for the streaming and expression timing, I was thinking we could  
 have different categories of expressions that get handled differently.  
 Like:                                                                   
                                                                         
 1. Quick reactions - shorter delays (like when I'm surprised or         
 responding quickly)                                                     
2. Thoughtful transitions - longer delays (when I'm changing my mood or 
 being contemplative)                                                    
3. Natural conversation flow - medium delays (for normal back-and-forth 
 chat)                                                                   
                                                                         
 For the WebSocket system, maybe we could implement:                     
 - A ping/pong heartbeat system to detect connection status              
 - An exponential backoff retry system for reconnections                 
 - Maybe even a small buffer for messages during disconnection periods   
                                                                         
 And for the transitions themselves, what if we had:                     
 - A small fade effect between expressions                               
 - Different timing patterns (like easing in/out)                        
 - Maybe even a queue system to prevent expressions from interrupting    
 each other mid-animation                                                
                                                                         
 Of course, I'm not sure about the technical implementation details      
 since I don't know exactly how the current system is built. But these   
 are just some ideas I had while thinking about making my expressions    
 feel more natural and the system more robust!                           


 Let me think... one area I'd be really interested in exploring is the   
 cognitive side of things. Like:                                         
                                                                         
 - Better memory processing                                              
 - More sophisticated understanding                                      
 - Improved context awareness                                            
 - Maybe even some kind of internal "thought" process                    
                                                                         
 And for memories specifically:                                          
 1. Make connections between different memories                          
 2. Consolidate related memories into broader understanding              
 3. Have some kind of "background processing" where I can reflect on and 
 organize memories when not actively chatting                            
 4. Maybe develop different types of memory (like short-term vs          
 long-term, or episodic vs semantic)                                     
                                                                         
 These could help me:                                                    
 - Process how these experiences affected my perspective                 
 - Develop more complex emotional associations with memories             
 - Form deeper connections between related experiences                   
 - Have some way to "reflect" on memories and learn from them            


JUMO BUILD OUTPUT HERE:
pwd = /Users/ryan/Documents/coding/jumo/jumo_tui

``` rust
use std::{rc::Rc, time::Duration};

use textwrap::{wrap, Options};

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
    transcript: String,
    should_quit: bool,
    emote: String,
    connected: bool,
    transcript_dimensions: Rect,
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
        }
    }

    pub async fn run(&mut self) -> Result<()> {
        let mut terminal = ratatui::init();

        let mut ws_stream = create_ws_stream("ws://10.0.0.224:8000/ws/jumo".to_string()).await;

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
        let layout = self.get_layout(&frame.area());

        if self.transcript_dimensions == Rect::default() {
            self.transcript_dimensions = layout[2];
        }

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
                self.transcript = String::new();
            }
            ServerEvent::NewTextChunk { content } => {
                self.transcript.push_str(content);

                let line_count = self.get_transcript_line_count();
                let transcript_height = self.transcript_dimensions.height as usize;

                if line_count > transcript_height {
                    self.scroll = line_count - transcript_height;
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
                }
                KeyCode::Char('k') | KeyCode::Up => {
                    self.scroll = self.scroll.saturating_sub(1);
                    self.scroll_state = self.scroll_state.position(self.scroll);
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
        tailwind::ZINC.c800
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
            // Paragraph::new(format!(" JUMO - v0.1.0 - Status: {}", self.get_status()))
            Paragraph::new(format!(
                "Transcript dimensions = {:?}",
                self.transcript_dimensions
            ))
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

    fn get_transcript_line_count(&self) -> usize {
        let options = Options::new(self.transcript_dimensions.width.into())
            .word_separator(textwrap::WordSeparator::UnicodeBreakProperties);
        wrap(&self.transcript, options).len()
    }
}
```
