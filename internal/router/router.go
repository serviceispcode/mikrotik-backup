package router

import (
    "net/http"

    "github.com/gin-gonic/gin"
)

func SetupRoutes(r *gin.Engine) {
    api := r.Group("/api")
    {
        api.GET("/health", health)
    }
}

func health(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{"status": "ok"})
} 