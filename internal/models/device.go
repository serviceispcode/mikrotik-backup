package models

import "time"

// Device represents a MikroTik device configuration backup target
// and maps to the devices table.
type Device struct {
	ID          int       `json:"id"`
	Name        string    `json:"name"`
	IPAddress   string    `json:"ip_address"`
	Description *string   `json:"description,omitempty"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
}
