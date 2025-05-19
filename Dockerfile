# Build stage
FROM golang:1.24-alpine AS builder

WORKDIR /app
COPY go.mod ./
RUN go mod download

COPY . .
RUN go build -o mikrotik-backup ./cmd/server

# Run stage
FROM alpine:latest
WORKDIR /app

COPY --from=builder /app/mikrotik-backup .
EXPOSE 8080
ENTRYPOINT ["./mikrotik-backup"] 