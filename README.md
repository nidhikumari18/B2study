# B2Study - School Study Platform

## Modern, Production-Ready Flask Application for Educational Content Management

### Features

✅ **Secure Authentication**: Student and admin login with hashed passwords  
✅ **Dashboard**: Personalized learning hub with notices, materials, and stats  
✅ **Content Management**: Upload and organize syllabuses, notes, materials, and PYQs  
✅ **Search & Filter**: Find notes by subject, year, and exam type  
✅ **Notice Board**: Dynamic announcements with expiration dates  
✅ **Export Functionality**: Download student data and login logs as CSV/Excel  
✅ **Download Tracking**: Track all file downloads for analytics  
✅ **Admin Panel**: Comprehensive admin dashboard with user management  
✅ **Responsive UI**: Modern, aesthetic design with Bootstrap 5  
✅ **Social Links**: Footer with Instagram, LinkedIn, GitHub, Twitter links  
✅ **Production Ready**: Modular code, error handling, security best practices  

### Project Structure

```
B2Study/
├── app.py                    # Main Flask application
├── config.py                 # Configuration management
├── models.py                 # Database models
├── wsgi.py                   # WSGI entry point
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── utils/
│   ├── __init__.py
│   ├── export_utils.py      # Export functionality
│   └── file_utils.py        # File handling
├── templates/
│   ├── base.html            # Base template
│   ├── login.html           # Login page
│   ├── signup.html          # Registration page
│   ├── dashboard.html       # Main dashboard
│   ├── syllabus.html        # Syllabus listing
│   ├── upload_syllabus.html # Upload syllabus
│   ├── materials.html       # Study materials
│   ├── upload_material.html # Upload materials
│   ├── notes.html           # Notes listing
│   ├── add_notes.html       # Add notes
│   ├── pyq.html             # PYQ listing
│   ├── upload_pyq.html      # Upload PYQ
│   ├── notices.html         # Notices board
│   ├── post_notice.html     # Post notice
│   ├── admin/
│   │   ├── dashboard.html   # Admin dashboard
│   │   ├── export.html      # Export page
│   │   └── users.html       # User management
│   ├── errors/
│   │   ├── 404.html
│   │   ├── 403.html
│   │   └── 500.html
├── static/
│   ├── css/
│   │   └── style.css        # Custom styles
│   └── js/
│       └── main.js          # JavaScript utilities
├── uploads/                 # User uploaded files
├── exports/                 # Generated exports
└── b2study.db              # SQLite database
```

### Database Models

- **User**: Students and admins
- **Syllabus**: Curriculum documents
- **StudyMaterial**: Educational resources
- **Notes**: Lecture and class notes
- **PYQ**: Previous year questions
- **Notice**: Announcements and updates
- **LoginLog**: User login tracking
- **DownloadLog**: File download tracking

### Installation

```bash
# Clone repository
git clone https://github.com/nidhikumari18/B2Study.git
cd B2Study

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python
>>> from app import create_app
>>> app = create_app()
>>> with app.app_context():
...     from models import db
...     db.create_all()
>>> exit()

# Run application
python app.py
```

Access at `http://localhost:5000`

### Production Deployment

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### Configuration

See `.env.example` for all available configuration options.

### Key Routes

**Authentication**
- `GET /login` - Login page
- `POST /login` - Login submission
- `GET /signup` - Registration page
- `POST /signup` - Register new student
- `GET /logout` - Logout

**Student Routes**
- `GET /dashboard` - Main dashboard
- `GET /syllabus` - View syllabuses
- `GET /materials` - View study materials
- `GET /notes` - View and search notes
- `GET /pyq` - View PYQs with filters
- `GET /notices` - View notices

**Admin Routes**
- `GET /admin` - Admin dashboard
- `POST /syllabus/upload` - Upload syllabus
- `POST /materials/upload` - Upload material
- `POST /notes/add` - Add notes
- `POST /pyq/upload` - Upload PYQ
- `POST /notices/post` - Post notice
- `GET /admin/export` - Export data
- `GET /admin/users` - Manage users

### Technologies

- **Backend**: Flask, Flask-SQLAlchemy
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Frontend**: HTML5, CSS3, Bootstrap 5, JavaScript
- **Authentication**: Werkzeug password hashing
- **Export**: Pandas, OpenPyXL

### Security Features

- Password hashing with PBKDF2
- Session management
- CSRF protection
- Role-based access control
- File upload validation
- SQL injection prevention
- Secure filename generation

### License

MIT License

### Author

Nidhi Kumari - [@nidhikumari18](https://github.com/nidhikumari18)
