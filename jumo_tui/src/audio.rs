use color_eyre::eyre::Result;
use cpal::traits::{DeviceTrait, HostTrait, StreamTrait};
use cpal::{SampleFormat, Stream, StreamConfig};
use tokio::sync::mpsc;

pub fn build_input_stream(tx: mpsc::Sender<Vec<u8>>) -> Result<Option<Stream>> {
    let host = cpal::default_host();

    let Some(device) = host.default_input_device() else {
        return Ok(None);
    };

    let config = device.default_input_config()?;
    let sample_format = config.sample_format();
    let stream_config: StreamConfig = config.into();

    let handle_err = move |err| {
        eprintln!("an error occurred on stream: {}", err);
    };

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

        return Ok(Some(stream));
    }

    Ok(None)
}
