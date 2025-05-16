"""
# Mikrotik Backup System

A Flask-based web application for managing Mikrotik device backups.

## Features

- User authentication
- Device management (add, edit, delete Mikrotik devices)
- Manual and scheduled backups
- Backup file downloads
- System logs

## Installation

1. Clone the repository:
```
git clone https://github.com/serviceispcode/mikrotik-backup.git
cd mikrotik-backup
```

2. Create a virtual environment:
```
python -m venv venv
source venv/bin/activate  
```

3. Install dependencies:
```
pip install flask flask-sqlalchemy flask-login apscheduler routeros-api werkzeug
```

4. Run the application:
```
python app.py
```

5. Access the application at http://localhost:5000

## Default Login

- Username: admin
- Password: admin

**Important:** Change the default password after the first login.

## Configuration

Edit `config.py` to customize the application settings:

- `SECRET_KEY`: Set a strong secret key for production
- `SQLALCHEMY_DATABASE_URI`: Database connection string
- `BACKUP_DIR`: Directory to store backup files

## Production Deployment

For production deployment, consider:

1. Using a production WSGI server like Gunicorn or uWSGI
2. Setting up a reverse proxy with Nginx or Apache
3. Using a production-grade database like PostgreSQL
4. Setting environment variables for sensitive configuration

## License

[MIT License](LICENSE)
"""
