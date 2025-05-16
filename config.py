"""Configuration settings for the application."""
import os

class Config:
    # Flask configuration
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-should-change-this-in-production'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///mikrotik_backup.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Backup storage configuration
    BACKUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backups')
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)