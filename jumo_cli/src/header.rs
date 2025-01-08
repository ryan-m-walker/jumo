use ratatui::{
    style::{palette::tailwind, Style, Stylize},
    text::{Line, Span},
    widgets::{Block, BorderType, Paragraph, Widget},
};

use crate::{
    app::View,
    colors::{BG_COLOR, FG_COLOR},
};

pub struct Header<'a> {
    view: &'a View,
}

impl<'a> Header<'a> {
    pub fn new(view: &'a View) -> Self {
        Self { view }
    }
}

impl Widget for Header<'_> {
    fn render(self, area: ratatui::prelude::Rect, buf: &mut ratatui::prelude::Buffer) {
        let inactive_style = Style::default().fg(*FG_COLOR).bg(*BG_COLOR);
        let active_style = Style::default().bold().fg(*BG_COLOR).bg(*FG_COLOR);

        let header_text = Line::from_iter([
            Span::styled(" JUMO CLI - ", Style::default().fg(*FG_COLOR).bold()),
            Span::styled(
                " [1] Chat ",
                if *self.view == View::Chat {
                    active_style
                } else {
                    inactive_style
                },
            ),
            Span::styled(
                " [2] Mem ",
                if *self.view == View::Mem {
                    active_style
                } else {
                    inactive_style
                },
            ),
        ]);

        Paragraph::new(header_text)
            .style(
                Style::default()
                    .fg(tailwind::YELLOW.c300)
                    .bg(tailwind::SLATE.c800),
            )
            .block(Block::bordered().border_type(BorderType::Rounded))
            .render(area, buf);
    }
}
