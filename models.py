"""
Database models for B2Study
Using Flask-SQLAlchemy with modular design
"""

from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import uuid

db = SQLAlchemy()


class User(db.Model):
    """User model for students and admins"""
    __tablename__ = 'users'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), default='student', nullable=False)  # student or admin
    is_active = db.Column(db.Boolean, default=True)
    enrollment_number = db.Column(db.String(50), unique=True, nullable=True, index=True)
    phone = db.Column(db.String(20), nullable=True)
    batch = db.Column(db.String(50), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    logins = db.relationship('LoginLog', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password, method='pbkdf2:sha256')
    
    def check_password(self, password):
        """Verify password"""
        return check_password_hash(self.password_hash, password)
    
    def is_admin(self):
        """Check if user is admin"""
        return self.role == 'admin'
    
    def is_student(self):
        """Check if user is student"""
        return self.role == 'student'
    
    def __repr__(self):
        return f'<User {self.email} ({self.role})>'


class Syllabus(db.Model):
    """Syllabus documents"""
    __tablename__ = 'syllabuses'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False, index=True)
    semester = db.Column(db.Integer, nullable=True)
    file_url = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=True)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Syllabus {self.title}>'


class StudyMaterial(db.Model):
    """Study materials (notes, guides, etc.)"""
    __tablename__ = 'study_materials'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(100), nullable=False, index=True)
    material_type = db.Column(db.String(50), nullable=False)  # e.g., notes, guide, tutorial
    file_url = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=True)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<StudyMaterial {self.title}>'


class Notes(db.Model):
    """Class notes and lecture notes"""
    __tablename__ = 'notes'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(100), nullable=False, index=True)
    chapter = db.Column(db.String(150), nullable=True)
    content = db.Column(db.Text, nullable=True)
    file_url = db.Column(db.String(255), nullable=True)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notes {self.title}>'


class PYQ(db.Model):
    """Previous Year Questions"""
    __tablename__ = 'pyqs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    subject = db.Column(db.String(100), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=False, index=True)
    exam_type = db.Column(db.String(50), nullable=False)  # e.g., midterm, final, quiz
    semester = db.Column(db.Integer, nullable=True)
    file_url = db.Column(db.String(255), nullable=False)
    solutions_url = db.Column(db.String(255), nullable=True)
    uploaded_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<PYQ {self.subject} - {self.year}>'


class Notice(db.Model):
    """Notices and announcements"""
    __tablename__ = 'notices'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), default='general')  # e.g., general, academic, event
    posted_by = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    is_important = db.Column(db.Boolean, default=False)
    expires_at = db.Column(db.DateTime, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<Notice {self.title}>'
    
    @property
    def is_expired(self):
        """Check if notice is expired"""
        if self.expires_at:
            return datetime.utcnow() > self.expires_at
        return False


class LoginLog(db.Model):
    """User login logs for tracking"""
    __tablename__ = 'login_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    ip_address = db.Column(db.String(45), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    login_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    logout_time = db.Column(db.DateTime, nullable=True)
    
    def __repr__(self):
        return f'<LoginLog {self.user_id} at {self.login_time}>'


class DownloadLog(db.Model):
    """Track file downloads"""
    __tablename__ = 'download_logs'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False, index=True)
    file_type = db.Column(db.String(50), nullable=False)  # e.g., syllabus, notes, pyq
    file_id = db.Column(db.String(36), nullable=False)
    file_name = db.Column(db.String(255), nullable=False)
    download_time = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    
    def __repr__(self):
        return f'<DownloadLog {self.file_name}>'
