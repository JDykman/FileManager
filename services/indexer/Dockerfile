# services/indexer/Dockerfile

# --- Stage 1: Build the Rust application ---
FROM rust:1.88.0-slim-bookworm AS builder

RUN apt-get update && apt-get install -y musl-tools \
    && rm -rf /var/lib/apt/lists/*
RUN rustup target add x86_64-unknown-linux-musl

WORKDIR /app

COPY Cargo.toml Cargo.lock ./
COPY services/indexer/Cargo.toml ./services/indexer/Cargo.toml
COPY services/indexer/src ./services/indexer/src

WORKDIR /app/services/indexer

RUN cargo build --release --locked --target x86_64-unknown-linux-musl

# --- Stage 2: Create a minimal runtime image ---
FROM alpine:3.22.1

RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

COPY --from=builder /app/target/x86_64-unknown-linux-musl/release/indexer /usr/local/bin/indexer

COPY supported_extensions.txt /app/supported_extensions.txt

ENTRYPOINT ["/usr/local/bin/indexer"]
CMD ["--extensions-file", "/app/supported_extensions.txt"]