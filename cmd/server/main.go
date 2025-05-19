package main

import (
	"log"

	"github.com/gin-gonic/gin"
	"github.com/serviceispcode/mikrotik-backup/internal/config"
	"github.com/serviceispcode/mikrotik-backup/internal/db"
	"github.com/serviceispcode/mikrotik-backup/internal/router"
)

func main() {
	cfg, err := config.LoadConfig()
	if err != nil {
		log.Fatalf("failed to load config: %v", err)
	}

	// Initialize PostgreSQL connection
	pool, err := db.Connect(cfg)
	if err != nil {
		log.Fatalf("failed to connect to database: %v", err)
	}
	defer pool.Close()

	r := gin.Default()
	// You may set DB pool in Gin context if needed
	router.SetupRoutes(r, pool)

	log.Printf("starting server on %s", cfg.Server.Address)
	if err := r.Run(cfg.Server.Address); err != nil {
		log.Fatalf("failed to run server: %v", err)
	}
}
