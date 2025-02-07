use ratatui::{buffer::Buffer, layout::Rect, widgets::Widget};

struct ChatView {
    editor_state: EditorState,
}

impl ChatView {
    pub fn new() -> Self {
        Self {
            editor_state: EditorState::default(),
        }
    }
}

// impl Widget for ChatView {
//     fn render(&self, area: Rect, buf: &mut Buffer) {
//         // Render the chat view
//     }
// }
