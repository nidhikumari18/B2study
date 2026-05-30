# Setup and Installation Guide

## B2Study - School Study Platform

### Quick Start

#### 1. Clone Repository
```bash
git clone https://github.com/nidhikumari18/B2Study.git
cd B2Study
```

#### 2. Create Virtual Environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

#### 4. Configure Environment
```bash
cp .env.example .env
```
Edit `.env` and add your configuration:
```
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///b2study.db
INSTAGRAM_URL=https://instagram.com/your-handle
LINKEDIN_URL=https://linkedin.com/in/your-profile
GITHUB_URL=https://github.com/your-username
```

#### 5. Initialize Database
```bash
python
>>> from app import create_app
>>> app = create_app()
>>> with app.app_context():
...     from models import db
...     db.create_all()
>>> exit()
```

#### 6. Run Application
```bash
python app.py
```

Access at: **http://localhost:5000**

### Default Admin Setup

1. Go to `/signup` to create your admin account
2. Use that email and password to login
3. You'll have access to all admin features

### Production Deployment

#### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

#### Environment Variables (Production)
```bash
export FLASK_ENV=production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://user:password@localhost/b2study
export INSTAGRAM_URL=https://instagram.com/...
export LINKEDIN_URL=https://linkedin.com/...
export GITHUB_URL=https://github.com/...
```

#### Using PostgreSQL
```bash
pip install psycopg2-binary
# Update DATABASE_URL to PostgreSQL connection string
```

### Features

✅ **Student Features**
- Secure registration and login
- View syllabuses, study materials, notes
- Search and filter notes by subject
- Browse previous year questions (PYQs)
- View notices and announcements
- Download educational resources

✅ **Admin Features**
- Upload syllabuses, materials, notes, PYQs
- Post notices with expiration dates
- Manage user accounts (activate/deactivate)
- View admin dashboard with statistics
- Export student data (CSV/Excel)
- Export login records
- Track downloads and user activity

### API Routes

**Authentication**
- `POST /login` - User login
- `POST /signup` - New user registration
- `GET /logout` - User logout

**Student Routes**
- `GET /dashboard` - Main dashboard
- `GET /syllabus` - View syllabuses
- `GET /materials` - View study materials
- `GET /notes` - Search notes
- `GET /pyq` - Browse PYQs
- `GET /notices` - View notices
- `GET /<resource>/download/<id>` - Download files

**Admin Routes**
- `GET /admin` - Admin dashboard
- `POST /syllabus/upload` - Upload syllabus
- `POST /materials/upload` - Upload material
- `POST /notes/add` - Add notes
- `POST /pyq/upload` - Upload PYQ
- `POST /notices/post` - Post notice
- `GET /admin/export` - Export data
- `GET /admin/users` - Manage users

### Database Schema

**Users Table**
- id, name, email, password_hash, role, is_active, enrollment_number, phone, batch, branch, created_at, updated_at, last_login

**Content Tables**
- Syllabus, StudyMaterial, Notes, PYQ, Notice
- Each with timestamps, file URLs, and creator references

**Tracking Tables**
- LoginLog (user logins with IP and timestamp)
- DownloadLog (file downloads tracking)

### Security Features

🔒 Password hashing with PBKDF2  
🔒 Session-based authentication  
🔒 Role-based access control  
🔒 CSRF protection  
🔒 Secure file upload validation  
🔒 SQL injection prevention  
🔒 XSS protection through Jinja2 escaping  

### Troubleshooting

**Port Already in Use**
```bash
python app.py --port 5001
```

**Database Issues**
```bash
rm b2study.db
python app.py
```

**Module Not Found**
```bash
pip install --upgrade -r requirements.txt
```

### Support

For issues, create an issue on GitHub or contact through:
- Instagram: [your-handle]
- LinkedIn: [your-profile]
- GitHub: [your-username]

### License

MIT License - Feel free to use this project for educational purposes.

---

**Made with ❤️ by Nidhi Kumari**
