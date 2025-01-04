!#/bin/bash

echo "Building Jumo TUI for Raspberry Pi..."

# Build docker image if it doesn't exist
docker build -t jumo-builder -f Dockerfile.build . || exit 1

# Run cross-compilation
docker run -v "$(pwd):/app" -w /app jumo-builder \
cargo build --target aarch64-unknown-linux-gnu || exit 1

PI_HOST="ryan@10.0.0.36"
PI_PATH="~/"

echo "Copying binary to Raspberry Pi..."
scp target/aarch64-unknown-linux-gnu/debug/jumo_tui $PI_HOST:$PI_PATH || exit 1

echo "Done! Binary copied to Pi"
