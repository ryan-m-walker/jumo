use color_eyre::eyre::Result;
use cpal::{
    traits::{DeviceTrait, HostTrait, StreamTrait},
    SampleFormat, StreamConfig,
};
use tokio::sync::mpsc;

use crate::module::Module;

pub struct AudioController {
    recording: bool,
    websocket_tx: mpsc::Sender<Vec<u8>>,
}

impl AudioController {
    pub fn new(websocket_tx: mpsc::Sender<Vec<u8>>) -> Self {
        Self {
            recording: false,
            websocket_tx,
        }
    }

    pub async fn start(&mut self) -> Result<()> {
        let host = cpal::default_host();

        let Some(device) = host.default_input_device() else {
            return Ok(());
        };

        let config = device.default_input_config()?;
        let sample_format = config.sample_format();
        let stream_config: StreamConfig = config.into();

        let handle_err = move |err| {
            eprintln!("an error occurred on stream: {}", err);
        };

        let tx = self.websocket_tx.clone();

        if let SampleFormat::F32 = sample_format {
            let stream = device.build_input_stream(
                &stream_config,
                move |data: &[f32], _: &cpal::InputCallbackInfo| {
                    let bytes = data
                        .iter()
                        .flat_map(|s| s.to_le_bytes())
                        .collect::<Vec<u8>>();
                    let _ = tx.try_send(bytes);
                },
                handle_err,
                None,
            )?;

            self.recording = true;

            stream.play()?;

            #[allow(clippy::while_immutable_condition)]
            while self.recording {
                tokio::time::sleep(std::time::Duration::from_secs(1)).await;
            }
        }

        Ok(())
    }

    pub fn stop(&mut self) {
        self.recording = false;
    }
}
