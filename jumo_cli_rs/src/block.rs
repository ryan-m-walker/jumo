use ratatui::{
    style::Style,
    widgets::{Block, BorderType},
};

use crate::colors::{BG_COLOR, FG_COLOR};

pub fn get_default_block() -> Block<'static> {
    Block::bordered()
        .border_type(BorderType::Rounded)
        .border_style(Style::default().fg(*FG_COLOR).bg(*BG_COLOR))
}
