"""
File handling utilities
"""

import os
import secrets
from werkzeug.utils import secure_filename
from datetime import datetime


def generate_filename(original_filename):
    """Generate a secure filename with timestamp"""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S_')
    filename = secure_filename(original_filename)
    random_suffix = secrets.token_hex(4)
    name, ext = os.path.splitext(filename)
    return f"{timestamp}{name}_{random_suffix}{ext}"


def save_upload_file(file, upload_folder, allowed_extensions):
    """Save uploaded file safely"""
    if not file or file.filename == '':
        return None, 'No file selected'
    
    filename = file.filename
    if '.' not in filename:
        return None, 'Invalid file format'
    
    ext = filename.rsplit('.', 1)[1].lower()
    if ext not in allowed_extensions:
        return None, f'File type .{ext} not allowed. Allowed: {", ".join(allowed_extensions)}'
    
    try:
        secure_name = generate_filename(filename)
        filepath = os.path.join(upload_folder, secure_name)
        os.makedirs(upload_folder, exist_ok=True)
        file.save(filepath)
        return secure_name, None
    except Exception as e:
        return None, f'Error saving file: {str(e)}'


def delete_file(filepath):
    """Delete a file safely"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting file: {str(e)}")
    return False


def get_file_extension(filename):
    """Get file extension"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def get_file_size(filepath):
    """Get file size in bytes"""
    try:
        return os.path.getsize(filepath)
    except:
        return 0
