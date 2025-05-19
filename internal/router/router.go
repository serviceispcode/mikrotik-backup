package router

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/serviceispcode/mikrotik-backup/internal/handlers"
	"github.com/serviceispcode/mikrotik-backup/internal/repo"
)

// SetupRoutes registers all HTTP routes on the given engine with DB pool
func SetupRoutes(r *gin.Engine, pool *pgxpool.Pool) {
	api := r.Group("/api")
	{
		api.GET("/health", health)
		// Device CRUD endpoints
		deviceRepo := repo.NewDeviceRepository(pool)
		deviceHandler := handlers.NewDeviceHandler(deviceRepo)
		api.POST("/devices", deviceHandler.Create)
		api.GET("/devices", deviceHandler.List)
		api.GET("/devices/:id", deviceHandler.Get)
		api.PUT("/devices/:id", deviceHandler.Update)
		api.DELETE("/devices/:id", deviceHandler.Delete)
	}
}

func health(c *gin.Context) {
	c.JSON(http.StatusOK, gin.H{"status": "ok"})
}
