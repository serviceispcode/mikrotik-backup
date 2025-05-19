# Mikrotik Backup

A network backup system for MikroTik devices built with Go and Gin.

## Features

- Device discovery & inventory
- Scheduled backups via API/CLI
- Secure credential management
- Versioning & diffs
- Multi-storage support
- Notification & alerts

## Stack

- Go + Gin
- PostgreSQL
- Redis
- MinIO
- RabbitMQ
- Docker & Docker Compose

## Getting Started

### Prerequisites

- Go 1.20+
- Docker & Docker Compose

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/serviceispcode/mikrotik-backup.git
   cd mikrotik-backup
   ```

2. Copy the example configuration and adjust as needed:
   ```bash
   cp config.example.yaml config.yaml
   ```

3. Build and run with Docker Compose:
   ```bash
   docker-compose up --build
   ```

4. Access health check at [http://localhost:8080/api/health](http://localhost:8080/api/health).

## Configuration

`config.yaml`:
```yaml
server:
  address: ":8080"
```

## Database Migrations

We use [golang-migrate](https://github.com/golang-migrate/migrate) to manage schema versions.

### Install migrate CLI
```bash
# for PostgreSQL support
go install -tags 'postgres' github.com/golang-migrate/migrate/v4/cmd/migrate@latest
```

### Run migrations
```bash
# From project root
docker-compose up -d postgres
migrate -path migrations -database "postgresql://user:pass@localhost:5432/mikrotik_backup?sslmode=disable" up
```

### Rollback
```bash
migrate -path migrations -database "..." down 1
``` 