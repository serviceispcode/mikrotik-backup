"""Scheduler for automated backups."""
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from models import Device
from services.backup_service import BackupService

class BackupScheduler:
    """Scheduler for automated backups."""
    
    def __init__(self):
        """Initialize the scheduler."""
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        self.reload_jobs()
    
    def reload_jobs(self):
        """Clear all jobs and reload them from the database."""
        self.scheduler.remove_all_jobs()
        
        # Get all devices with schedules
        devices = Device.query.filter(Device.schedule_type != 'none').all()
        
        for device in devices:
            self.add_device_job(device)
    
    def add_device_job(self, device):
        """
        Add a backup job for a device.
        
        Args:
            device: Device object
        """
        if device.schedule_type == 'none':
            return
            
        job_id = f"backup_{device.id}"
        
        if device.schedule_type == 'daily':
            trigger = CronTrigger(
                hour=device.schedule_hour,
                minute=device.schedule_minute
            )
        elif device.schedule_type == 'weekly':
            trigger = CronTrigger(
                day_of_week=device.schedule_day,
                hour=device.schedule_hour,
                minute=device.schedule_minute
            )
        else:
            return
            
        self.scheduler.add_job(
            BackupService.create_backup,
            trigger=trigger,
            id=job_id,
            replace_existing=True,
            args=[device.id]
        )
    
    def update_device_job(self, device):
        """
        Update a device's backup job.
        
        Args:
            device: Device object
        """
        # Remove existing job
        job_id = f"backup_{device.id}"
        try:
            self.scheduler.remove_job(job_id)
        except:
            pass
            
        # Add new job if scheduled
        if device.schedule_type != 'none':
            self.add_device_job(device)
    
    def remove_device_job(self, device_id):
        """
        Remove a device's backup job.
        
        Args:
            device_id: Device ID
        """
        job_id = f"backup_{device_id}"
        try:
            self.scheduler.remove_job(job_id)
        except:
            pass