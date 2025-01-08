// use edtui::EditorState;
//
// use crate::app::{Message, NetworkError, View};
//
// // #[derive(Debug, Default, PartialEq)]
// // pub enum View {
// //     #[default]
// //     Chat,
// //     Mem,
// // }
//
// #[derive(Debug)]
// pub enum StateMessage {
//     AppendChatMessage(Message),
//     SetView(View),
// }
//
// #[derive(Default)]
// pub struct State {
//     pub active_view: View,
//
//     pub chat_editor_state: EditorState,
//     pub chat_messages: Vec<Message>,
//     pub chat_error: Option<NetworkError>,
//
//     pub mem_editor_state: EditorState,
// }
//
// impl State {
//     pub fn new(rx: tokio::sync::mpsc::Receiver<StateMessage>) -> Self {
//         Self::default()
//     }
//
//     pub fn listen(&mut self, rx: tokio::sync::mpsc::Receiver<StateMessage>) {
//         tokio::spawn(async move {
//             while let Some(message) = rx.recv().await {
//                 match message {
//                     StateMessage::AppendChatMessage(message) => {
//                         self.chat_messages.push(message);
//                     }
//                     StateMessage::SetView(view) => {
//                         self.active_view = view;
//                     }
//                 }
//             }
//         });
//     }
//
//     fn update(&mut self, message: StateMessage) {}
// }
