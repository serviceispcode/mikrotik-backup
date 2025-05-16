"""Database models for the application."""
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()

class User(UserMixin, db.Model):
    """User model for authentication."""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    
    def set_password(self, password):
        """Set the password hash."""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check the password against the hash."""
        return check_password_hash(self.password_hash, password)

class Device(db.Model):
    """Device model for Mikrotik routers."""
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    host = db.Column(db.String(128), nullable=False)
    username = db.Column(db.String(64), nullable=False)
    password = db.Column(db.String(128), nullable=False)  # Should be encrypted in production
    port = db.Column(db.Integer, default=8728)  # Default API port
    connection_type = db.Column(db.String(16), default='api')  # 'api' or 'ssh'
    schedule_type = db.Column(db.String(16), default='none')  # 'none', 'daily', 'weekly'
    schedule_hour = db.Column(db.Integer, default=0)
    schedule_minute = db.Column(db.Integer, default=0)
    schedule_day = db.Column(db.Integer, default=0)  # 0=Monday for weekly schedule
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship with backups
    backups = db.relationship('Backup', backref='device', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Device {self.name}>'

class Backup(db.Model):
    """Backup model for storing backup metadata."""
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    filename = db.Column(db.String(128), nullable=False)
    file_path = db.Column(db.String(256), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(16), nullable=False)  # 'success', 'failed'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Backup {self.filename}>'

class Log(db.Model):
    """Log model for storing operation logs."""
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=True)
    message = db.Column(db.Text, nullable=False)
    level = db.Column(db.String(16), default='info')  # 'info', 'warning', 'error'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Optional relationship with device
    device = db.relationship('Device', backref='logs')
    
    def __repr__(self):
        return f'<Log {self.id}: {self.level}>'