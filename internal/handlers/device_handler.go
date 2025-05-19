package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/jackc/pgx/v4"
	"github.com/serviceispcode/mikrotik-backup/internal/models"
	"github.com/serviceispcode/mikrotik-backup/internal/repo"
)

// DeviceHandler handles HTTP requests for devices.
type DeviceHandler struct {
	repo *repo.DeviceRepository
}

// NewDeviceHandler constructs a new DeviceHandler.
func NewDeviceHandler(r *repo.DeviceRepository) *DeviceHandler {
	return &DeviceHandler{repo: r}
}

// Create handles POST /devices
func (h *DeviceHandler) Create(c *gin.Context) {
	var d models.Device
	if err := c.ShouldBindJSON(&d); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	if err := h.repo.Create(c.Request.Context(), &d); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusCreated, d)
}

// List handles GET /devices
func (h *DeviceHandler) List(c *gin.Context) {
	devices, err := h.repo.List(c.Request.Context())
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, devices)
}

// Get handles GET /devices/:id
func (h *DeviceHandler) Get(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}
	d, err := h.repo.GetByID(c.Request.Context(), id)
	if err != nil {
		if err == pgx.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "device not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}
	c.JSON(http.StatusOK, d)
}

// Update handles PUT /devices/:id
func (h *DeviceHandler) Update(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}
	var d models.Device
	if err := c.ShouldBindJSON(&d); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	d.ID = id
	if err := h.repo.Update(c.Request.Context(), &d); err != nil {
		if err.Error() == "device not found or not updated" {
			c.JSON(http.StatusNotFound, gin.H{"error": "device not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}
	c.JSON(http.StatusOK, d)
}

// Delete handles DELETE /devices/:id
func (h *DeviceHandler) Delete(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "invalid id"})
		return
	}
	if err := h.repo.Delete(c.Request.Context(), id); err != nil {
		if err.Error() == "device not found or not deleted" {
			c.JSON(http.StatusNotFound, gin.H{"error": "device not found"})
		} else {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		}
		return
	}
	c.Status(http.StatusNoContent)
}
