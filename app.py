import uvicorn
import sqlite3
import os
import shutil
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Request, Form, UploadFile, File, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import aiosqlite

# Create app directory structure
os.makedirs("static", exist_ok=True)
os.makedirs("static/uploads", exist_ok=True)
os.makedirs("templates", exist_ok=True)

# Initialize FastAPI
app = FastAPI(title="LinkedIn Content Bank")

# Mount static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

# Setup Jinja2 templates
templates = Jinja2Templates(directory="templates")

# Add now() function to templates
templates.env.globals["now"] = datetime.now

# Database setup
DATABASE_NAME = "content_bank.db"

async def init_db():
    """Initialize the database with required tables"""
    async with aiosqlite.connect(DATABASE_NAME) as db:
        # Create table if it doesn't exist
        await db.execute('''
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
        async with db.execute("PRAGMA table_info(content)") as cursor:
            columns = await cursor.fetchall()
            column_names = [column[1] for column in columns]
            if "cover_image" not in column_names:
                await db.execute("ALTER TABLE content ADD COLUMN cover_image TEXT")
        
        await db.commit()

async def get_db():
    """Database connection dependency"""
    db = await aiosqlite.connect(DATABASE_NAME)
    try:
        yield db
    finally:
        await db.close()

# Helper function to save uploaded file
async def save_upload_file(upload_file: UploadFile) -> str:
    """Save an uploaded file to the uploads directory and return the filename"""
    if not upload_file:
        return None
        
    # Create a unique filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_")
    filename = timestamp + upload_file.filename
    file_path = os.path.join("static/uploads", filename)
    
    # Save the file
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)
    
    return filename

# Models
class ContentBase(BaseModel):
    title: str
    content_type: str
    description: Optional[str] = None
    resources: Optional[str] = None
    cover_image: Optional[str] = None
    status: str = "draft"
    scheduled_for: Optional[datetime] = None

class Content(ContentBase):
    id: int
    created_at: datetime
    posted_at: Optional[datetime] = None

# Routes
@app.get("/", response_class=HTMLResponse)
async def home(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    """Homepage showing the next content to post"""
    # Get the next content that is not posted yet
    async with db.execute(
        "SELECT * FROM content WHERE status != 'posted' ORDER BY scheduled_for ASC LIMIT 1"
    ) as cursor:
        next_content = await cursor.fetchone()
    
    # Get all content for the sidebar
    async with db.execute(
        "SELECT * FROM content ORDER BY scheduled_for ASC"
    ) as cursor:
        all_content = await cursor.fetchall()
    
    column_names = [description[0] for description in cursor.description]
    
    # Format the results as dictionaries
    next_content_dict = None
    if next_content:
        next_content_dict = dict(zip(column_names, next_content))
    
    all_content_list = []
    for content in all_content:
        all_content_list.append(dict(zip(column_names, content)))
    
    return templates.TemplateResponse(
        "index.html", 
        {
            "request": request, 
            "next_content": next_content_dict,
            "all_content": all_content_list
        }
    )

@app.get("/cms", response_class=HTMLResponse)
async def cms(request: Request, db: aiosqlite.Connection = Depends(get_db)):
    """CMS page to manage content"""
    async with db.execute(
        "SELECT * FROM content ORDER BY scheduled_for ASC"
    ) as cursor:
        all_content = await cursor.fetchall()
    
    column_names = [description[0] for description in cursor.description]
    
    # Format the results as dictionaries
    all_content_list = []
    for content in all_content:
        all_content_list.append(dict(zip(column_names, content)))
    
    return templates.TemplateResponse(
        "cms.html", 
        {
            "request": request, 
            "content_list": all_content_list
        }
    )

@app.get("/content/new", response_class=HTMLResponse)
async def new_content_form(request: Request):
    """Form to add new content"""
    return templates.TemplateResponse(
        "content_form.html", 
        {
            "request": request,
            "content": None
        }
    )

@app.post("/content/new")
async def create_content(
    title: str = Form(...),
    content_type: str = Form(...),
    description: str = Form(None),
    resource_file: UploadFile = File(None),
    cover_image_file: UploadFile = File(None),
    scheduled_for: str = Form(None),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Create new content"""
    # Save the uploaded file if present
    resources = None
    if resource_file and resource_file.filename:
        resources = await save_upload_file(resource_file)
    
    # Save the cover image if present
    cover_image = None
    if cover_image_file and cover_image_file.filename:
        cover_image = await save_upload_file(cover_image_file)
    
    query = """
        INSERT INTO content (title, content_type, description, resources, cover_image, scheduled_for)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    await db.execute(
        query, 
        (title, content_type, description, resources, cover_image, scheduled_for)
    )
    await db.commit()
    return RedirectResponse(url="/cms", status_code=303)

@app.get("/content/{content_id}", response_class=HTMLResponse)
async def get_content(
    content_id: int, 
    request: Request, 
    db: aiosqlite.Connection = Depends(get_db)
):
    """View single content details"""
    async with db.execute(
        "SELECT * FROM content WHERE id = ?", 
        (content_id,)
    ) as cursor:
        content = await cursor.fetchone()
        
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    column_names = [description[0] for description in cursor.description]
    content_dict = dict(zip(column_names, content))
    
    return templates.TemplateResponse(
        "content_detail.html", 
        {
            "request": request, 
            "content": content_dict
        }
    )

@app.get("/content/{content_id}/edit", response_class=HTMLResponse)
async def edit_content_form(
    content_id: int,
    request: Request,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Form to edit content"""
    async with db.execute(
        "SELECT * FROM content WHERE id = ?", 
        (content_id,)
    ) as cursor:
        content = await cursor.fetchone()
    
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")
    
    column_names = [description[0] for description in cursor.description]
    content_dict = dict(zip(column_names, content))
    
    return templates.TemplateResponse(
        "content_form.html", 
        {
            "request": request, 
            "content": content_dict
        }
    )

@app.post("/content/{content_id}/edit")
async def update_content(
    content_id: int,
    title: str = Form(...),
    content_type: str = Form(...),
    description: str = Form(None),
    resource_file: UploadFile = File(None),
    cover_image_file: UploadFile = File(None),
    status: str = Form(...),
    scheduled_for: str = Form(None),
    db: aiosqlite.Connection = Depends(get_db)
):
    """Update existing content"""
    # Get the current resources and cover image values
    async with db.execute(
        "SELECT resources, cover_image FROM content WHERE id = ?", 
        (content_id,)
    ) as cursor:
        current_data = await cursor.fetchone()
    
    # Save the uploaded file if present
    resources = current_data[0] if current_data else None
    if resource_file and resource_file.filename:
        resources = await save_upload_file(resource_file)
    
    # Save the cover image if present
    cover_image = current_data[1] if current_data else None
    if cover_image_file and cover_image_file.filename:
        cover_image = await save_upload_file(cover_image_file)
    
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
        await db.execute(
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
        await db.execute(
            query, 
            (title, content_type, description, resources, cover_image, status, scheduled_for, content_id)
        )
    
    await db.commit()
    return RedirectResponse(url="/cms", status_code=303)

@app.post("/content/{content_id}/mark-posted")
async def mark_as_posted(
    content_id: int,
    db: aiosqlite.Connection = Depends(get_db)
):
    """Mark content as posted"""
    posted_at = datetime.now().isoformat()
    await db.execute(
        "UPDATE content SET status = 'posted', posted_at = ? WHERE id = ?",
        (posted_at, content_id)
    )
    await db.commit()
    return RedirectResponse(url="/", status_code=303)

@app.on_event("startup")
async def startup_event():
    """Run database initialization on startup"""
    await init_db()

# Run the application
if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True) 