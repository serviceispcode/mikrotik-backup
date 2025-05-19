package repo

import (
	"context"
	"fmt"
	"time"

	"github.com/jackc/pgx/v4/pgxpool"
	"github.com/serviceispcode/mikrotik-backup/internal/models"
)

// DeviceRepository provides CRUD operations for Device entities.
type DeviceRepository struct {
	db *pgxpool.Pool
}

// NewDeviceRepository creates a new DeviceRepository.
func NewDeviceRepository(pool *pgxpool.Pool) *DeviceRepository {
	return &DeviceRepository{db: pool}
}

// Create inserts a new device and sets its ID, CreatedAt, and UpdatedAt.
func (r *DeviceRepository) Create(ctx context.Context, d *models.Device) error {
	query := `INSERT INTO devices (name, ip_address, description)
              VALUES ($1, $2, $3)
              RETURNING id, created_at, updated_at`
	return r.db.QueryRow(ctx, query, d.Name, d.IPAddress, d.Description).
		Scan(&d.ID, &d.CreatedAt, &d.UpdatedAt)
}

// GetByID retrieves a device by its ID.
func (r *DeviceRepository) GetByID(ctx context.Context, id int) (*models.Device, error) {
	query := `SELECT id, name, ip_address, description, created_at, updated_at
              FROM devices WHERE id = $1`
	var d models.Device
	err := r.db.QueryRow(ctx, query, id).
		Scan(&d.ID, &d.Name, &d.IPAddress, &d.Description, &d.CreatedAt, &d.UpdatedAt)
	if err != nil {
		return nil, err
	}
	return &d, nil
}

// List retrieves all devices.
func (r *DeviceRepository) List(ctx context.Context) ([]models.Device, error) {
	query := `SELECT id, name, ip_address, description, created_at, updated_at
              FROM devices`
	rows, err := r.db.Query(ctx, query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var list []models.Device
	for rows.Next() {
		var d models.Device
		if err := rows.Scan(&d.ID, &d.Name, &d.IPAddress, &d.Description, &d.CreatedAt, &d.UpdatedAt); err != nil {
			return nil, err
		}
		list = append(list, d)
	}
	return list, rows.Err()
}

// Update modifies an existing device by ID.
func (r *DeviceRepository) Update(ctx context.Context, d *models.Device) error {
	d.UpdatedAt = time.Now()
	query := `UPDATE devices
              SET name = $1, ip_address = $2, description = $3, updated_at = $4
              WHERE id = $5`
	tag, err := r.db.Exec(ctx, query, d.Name, d.IPAddress, d.Description, d.UpdatedAt, d.ID)
	if err != nil {
		return err
	}
	if tag.RowsAffected() != 1 {
		return fmt.Errorf("device not found or not updated")
	}
	return nil
}

// Delete removes a device by its ID.
func (r *DeviceRepository) Delete(ctx context.Context, id int) error {
	tag, err := r.db.Exec(ctx, `DELETE FROM devices WHERE id = $1`, id)
	if err != nil {
		return err
	}
	if tag.RowsAffected() != 1 {
		return fmt.Errorf("device not found or not deleted")
	}
	return nil
}
