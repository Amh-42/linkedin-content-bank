# Deploying LinkedIn Content Bank on cPanel

## Prerequisites
- cPanel hosting account with Python support
- SSH access (recommended)
- Git (optional)

## Deployment Steps

### 1. Upload Files to cPanel

**Option A: Using File Manager**
1. Log in to your cPanel account
2. Go to File Manager
3. Navigate to your domain's public_html directory (or a subdirectory if you want to deploy to a subfolder)
4. Upload all project files, preserving the directory structure

**Option B: Using Git (recommended)**
1. Log in to your server via SSH
2. Navigate to your domain's public_html directory
3. Clone your repository:
   ```
   git clone https://github.com/Amh-42/linkedin-content-bank.git .
   ```

### 2. Set Up Python Environment

1. In cPanel, go to "Setup Python App"
2. Create a new Python application:
   - Python version: 3.8+ (3.10 recommended)
   - Application root: your domain or subdomain path
   - Application URL: your domain or subdomain
   - Application startup file: passenger_wsgi.py
3. Create a virtual environment

### 3. Install Requirements

Via SSH (recommended):
```
cd ~/public_html  # or your application directory
source venv/bin/activate  # activate the virtual environment
pip install -r requirements.txt
```

### 4. Set Up Database and Static Files

1. Ensure the database file (content_bank.db) is in the application directory and has proper permissions:
   ```
   chmod 666 content_bank.db
   ```

2. Create upload directories with proper permissions:
   ```
   mkdir -p static/uploads
   chmod -R 755 static
   ```

### 5. Configure Application

1. Make sure passenger_wsgi.py is properly set up (already included in the repository)
2. Make sure .htaccess is properly set up (already included in the repository)

### 6. Restart Python Application

1. In cPanel, go to "Setup Python App"
2. Select your application
3. Click "Restart" to apply changes

### 7. Troubleshooting

Check the error logs if you encounter issues:
1. In cPanel, go to "Error Log"
2. Look for any Python or application-related errors

Common issues:
- Permissions: Make sure directories and files have proper permissions
- Virtual environment: Ensure requirements are installed in the correct environment
- Database: Check if SQLite database has write permissions

### 8. Updating the Application

To update your application after deployment:

**Using Git:**
```
cd ~/public_html  # or your application directory
git pull
```

Then restart the Python application in cPanel. 