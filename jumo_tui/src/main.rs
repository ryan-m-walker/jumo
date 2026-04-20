use app::App;
use color_eyre::Result;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};

mod app;
mod audio;
mod audio_controller;
mod emotes;
mod events;
mod module;
mod websocket_client;
mod ws;

#[tokio::main]
async fn main() -> Result<()> {
    color_eyre::install()?;
    let mut app = App::new();
    app.run().await
}

// fn main() -> Result<()> {
//     let available_hosts = cpal::available_hosts();
//
//     for host_id in available_hosts {
//         println!("Available host: {:?}", host_id);
//         let host = cpal::host_from_id(host_id)?;
//
//         let input_device = host.default_input_device().unwrap();
//         let output_device = host.default_output_device().unwrap();
//
//         let input_config = input_device
//             .default_input_config()
//             .expect("Failed to get default input config");
//         let output_config = output_device
//             .default_output_config()
//             .expect("Failed to get default output config");
//
//         println!("sample format {:?}", input_config.sample_format());
//
//         // if let cpal::SampleFormat::F32 = input_config.sample_format() {
//         //     let stream = input_device.build_input_stream(
//         //         &input_config.into(),
//         //         move |data, _: &_| process_input_data(data),
//         //         move |err| eprintln!("an error occurred on stream: {}", err),
//         //         None,
//         //     )?;
//         //
//         //     stream.play()?;
//         //
//         //     std::thread::sleep(std::time::Duration::from_secs(3));
//         //     drop(stream);
//         // }
//
//         if let cpal::SampleFormat::F32 = output_config.sample_format() {
//             let stream = output_device.build_output_stream(
//                 &output_config.into(),
//                 move |data, _: &_| process_output_data(data),
//                 move |err| eprintln!("an error occurred on stream: {}", err),
//                 None,
//             )?;
//
//             stream.play()?;
//
//             std::thread::sleep(std::time::Duration::from_secs(3));
//             drop(stream);
//         }
//     }
//
//     Ok(())
// }
//
// fn process_input_data(data: &[f32]) {
//     // println!("{:?}", data);
// }
//
// fn process_output_data(data: &mut [f32], channels: usize, output_data: &mut [f32]) {
//     for frame in data.chunks_mut(channels) {
//         let next = output_data.iter().cloned().cycle().take(frame.len());
//         for sample in frame.iter_mut() {
//             *sample = next.clone().next().unwrap();
//         }
//     }
// }
