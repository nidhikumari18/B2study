"""
B2Study - School Study Platform
Production-ready Flask application
"""

from flask import (
    Flask, render_template, request, redirect, url_for,
    flash, session, send_file, jsonify, abort
)
from functools import wraps
from datetime import datetime, timedelta
import os
import uuid
from werkzeug.utils import secure_filename

from config import get_config
from models import db, User, Syllabus, StudyMaterial, Notes, PYQ, Notice, LoginLog, DownloadLog
from utils import ExportManager, save_upload_file, delete_file, get_file_size


def create_app(config=None):
    """Application factory"""
    app = Flask(__name__)
    
    # Configuration
    if config is None:
        config = get_config()
    app.config.from_object(config)
    
    # Initialize extensions
    db.init_app(app)
    
    # Create necessary folders
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    os.makedirs(app.config['EXPORT_FOLDER'], exist_ok=True)
    
    # Register routes
    register_routes(app)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app


def register_routes(app):
    """Register all application routes"""
    
    export_manager = ExportManager(app.config['EXPORT_FOLDER'])
    
    # ============= DECORATORS =============
    
    def login_required(f):
        """Require login"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            return f(*args, **kwargs)
        return decorated_function
    
    def admin_required(f):
        """Require admin role"""
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                flash('Please log in first.', 'warning')
                return redirect(url_for('login'))
            user = User.query.get(session['user_id'])
            if not user or not user.is_admin():
                flash('Admin access required.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    
    # ============= AUTHENTICATION ROUTES =============
    
    @app.route('/')
    def index():
        """Home page"""
        if 'user_id' in session:
            return redirect(url_for('dashboard'))
        return redirect(url_for('login'))
    
    @app.route('/login', methods=['GET', 'POST'])
    def login():
        """User login"""
        if request.method == 'POST':
            try:
                email = request.form.get('email', '').strip()
                password = request.form.get('password', '')
                
                if not email or not password:
                    flash('Email and password required.', 'error')
                    return redirect(url_for('login'))
                
                user = User.query.filter_by(email=email).first()
                
                if user and user.check_password(password):
                    if not user.is_active:
                        flash('Account is inactive.', 'error')
                        return redirect(url_for('login'))
                    
                    session['user_id'] = user.id
                    session['username'] = user.name
                    session['email'] = user.email
                    session['role'] = user.role
                    session.permanent = True
                    app.permanent_session_lifetime = timedelta(hours=24)
                    
                    # Log login
                    login_log = LoginLog(
                        user_id=user.id,
                        ip_address=request.remote_addr,
                        user_agent=request.headers.get('User-Agent')
                    )
                    db.session.add(login_log)
                    user.last_login = datetime.utcnow()
                    db.session.commit()
                    
                    flash(f'Welcome back, {user.name}!', 'success')
                    return redirect(url_for('dashboard'))
                else:
                    flash('Invalid email or password.', 'error')
            
            except Exception as e:
                app.logger.error(f"Login error: {str(e)}")
                flash('An error occurred.', 'error')
        
        return render_template('login.html')
    
    @app.route('/signup', methods=['GET', 'POST'])
    def signup():
        """User registration"""
        if request.method == 'POST':
            try:
                name = request.form.get('name', '').strip()
                email = request.form.get('email', '').strip()
                password = request.form.get('password', '')
                confirm = request.form.get('confirm_password', '')
                enrollment = request.form.get('enrollment_number', '').strip()
                batch = request.form.get('batch', '').strip()
                branch = request.form.get('branch', '').strip()
                phone = request.form.get('phone', '').strip()
                
                errors = []
                
                if not all([name, email, password]):
                    errors.append('Name, email, and password required.')
                
                if len(password) < 6:
                    errors.append('Password must be at least 6 characters.')
                
                if password != confirm:
                    errors.append('Passwords do not match.')
                
                if User.query.filter_by(email=email).first():
                    errors.append('Email already registered.')
                
                if enrollment and User.query.filter_by(enrollment_number=enrollment).first():
                    errors.append('Enrollment number already exists.')
                
                for error in errors:
                    flash(error, 'error')
                
                if not errors:
                    user = User(
                        name=name,
                        email=email,
                        enrollment_number=enrollment if enrollment else None,
                        batch=batch if batch else None,
                        branch=branch if branch else None,
                        phone=phone if phone else None,
                        role='student'
                    )
                    user.set_password(password)
                    
                    db.session.add(user)
                    db.session.commit()
                    
                    flash('Account created! Please log in.', 'success')
                    return redirect(url_for('login'))
            
            except Exception as e:
                db.session.rollback()
                app.logger.error(f"Signup error: {str(e)}")
                flash('An error occurred.', 'error')
        
        return render_template('signup.html')
    
    @app.route('/logout')
    def logout():
        """User logout"""
        session.clear()
        flash('You have been logged out.', 'success')
        return redirect(url_for('login'))
    
    # ============= DASHBOARD & MAIN ROUTES =============
    
    @app.route('/dashboard')
    @login_required
    def dashboard():
        """Main dashboard"""
        try:
            user = User.query.get(session['user_id'])
            
            # Get active notices
            notices = Notice.query.filter(
                (Notice.expires_at.isnull()) | (Notice.expires_at > datetime.utcnow())
            ).order_by(Notice.created_at.desc()).limit(5).all()
            
            # Get recent materials
            materials = StudyMaterial.query.order_by(
                StudyMaterial.created_at.desc()
            ).limit(6).all()
            
            # Admin stats
            stats = {}
            if user.is_admin():
                stats = {
                    'total_students': User.query.filter_by(role='student').count(),
                    'total_materials': StudyMaterial.query.count(),
                    'total_notes': Notes.query.count(),
                    'total_pyqs': PYQ.query.count(),
                    'total_notices': Notice.query.count(),
                    'total_logins': LoginLog.query.count(),
                }
            
            return render_template('dashboard.html', 
                                 user=user, notices=notices, materials=materials, stats=stats)
        
        except Exception as e:
            app.logger.error(f"Dashboard error: {str(e)}")
            flash('An error occurred.', 'error')
            return redirect(url_for('logout'))
    
    # ============= SYLLABUS ROUTES =============
    
    @app.route('/syllabus')
    @login_required
    def syllabus_list():
        """List all syllabuses"""
        try:
            page = request.args.get('page', 1, type=int)
            subject = request.args.get('subject', '', type=str)
            
            query = Syllabus.query
            if subject:
                query = query.filter_by(subject=subject)
            
            syllabuses = query.order_by(Syllabus.created_at.desc()).paginate(
                page=page, per_page=app.config['ITEMS_PER_PAGE']
            )
            
            subjects = db.session.query(Syllabus.subject).distinct().all()
            subjects = [s[0] for s in subjects]
            
            return render_template('syllabus.html', syllabuses=syllabuses, subjects=subjects, current_subject=subject)
        
        except Exception as e:
            app.logger.error(f"Syllabus error: {str(e)}")
            flash('An error occurred.', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/syllabus/upload', methods=['GET', 'POST'])
    @admin_required
    def upload_syllabus():
        """Upload syllabus (admin only)"""
        try:
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file selected.', 'error')
                    return redirect(url_for('upload_syllabus'))
                
                file = request.files['file']
                title = request.form.get('title', '').strip()
                subject = request.form.get('subject', '').strip()
                description = request.form.get('description', '').strip()
                semester = request.form.get('semester', type=int)
                
                if not all([title, subject, file.filename]):
                    flash('Title, subject, and file required.', 'error')
                    return redirect(url_for('upload_syllabus'))
                
                filename, error = save_upload_file(file, app.config['UPLOAD_FOLDER'], 
                                                   app.config['ALLOWED_EXTENSIONS'])
                
                if error:
                    flash(error, 'error')
                    return redirect(url_for('upload_syllabus'))
                
                syllabus = Syllabus(
                    title=title,
                    subject=subject,
                    description=description if description else None,
                    semester=semester,
                    file_url=filename,
                    uploaded_by=session['user_id']
                )
                
                db.session.add(syllabus)
                db.session.commit()
                
                flash('Syllabus uploaded successfully!', 'success')
                return redirect(url_for('syllabus_list'))
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Upload syllabus error: {str(e)}")
            flash('An error occurred.', 'error')
        
        return render_template('upload_syllabus.html')
    
    @app.route('/syllabus/download/<syllabus_id>')
    @login_required
    def download_syllabus(syllabus_id):
        """Download syllabus"""
        try:
            syllabus = Syllabus.query.get(syllabus_id)
            if not syllabus:
                abort(404)
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], syllabus.file_url)
            if not os.path.exists(filepath):
                abort(404)
            
            # Log download
            download = DownloadLog(
                user_id=session['user_id'],
                file_type='syllabus',
                file_id=syllabus_id,
                file_name=syllabus.title
            )
            db.session.add(download)
            db.session.commit()
            
            return send_file(filepath, as_attachment=True, download_name=f"{syllabus.title}.pdf")
        
        except Exception as e:
            app.logger.error(f"Download error: {str(e)}")
            abort(500)
    
    # ============= STUDY MATERIALS ROUTES =============
    
    @app.route('/materials')
    @login_required
    def materials_list():
        """List study materials"""
        try:
            page = request.args.get('page', 1, type=int)
            subject = request.args.get('subject', '', type=str)
            material_type = request.args.get('type', '', type=str)
            
            query = StudyMaterial.query
            if subject:
                query = query.filter_by(subject=subject)
            if material_type:
                query = query.filter_by(material_type=material_type)
            
            materials = query.order_by(StudyMaterial.created_at.desc()).paginate(
                page=page, per_page=app.config['ITEMS_PER_PAGE']
            )
            
            subjects = db.session.query(StudyMaterial.subject).distinct().all()
            subjects = [s[0] for s in subjects]
            types = db.session.query(StudyMaterial.material_type).distinct().all()
            types = [t[0] for t in types]
            
            return render_template('materials.html', materials=materials, subjects=subjects,
                                 material_types=types, current_subject=subject, current_type=material_type)
        
        except Exception as e:
            app.logger.error(f"Materials error: {str(e)}")
            flash('An error occurred.', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/materials/upload', methods=['GET', 'POST'])
    @admin_required
    def upload_material():
        """Upload study material"""
        try:
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file selected.', 'error')
                    return redirect(url_for('upload_material'))
                
                file = request.files['file']
                title = request.form.get('title', '').strip()
                subject = request.form.get('subject', '').strip()
                material_type = request.form.get('type', '').strip()
                description = request.form.get('description', '').strip()
                
                if not all([title, subject, material_type, file.filename]):
                    flash('Title, subject, type, and file required.', 'error')
                    return redirect(url_for('upload_material'))
                
                filename, error = save_upload_file(file, app.config['UPLOAD_FOLDER'],
                                                   app.config['ALLOWED_EXTENSIONS'])
                
                if error:
                    flash(error, 'error')
                    return redirect(url_for('upload_material'))
                
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file_size = get_file_size(filepath)
                
                material = StudyMaterial(
                    title=title,
                    subject=subject,
                    material_type=material_type,
                    description=description if description else None,
                    file_url=filename,
                    file_size=file_size,
                    uploaded_by=session['user_id']
                )
                
                db.session.add(material)
                db.session.commit()
                
                flash('Study material uploaded!', 'success')
                return redirect(url_for('materials_list'))
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Upload material error: {str(e)}")
            flash('An error occurred.', 'error')
        
        return render_template('upload_material.html')
    
    @app.route('/materials/download/<material_id>')
    @login_required
    def download_material(material_id):
        """Download study material"""
        try:
            material = StudyMaterial.query.get(material_id)
            if not material:
                abort(404)
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], material.file_url)
            if not os.path.exists(filepath):
                abort(404)
            
            # Log download
            download = DownloadLog(
                user_id=session['user_id'],
                file_type='material',
                file_id=material_id,
                file_name=material.title
            )
            db.session.add(download)
            db.session.commit()
            
            return send_file(filepath, as_attachment=True, download_name=f"{material.title}.pdf")
        
        except Exception as e:
            app.logger.error(f"Download error: {str(e)}")
            abort(500)
    
    # ============= NOTES ROUTES =============
    
    @app.route('/notes')
    @login_required
    def notes_list():
        """List notes with search"""
        try:
            page = request.args.get('page', 1, type=int)
            search = request.args.get('search', '', type=str)
            subject = request.args.get('subject', '', type=str)
            
            query = Notes.query
            if search:
                query = query.filter(
                    (Notes.title.ilike(f'%{search}%')) |
                    (Notes.content.ilike(f'%{search}%')) |
                    (Notes.chapter.ilike(f'%{search}%'))
                )
            if subject:
                query = query.filter_by(subject=subject)
            
            notes = query.order_by(Notes.created_at.desc()).paginate(
                page=page, per_page=app.config['ITEMS_PER_PAGE']
            )
            
            subjects = db.session.query(Notes.subject).distinct().all()
            subjects = [s[0] for s in subjects]
            
            return render_template('notes.html', notes=notes, subjects=subjects,
                                 current_subject=subject, search_query=search)
        
        except Exception as e:
            app.logger.error(f"Notes error: {str(e)}")
            flash('An error occurred.', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/notes/add', methods=['GET', 'POST'])
    @admin_required
    def add_notes():
        """Add notes"""
        try:
            if request.method == 'POST':
                title = request.form.get('title', '').strip()
                subject = request.form.get('subject', '').strip()
                chapter = request.form.get('chapter', '').strip()
                content = request.form.get('content', '').strip()
                file = request.files.get('file')
                
                if not all([title, subject]):
                    flash('Title and subject required.', 'error')
                    return redirect(url_for('add_notes'))
                
                file_url = None
                if file and file.filename:
                    filename, error = save_upload_file(file, app.config['UPLOAD_FOLDER'],
                                                       app.config['ALLOWED_EXTENSIONS'])
                    if error:
                        flash(error, 'error')
                        return redirect(url_for('add_notes'))
                    file_url = filename
                
                note = Notes(
                    title=title,
                    subject=subject,
                    chapter=chapter if chapter else None,
                    content=content if content else None,
                    file_url=file_url,
                    uploaded_by=session['user_id']
                )
                
                db.session.add(note)
                db.session.commit()
                
                flash('Note added successfully!', 'success')
                return redirect(url_for('notes_list'))
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Add notes error: {str(e)}")
            flash('An error occurred.', 'error')
        
        return render_template('add_notes.html')
    
    @app.route('/notes/download/<note_id>')
    @login_required
    def download_notes(note_id):
        """Download notes"""
        try:
            note = Notes.query.get(note_id)
            if not note or not note.file_url:
                abort(404)
            
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], note.file_url)
            if not os.path.exists(filepath):
                abort(404)
            
            # Log download
            download = DownloadLog(
                user_id=session['user_id'],
                file_type='notes',
                file_id=note_id,
                file_name=note.title
            )
            db.session.add(download)
            db.session.commit()
            
            return send_file(filepath, as_attachment=True, download_name=f"{note.title}.pdf")
        
        except Exception as e:
            app.logger.error(f"Download error: {str(e)}")
            abort(500)
    
    # ============= PYQ ROUTES =============
    
    @app.route('/pyq')
    @login_required
    def pyq_list():
        """List previous year questions with filters"""
        try:
            page = request.args.get('page', 1, type=int)
            subject = request.args.get('subject', '', type=str)
            year = request.args.get('year', '', type=int)
            exam_type = request.args.get('exam', '', type=str)
            
            query = PYQ.query
            if subject:
                query = query.filter_by(subject=subject)
            if year:
                query = query.filter_by(year=year)
            if exam_type:
                query = query.filter_by(exam_type=exam_type)
            
            pyqs = query.order_by(PYQ.year.desc(), PYQ.created_at.desc()).paginate(
                page=page, per_page=app.config['ITEMS_PER_PAGE']
            )
            
            subjects = db.session.query(PYQ.subject).distinct().all()
            subjects = [s[0] for s in subjects]
            years = db.session.query(PYQ.year).distinct().order_by(PYQ.year.desc()).all()
            years = [y[0] for y in years]
            exams = db.session.query(PYQ.exam_type).distinct().all()
            exams = [e[0] for e in exams]
            
            return render_template('pyq.html', pyqs=pyqs, subjects=subjects, years=years,
                                 exam_types=exams, current_subject=subject, current_year=year,
                                 current_exam=exam_type)
        
        except Exception as e:
            app.logger.error(f"PYQ error: {str(e)}")
            flash('An error occurred.', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/pyq/upload', methods=['GET', 'POST'])
    @admin_required
    def upload_pyq():
        """Upload PYQ"""
        try:
            if request.method == 'POST':
                if 'file' not in request.files:
                    flash('No file selected.', 'error')
                    return redirect(url_for('upload_pyq'))
                
                file = request.files['file']
                solutions = request.files.get('solutions')
                subject = request.form.get('subject', '').strip()
                year = request.form.get('year', type=int)
                exam_type = request.form.get('exam_type', '').strip()
                semester = request.form.get('semester', type=int)
                
                if not all([subject, year, exam_type, file.filename]):
                    flash('Subject, year, exam type, and file required.', 'error')
                    return redirect(url_for('upload_pyq'))
                
                filename, error = save_upload_file(file, app.config['UPLOAD_FOLDER'],
                                                   app.config['ALLOWED_EXTENSIONS'])
                
                if error:
                    flash(error, 'error')
                    return redirect(url_for('upload_pyq'))
                
                solutions_url = None
                if solutions and solutions.filename:
                    sol_filename, sol_error = save_upload_file(solutions, app.config['UPLOAD_FOLDER'],
                                                               app.config['ALLOWED_EXTENSIONS'])
                    if not sol_error:
                        solutions_url = sol_filename
                
                pyq = PYQ(
                    subject=subject,
                    year=year,
                    exam_type=exam_type,
                    semester=semester,
                    file_url=filename,
                    solutions_url=solutions_url,
                    uploaded_by=session['user_id']
                )
                
                db.session.add(pyq)
                db.session.commit()
                
                flash('PYQ uploaded successfully!', 'success')
                return redirect(url_for('pyq_list'))
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Upload PYQ error: {str(e)}")
            flash('An error occurred.', 'error')
        
        return render_template('upload_pyq.html')
    
    @app.route('/pyq/download/<pyq_id>')
    @login_required
    def download_pyq(pyq_id):
        """Download PYQ"""
        try:
            pyq = PYQ.query.get(pyq_id)
            if not pyq:
                abort(404)
            
            file_type = request.args.get('type', 'question')  # question or solutions
            
            if file_type == 'solutions' and pyq.solutions_url:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], pyq.solutions_url)
            else:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], pyq.file_url)
            
            if not os.path.exists(filepath):
                abort(404)
            
            # Log download
            download = DownloadLog(
                user_id=session['user_id'],
                file_type='pyq',
                file_id=pyq_id,
                file_name=f"{pyq.subject} - {pyq.year}"
            )
            db.session.add(download)
            db.session.commit()
            
            return send_file(filepath, as_attachment=True, download_name=f"{pyq.subject}_{pyq.year}.pdf")
        
        except Exception as e:
            app.logger.error(f"Download error: {str(e)}")
            abort(500)
    
    # ============= NOTICE ROUTES =============
    
    @app.route('/notices')
    @login_required
    def notices():
        """View all notices"""
        try:
            page = request.args.get('page', 1, type=int)
            category = request.args.get('category', '', type=str)
            
            query = Notice.query.filter(
                (Notice.expires_at.isnull()) | (Notice.expires_at > datetime.utcnow())
            )
            if category:
                query = query.filter_by(category=category)
            
            notices = query.order_by(Notice.created_at.desc()).paginate(
                page=page, per_page=app.config['ITEMS_PER_PAGE']
            )
            
            categories = db.session.query(Notice.category).distinct().all()
            categories = [c[0] for c in categories]
            
            return render_template('notices.html', notices=notices, categories=categories,
                                 current_category=category)
        
        except Exception as e:
            app.logger.error(f"Notices error: {str(e)}")
            flash('An error occurred.', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/notices/post', methods=['GET', 'POST'])
    @admin_required
    def post_notice():
        """Post a notice (admin only)"""
        try:
            if request.method == 'POST':
                title = request.form.get('title', '').strip()
                content = request.form.get('content', '').strip()
                category = request.form.get('category', 'general').strip()
                is_important = request.form.get('is_important') == 'on'
                expires_at = request.form.get('expires_at')
                
                if not all([title, content]):
                    flash('Title and content required.', 'error')
                    return redirect(url_for('post_notice'))
                
                expires = None
                if expires_at:
                    try:
                        expires = datetime.fromisoformat(expires_at)
                    except:
                        pass
                
                notice = Notice(
                    title=title,
                    content=content,
                    category=category,
                    is_important=is_important,
                    expires_at=expires,
                    posted_by=session['user_id']
                )
                
                db.session.add(notice)
                db.session.commit()
                
                flash('Notice posted successfully!', 'success')
                return redirect(url_for('notices'))
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Post notice error: {str(e)}")
            flash('An error occurred.', 'error')
        
        return render_template('post_notice.html')
    
    # ============= ADMIN EXPORT ROUTES =============
    
    @app.route('/admin/export')
    @admin_required
    def export_page():
        """Export page"""
        return render_template('admin/export.html')
    
    @app.route('/admin/export/students/<format>')
    @admin_required
    def export_students(format):
        """Export student data"""
        try:
            students = User.query.filter_by(role='student').all()
            
            if format == 'csv':
                bytes_data = export_manager.generate_students_csv(students)
                filename = f"students_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                mimetype = 'text/csv'
            elif format == 'excel':
                bytes_data = export_manager.generate_students_excel(students)
                filename = f"students_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                abort(400)
            
            if not bytes_data:
                flash('No data to export.', 'error')
                return redirect(url_for('export_page'))
            
            return send_file(bytes_data, mimetype=mimetype, as_attachment=True, download_name=filename)
        
        except Exception as e:
            app.logger.error(f"Export error: {str(e)}")
            flash('Export failed.', 'error')
            return redirect(url_for('export_page'))
    
    @app.route('/admin/export/logins/<format>')
    @admin_required
    def export_logins(format):
        """Export login logs"""
        try:
            logs = LoginLog.query.all()
            
            if format == 'csv':
                bytes_data = export_manager.generate_login_logs_csv(logs)
                filename = f"login_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"
                mimetype = 'text/csv'
            elif format == 'excel':
                bytes_data = export_manager.generate_login_logs_excel(logs)
                filename = f"login_logs_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.xlsx"
                mimetype = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            else:
                abort(400)
            
            if not bytes_data:
                flash('No data to export.', 'error')
                return redirect(url_for('export_page'))
            
            return send_file(bytes_data, mimetype=mimetype, as_attachment=True, download_name=filename)
        
        except Exception as e:
            app.logger.error(f"Export error: {str(e)}")
            flash('Export failed.', 'error')
            return redirect(url_for('export_page'))
    
    # ============= ADMIN PANEL =============
    
    @app.route('/admin')
    @admin_required
    def admin_panel():
        """Admin dashboard"""
        try:
            stats = {
                'total_students': User.query.filter_by(role='student').count(),
                'total_materials': StudyMaterial.query.count(),
                'total_notes': Notes.query.count(),
                'total_pyqs': PYQ.query.count(),
                'total_notices': Notice.query.count(),
                'total_logins': LoginLog.query.count(),
                'total_downloads': DownloadLog.query.count(),
            }
            
            recent_logins = LoginLog.query.order_by(LoginLog.login_time.desc()).limit(10).all()
            recent_downloads = DownloadLog.query.order_by(DownloadLog.download_time.desc()).limit(10).all()
            
            return render_template('admin/dashboard.html', stats=stats, 
                                 recent_logins=recent_logins, recent_downloads=recent_downloads)
        
        except Exception as e:
            app.logger.error(f"Admin panel error: {str(e)}")
            flash('An error occurred.', 'error')
            return redirect(url_for('dashboard'))
    
    @app.route('/admin/users')
    @admin_required
    def manage_users():
        """Manage users"""
        try:
            page = request.args.get('page', 1, type=int)
            users = User.query.order_by(User.created_at.desc()).paginate(
                page=page, per_page=app.config['ITEMS_PER_PAGE']
            )
            return render_template('admin/users.html', users=users)
        
        except Exception as e:
            app.logger.error(f"Manage users error: {str(e)}")
            flash('An error occurred.', 'error')
            return redirect(url_for('admin_panel'))
    
    @app.route('/admin/user/<user_id>/toggle', methods=['POST'])
    @admin_required
    def toggle_user(user_id):
        """Toggle user active status"""
        try:
            user = User.query.get(user_id)
            if not user:
                return jsonify({'error': 'User not found'}), 404
            
            user.is_active = not user.is_active
            db.session.commit()
            
            return jsonify({'success': True, 'active': user.is_active})
        
        except Exception as e:
            db.session.rollback()
            app.logger.error(f"Toggle user error: {str(e)}")
            return jsonify({'error': str(e)}), 500
    
    # ============= ERROR HANDLERS =============
    
    @app.errorhandler(404)
    def not_found(e):
        return render_template('errors/404.html'), 404
    
    @app.errorhandler(403)
    def forbidden(e):
        return render_template('errors/403.html'), 403
    
    @app.errorhandler(500)
    def server_error(e):
        db.session.rollback()
        app.logger.error(f"Server error: {str(e)}")
        return render_template('errors/500.html'), 500


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5000)
