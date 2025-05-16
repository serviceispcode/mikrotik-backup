"""Backup management routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request, send_file
from flask_login import login_required
from models import Device, Backup, Log, db
from services.backup_service import BackupService
import os

backups_bp = Blueprint('backups', __name__)

@backups_bp.route('/devices/<int:device_id>/backups')
@login_required
def list_backups(device_id):
    """List backups for a specific device."""
    device = Device.query.get_or_404(device_id)
    backups = Backup.query.filter_by(device_id=device_id).order_by(Backup.created_at.desc()).all()
    return render_template('backups/list.html', device=device, backups=backups)

@backups_bp.route('/devices/<int:device_id>/backup', methods=['POST'])
@login_required
def create_backup(device_id):
    """Create a backup for a specific device."""
    device = Device.query.get_or_404(device_id)
    
    backup = BackupService.create_backup(device_id)
    
    if backup and backup.status == 'success':
        flash(f'Backup for {device.name} created successfully', 'success')
    else:
        flash(f'Backup for {device.name} failed', 'danger')
        
    return redirect(url_for('backups.list_backups', device_id=device_id))

@backups_bp.route('/backups/<int:backup_id>/download')
@login_required
def download_backup(backup_id):
    """Download a backup file."""
    backup = Backup.query.get_or_404(backup_id)
    
    if backup.status != 'success' or not os.path.exists(backup.file_path):
        flash('Backup file not found', 'danger')
        return redirect(url_for('backups.list_backups', device_id=backup.device_id))
        
    return send_file(
        backup.file_path,
        as_attachment=True,
        download_name=backup.filename
    )

@backups_bp.route('/logs')
@login_required
def list_logs():
    """List all logs."""
    logs = Log.query.order_by(Log.created_at.desc()).limit(100).all()
    return render_template('logs.html', logs=logs)

# ========== app.py ==========
"""Main Flask application."""
from flask import Flask, redirect, url_for
from flask_login import LoginManager, current_user
from models import db, User
from config import Config
from routes.auth import auth_bp
from routes.devices import devices_bp, scheduler
from routes.backups import backups_bp
from services.scheduler import BackupScheduler

def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Initialize login manager
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)
    
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))
    
    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(devices_bp)
    app.register_blueprint(backups_bp)
    
    # Main route
    @app.route('/')
    def index():
        if current_user.is_authenticated:
            return redirect(url_for('dashboard'))
        return redirect(url_for('auth.login'))
    
    @app.route('/dashboard')
    def dashboard():
        if not current_user.is_authenticated:
            return redirect(url_for('auth.login'))
        return render_template('dashboard.html')
    
    # Create tables and initialize scheduler
    with app.app_context():
        db.create_all()
        
        # Create default admin user if no users exist
        if not User.query.first():
            admin = User(username='admin')
            admin.set_password('admin')  # Change this in production!
            db.session.add(admin)
            db.session.commit()
        
        # Initialize scheduler
        global scheduler
        scheduler = BackupScheduler()
    
    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)