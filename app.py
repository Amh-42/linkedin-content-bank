import os
import shutil
import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, flash, abort, send_from_directory
from werkzeug.utils import secure_filename
from flask_bootstrap import Bootstrap

# Create app directory structure
os.makedirs("static", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Initialize Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'linkedin-content-bank-secret-key'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max upload
app.config['UPLOAD_FOLDER'] = 'static/uploads'

# Initialize Bootstrap
bootstrap = Bootstrap(app)

# Database setup
DATABASE_NAME = "content_bank.db"

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    
    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS content (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content_type TEXT NOT NULL,
        description TEXT,
        resources TEXT,
        cover_image TEXT,
        status TEXT DEFAULT 'draft',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        scheduled_for TIMESTAMP,
        posted_at TIMESTAMP
    )
    ''')
    
    # Check if cover_image column exists, add it if it doesn't
    cursor.execute("PRAGMA table_info(content)")
    columns = cursor.fetchall()
    column_names = [column[1] for column in columns]
    if "cover_image" not in column_names:
        cursor.execute("ALTER TABLE content ADD COLUMN cover_image TEXT")
    
    conn.commit()
    conn.close()

def get_db():
    """Get database connection"""
    conn = sqlite3.connect(DATABASE_NAME)
    conn.row_factory = sqlite3.Row  # This enables column access by name
    return conn

def save_upload_file(file):
    """Save an uploaded file to the uploads directory and return the filename"""
    if not file or file.filename == '':
        return None
    
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
    filename = timestamp + secure_filename(file.filename)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    
    # Save the file
    file.save(file_path)
    return filename

# Add datetime filter for Jinja templates
@app.template_filter('datetime')
def format_datetime(value, format="%Y-%m-%d %H:%M"):
    if value is None:
        return ""
    if isinstance(value, str):
        try:
            value = datetime.fromisoformat(value.replace('Z', '+00:00'))
        except ValueError:
            return value
    return value.strftime(format)

# Make datetime.now available to templates
@app.context_processor
def inject_now():
    return {'now': datetime.now}

# Routes
@app.route('/')
def home():
    """Homepage showing the next content to post"""
    db = get_db()
    cursor = db.cursor()
    
    # Get the next content that is not posted yet
    cursor.execute(
        "SELECT * FROM content WHERE status != 'posted' ORDER BY scheduled_for ASC LIMIT 1"
    )
    next_content = cursor.fetchone()
    
    # Get all content for the sidebar
    cursor.execute(
        "SELECT * FROM content ORDER BY scheduled_for ASC"
    )
    all_content = cursor.fetchall()
    
    db.close()
    return render_template(
        "index.html", 
        next_content=next_content,
        all_content=all_content
    )

@app.route('/cms')
def cms():
    """CMS page to manage content"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute(
        "SELECT * FROM content ORDER BY scheduled_for ASC"
    )
    all_content = cursor.fetchall()
    
    db.close()
    return render_template(
        "cms.html", 
        content_list=all_content
    )

@app.route('/content/new', methods=['GET', 'POST'])
def new_content():
    """Form to add new content"""
    if request.method == 'POST':
        title = request.form.get('title')
        content_type = request.form.get('content_type')
        description = request.form.get('description')
        scheduled_for = request.form.get('scheduled_for')
        
        # Handle file uploads
        resource_file = request.files.get('resource_file')
        cover_image_file = request.files.get('cover_image_file')
        
        # Save the uploaded files if present
        resources = save_upload_file(resource_file) if resource_file else None
        cover_image = save_upload_file(cover_image_file) if cover_image_file else None
        
        # Insert into database
        db = get_db()
        cursor = db.cursor()
        
        query = """
            INSERT INTO content (title, content_type, description, resources, cover_image, scheduled_for)
            VALUES (?, ?, ?, ?, ?, ?)
        """
        cursor.execute(
            query, 
            (title, content_type, description, resources, cover_image, scheduled_for)
        )
        db.commit()
        db.close()
        
        return redirect(url_for('cms'))
    
    return render_template(
        "content_form.html", 
        content=None
    )

@app.route('/content/<int:content_id>')
def get_content(content_id):
    """View single content details"""
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute(
        "SELECT * FROM content WHERE id = ?", 
        (content_id,)
    )
    content = cursor.fetchone()
    
    db.close()
    
    if not content:
        abort(404)
    
    return render_template(
        "content_detail.html", 
        content=content
    )

@app.route('/content/<int:content_id>/edit', methods=['GET', 'POST'])
def edit_content(content_id):
    """Form to edit content"""
    db = get_db()
    cursor = db.cursor()
    
    if request.method == 'POST':
        title = request.form.get('title')
        content_type = request.form.get('content_type')
        description = request.form.get('description')
        status = request.form.get('status')
        scheduled_for = request.form.get('scheduled_for')
        
        # Get current resources value
        cursor.execute(
            "SELECT resources, cover_image FROM content WHERE id = ?", 
            (content_id,)
        )
        current_data = cursor.fetchone()
        
        # Handle file uploads
        resource_file = request.files.get('resource_file')
        cover_image_file = request.files.get('cover_image_file')
        
        # Save the uploaded files if present
        resources = current_data['resources'] if current_data else None
        if resource_file and resource_file.filename:
            resources = save_upload_file(resource_file)
            
        cover_image = current_data['cover_image'] if current_data else None
        if cover_image_file and cover_image_file.filename:
            cover_image = save_upload_file(cover_image_file)
        
        # If marked as posted, set posted_at timestamp
        posted_at = None
        if status == "posted":
            posted_at = datetime.now().isoformat()
            query = """
                UPDATE content 
                SET title = ?, content_type = ?, description = ?, 
                    resources = ?, cover_image = ?, status = ?, scheduled_for = ?, posted_at = ?
                WHERE id = ?
            """
            cursor.execute(
                query, 
                (title, content_type, description, resources, cover_image, status, scheduled_for, posted_at, content_id)
            )
        else:
            query = """
                UPDATE content 
                SET title = ?, content_type = ?, description = ?, 
                    resources = ?, cover_image = ?, status = ?, scheduled_for = ?
                WHERE id = ?
            """
            cursor.execute(
                query, 
                (title, content_type, description, resources, cover_image, status, scheduled_for, content_id)
            )
        
        db.commit()
        db.close()
        
        return redirect(url_for('cms'))
    
    # GET request - show edit form
    cursor.execute(
        "SELECT * FROM content WHERE id = ?", 
        (content_id,)
    )
    content = cursor.fetchone()
    
    db.close()
    
    if not content:
        abort(404)
    
    return render_template(
        "content_form.html", 
        content=content
    )

@app.route('/content/<int:content_id>/mark-posted', methods=['POST'])
def mark_as_posted(content_id):
    """Mark content as posted"""
    posted_at = datetime.now().isoformat()
    
    db = get_db()
    cursor = db.cursor()
    
    cursor.execute(
        "UPDATE content SET status = 'posted', posted_at = ? WHERE id = ?",
        (posted_at, content_id)
    )
    db.commit()
    db.close()
    
    return redirect(url_for('home'))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500

# Run the application
if __name__ == "__main__":
    # Initialize the database
    init_db()
    # Run the Flask app
    app.run(host="0.0.0.0", port=8000, debug=True) 