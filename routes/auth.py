"""Authentication routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from models import User, db

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user is None or not user.check_password(password):
            flash('Invalid username or password', 'danger')
            return render_template('login.html')
            
        login_user(user)
        next_page = request.args.get('next')
        
        if not next_page or not next_page.startswith('/'):
            next_page = url_for('main.dashboard')
            
        return redirect(next_page)
        
    return render_template('login.html')

@auth_bp.route('/logout')
@login_required
def logout():
    """Handle user logout."""
    logout_user()
    return redirect(url_for('auth.login'))

# ========== routes/devices.py ==========
"""Device management routes."""
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required
from models import Device, db
from services.scheduler import BackupScheduler

devices_bp = Blueprint('devices', __name__)
scheduler = None

@devices_bp.route('/devices')
@login_required
def list_devices():
    """List all devices."""
    devices = Device.query.all()
    return render_template('devices/list.html', devices=devices)

@devices_bp.route('/devices/add', methods=['GET', 'POST'])
@login_required
def add_device():
    """Add a new device."""
    if request.method == 'POST':
        # Get form data
        name = request.form.get('name')
        host = request.form.get('host')
        username = request.form.get('username')
        password = request.form.get('password')
        port = request.form.get('port', type=int, default=8728)
        connection_type = request.form.get('connection_type', 'api')
        schedule_type = request.form.get('schedule_type', 'none')
        schedule_hour = request.form.get('schedule_hour', type=int, default=0)
        schedule_minute = request.form.get('schedule_minute', type=int, default=0)
        schedule_day = request.form.get('schedule_day', type=int, default=0)
        
        # Validate required fields
        if not name or not host or not username or not password:
            flash('All fields are required', 'danger')
            return render_template('devices/add.html')
        
        # Create new device
        device = Device(
            name=name,
            host=host,
            username=username,
            password=password,  # Should be encrypted in production
            port=port,
            connection_type=connection_type,
            schedule_type=schedule_type,
            schedule_hour=schedule_hour,
            schedule_minute=schedule_minute,
            schedule_day=schedule_day
        )
        
        db.session.add(device)
        db.session.commit()
        
        # Add device to scheduler if needed
        global scheduler
        if scheduler and schedule_type != 'none':
            scheduler.add_device_job(device)
            
        flash(f'Device {name} added successfully', 'success')
        return redirect(url_for('devices.list_devices'))
        
    return render_template('devices/add.html')

@devices_bp.route('/devices/<int:device_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_device(device_id):
    """Edit an existing device."""
    device = Device.query.get_or_404(device_id)
    
    if request.method == 'POST':
        # Get form data
        device.name = request.form.get('name')
        device.host = request.form.get('host')
        device.username = request.form.get('username')
        
        # Only update password if provided
        new_password = request.form.get('password')
        if new_password:
            device.password = new_password  # Should be encrypted in production
            
        device.port = request.form.get('port', type=int, default=8728)
        device.connection_type = request.form.get('connection_type', 'api')
        device.schedule_type = request.form.get('schedule_type', 'none')
        device.schedule_hour = request.form.get('schedule_hour', type=int, default=0)
        device.schedule_minute = request.form.get('schedule_minute', type=int, default=0)
        device.schedule_day = request.form.get('schedule_day', type=int, default=0)
        
        db.session.commit()
        
        # Update scheduler
        global scheduler
        if scheduler:
            scheduler.update_device_job(device)
            
        flash(f'Device {device.name} updated successfully', 'success')
        return redirect(url_for('devices.list_devices'))
        
    return render_template('devices/edit.html', device=device)

@devices_bp.route('/devices/<int:device_id>/delete', methods=['POST'])
@login_required
def delete_device(device_id):
    """Delete a device."""
    device = Device.query.get_or_404(device_id)
    
    # Remove from scheduler
    global scheduler
    if scheduler:
        scheduler.remove_device_job(device_id)
    
    db.session.delete(device)
    db.session.commit()
    
    flash(f'Device {device.name} deleted successfully', 'success')
    return redirect(url_for('devices.list_devices'))