# Deploying LinkedIn Content Bank on cPanel

This guide explains how to deploy the LinkedIn Content Bank application on a cPanel hosting account.

## Prerequisites

- A cPanel hosting account with Python support
- Python 3.7+ enabled in your cPanel
- SSH access (recommended but not required)

## Setup Steps

### 1. Create a Python Application in cPanel

1. Log in to your cPanel account
2. Navigate to "Setup Python App" or "Python" under the "Software" section
3. Click "Create Application"
4. Configure the application:
   - Application root: Choose the directory where you want to deploy (e.g., `linkedin-content-bank`)
   - Application URL: Set the URL path (e.g., `/content-bank`)
   - Python version: Select Python 3.7 or higher
   - Application startup file: `passenger_wsgi.py`
   - Application Entry point: `application`
5. Click "Create"

### 2. Upload Your Files

Method 1: Using File Manager
1. In cPanel, open File Manager
2. Navigate to the application directory you specified
3. Upload all files from your local project

Method 2: Using FTP/SFTP
1. Use an FTP client like FileZilla
2. Connect to your cPanel server
3. Upload all files to the application directory

### 3. Install Dependencies

1. In cPanel, go to "Terminal" or use SSH to connect to your server
2. Navigate to your application directory
3. Create and activate a virtual environment:
   ```bash
   cd ~/your_application_directory
   python -m venv venv
   source venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### 4. Configure the Application

1. Set up database directory permissions:
   ```bash
   chmod 755 ~/your_application_directory
   touch ~/your_application_directory/content_bank.db
   chmod 664 ~/your_application_directory/content_bank.db
   ```

2. Create the uploads directory:
   ```bash
   mkdir -p ~/your_application_directory/static/uploads
   chmod 755 ~/your_application_directory/static/uploads
   ```

### 5. Create WSGI Configuration

The `passenger_wsgi.py` file should already be in place from your upload. This file helps Passenger (the cPanel middleware) communicate with your FastAPI application.

### 6. Restart the Application

In cPanel, go back to the Python App interface and click "Restart" for your application.

### 7. Access Your Application

Visit your application URL: `https://yourdomain.com/content-bank` (or whatever URL path you configured)

## Troubleshooting

### Application Shows 500 Error
- Check the error logs in cPanel → Logs → Error Log
- Ensure all dependencies are installed correctly
- Verify that file permissions are set properly

### Static Files Not Loading
- Make sure the static folder has correct permissions
- Check that URLs in templates correctly point to `/static/` paths

### Database Issues
- Ensure the database file has proper permissions (664)
- Check that the application has write permissions to the directory

## Maintenance

### Updating the Application
1. Backup your database: `cp content_bank.db content_bank.db.backup`
2. Upload the new files
3. Restart the application in cPanel

### Backing Up
Regularly backup your `content_bank.db` file and the `/static/uploads` directory, as these contain all your data and uploaded files. 