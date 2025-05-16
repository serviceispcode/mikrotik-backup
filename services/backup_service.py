"""Service for handling Mikrotik device backups."""
import os
import time
import routeros_api
from datetime import datetime
from werkzeug.utils import secure_filename
from models import db, Device, Backup, Log
from config import Config

class BackupService:
    """Service for handling Mikrotik device backups."""
    
    @staticmethod
    def create_backup(device_id):
        """
        Create a backup for a specific device.
        
        Args:
            device_id: The ID of the device to backup
            
        Returns:
            Backup object if successful, None if failed
        """
        device = Device.query.get(device_id)
        if not device:
            BackupService._log(None, f"Device with ID {device_id} not found", "error")
            return None
        
        # Log the backup attempt
        BackupService._log(device.id, f"Starting backup for {device.name}", "info")
        
        try:
            # Connect to the device
            if device.connection_type == 'api':
                backup_file = BackupService._backup_via_api(device)
            else:
                backup_file = BackupService._backup_via_ssh(device)
                
            if not backup_file:
                BackupService._log(device.id, f"Backup failed for {device.name}", "error")
                return None
                
            # Create backup record
            file_size = os.path.getsize(backup_file['path'])
            backup = Backup(
                device_id=device.id,
                filename=backup_file['filename'],
                file_path=backup_file['path'],
                file_size=file_size,
                status='success'
            )
            
            db.session.add(backup)
            db.session.commit()
            
            BackupService._log(device.id, f"Backup completed successfully for {device.name}", "info")
            return backup
            
        except Exception as e:
            BackupService._log(device.id, f"Backup failed for {device.name}: {str(e)}", "error")
            # Create failed backup record
            backup = Backup(
                device_id=device.id,
                filename=f"failed_{device.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.backup",
                file_path="",
                status='failed'
            )
            db.session.add(backup)
            db.session.commit()
            return None
    
    @staticmethod
    def _backup_via_api(device):
        """
        Create a backup using the RouterOS API.
        
        Args:
            device: Device object
            
        Returns:
            Dict with 'filename' and 'path' if successful, None if failed
        """
        try:
            # Connect to the router using routeros_api
            connection = routeros_api.RouterOsApiPool(
                device.host,
                username=device.username,
                password=device.password,
                port=device.port
            )
            api = connection.get_api()
            
            # Generate backup filename
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_filename = f"{device.name}_{timestamp}.backup"
            secure_name = secure_filename(backup_filename)
            
            # Execute backup command on the router
            api.get_binary_resource('/system/backup/save').call(
                name=backup_filename
            )
            
            # Give the router a moment to create the backup
            time.sleep(2)
            
            # Get the backup file from the router
            # Note: This is simplified - in a real implementation, you would need to
            # download the file using FTP/SFTP or another method as the API doesn't
            # directly support file downloads
            
            # For demonstration purposes, we'll create an empty file locally
            device_backup_dir = os.path.join(Config.BACKUP_DIR, str(device.id))
            os.makedirs(device_backup_dir, exist_ok=True)
            
            file_path = os.path.join(device_backup_dir, secure_name)
            
            # In a real implementation, you would download the file here
            # Simulating a file for demonstration:
            with open(file_path, 'wb') as f:
                f.write(b'Sample backup content')  # Placeholder for actual backup content
            
            connection.disconnect()
            
            return {
                'filename': secure_name,
                'path': file_path
            }
            
        except Exception as e:
            BackupService._log(device.id, f"API backup failed: {str(e)}", "error")
            return None
    
    @staticmethod
    def _backup_via_ssh(device):
        """
        Create a backup using SSH.
        
        Args:
            device: Device object
            
        Returns:
            Dict with 'filename' and 'path' if successful, None if failed
        """
        # In a real implementation, you would use paramiko to connect via SSH
        # and execute backup commands
        
        # This is a placeholder for demonstration
        BackupService._log(device.id, "SSH backup not implemented in this demo", "warning")
        return None
    
    @staticmethod
    def _log(device_id, message, level="info"):
        """
        Add a log entry.
        
        Args:
            device_id: Device ID or None
            message: Log message
            level: Log level (info, warning, error)
        """
        log = Log(device_id=device_id, message=message, level=level)
        db.session.add(log)
        db.session.commit()