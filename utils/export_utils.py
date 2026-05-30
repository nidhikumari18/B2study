"""
Export utilities for student data
Handles CSV and Excel exports
"""

import os
import csv
from datetime import datetime
from io import BytesIO, StringIO
import pandas as pd
from models import User, LoginLog


class ExportManager:
    """Manage data exports"""
    
    def __init__(self, export_folder='exports'):
        """Initialize export manager"""
        self.export_folder = export_folder
        self._ensure_folder_exists()
    
    def _ensure_folder_exists(self):
        """Create export folder if it doesn't exist"""
        if not os.path.exists(self.export_folder):
            os.makedirs(self.export_folder)
    
    def generate_students_csv(self, students):
        """Generate CSV for student registrations"""
        output = StringIO()
        
        if not students:
            return None
        
        fieldnames = [
            'Name', 'Email', 'Enrollment Number', 'Phone', 'Batch', 'Branch',
            'Role', 'Active', 'Joined Date'
        ]
        
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for student in students:
            writer.writerow({
                'Name': student.name,
                'Email': student.email,
                'Enrollment Number': student.enrollment_number or 'N/A',
                'Phone': student.phone or 'N/A',
                'Batch': student.batch or 'N/A',
                'Branch': student.branch or 'N/A',
                'Role': student.role,
                'Active': 'Yes' if student.is_active else 'No',
                'Joined Date': student.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        bytes_output = BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8'))
        bytes_output.seek(0)
        
        return bytes_output
    
    def generate_students_excel(self, students):
        """Generate Excel for student registrations"""
        if not students:
            return None
        
        data = []
        for student in students:
            data.append({
                'Name': student.name,
                'Email': student.email,
                'Enrollment Number': student.enrollment_number or 'N/A',
                'Phone': student.phone or 'N/A',
                'Batch': student.batch or 'N/A',
                'Branch': student.branch or 'N/A',
                'Role': student.role,
                'Active': 'Yes' if student.is_active else 'No',
                'Joined Date': student.created_at.strftime('%Y-%m-%d %H:%M:%S')
            })
        
        df = pd.DataFrame(data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Students')
            worksheet = writer.sheets['Students']
            for idx, col in enumerate(df.columns):
                worksheet.column_dimensions[chr(65 + idx)].width = 20
        
        output.seek(0)
        return output
    
    def generate_login_logs_csv(self, logs):
        """Generate CSV for login logs"""
        output = StringIO()
        
        if not logs:
            return None
        
        fieldnames = ['User Email', 'Login Time', 'Logout Time', 'IP Address']
        writer = csv.DictWriter(output, fieldnames=fieldnames)
        writer.writeheader()
        
        for log in logs:
            user = User.query.get(log.user_id)
            writer.writerow({
                'User Email': user.email if user else 'Unknown',
                'Login Time': log.login_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Logout Time': log.logout_time.strftime('%Y-%m-%d %H:%M:%S') if log.logout_time else 'Active',
                'IP Address': log.ip_address or 'N/A'
            })
        
        bytes_output = BytesIO()
        bytes_output.write(output.getvalue().encode('utf-8'))
        bytes_output.seek(0)
        
        return bytes_output
    
    def generate_login_logs_excel(self, logs):
        """Generate Excel for login logs"""
        if not logs:
            return None
        
        data = []
        for log in logs:
            user = User.query.get(log.user_id)
            data.append({
                'User Email': user.email if user else 'Unknown',
                'Login Time': log.login_time.strftime('%Y-%m-%d %H:%M:%S'),
                'Logout Time': log.logout_time.strftime('%Y-%m-%d %H:%M:%S') if log.logout_time else 'Active',
                'IP Address': log.ip_address or 'N/A'
            })
        
        df = pd.DataFrame(data)
        output = BytesIO()
        
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Login Logs')
            worksheet = writer.sheets['Login Logs']
            for idx, col in enumerate(df.columns):
                worksheet.column_dimensions[chr(65 + idx)].width = 20
        
        output.seek(0)
        return output


def allowed_file(filename, allowed_extensions):
    """Check if file is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def get_file_size_mb(file_size_bytes):
    """Convert bytes to MB"""
    return round(file_size_bytes / (1024 * 1024), 2)
