import os
import sys
from datetime import datetime
import subprocess
import django
from django.core.management import execute_from_command_line
from django.core import management

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moduletrack.settings')
django.setup()

def create_db_backup():
    """Create a backup of the database schema and data"""
    try:
        # Create timestamped backup filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db_backup')
        backup_file = os.path.join(backup_dir, f"db_backup_{timestamp}.json")
        
        # Run Django's dumpdata command
        management.call_command('dumpdata', 
                               '--exclude', 'contenttypes', 
                               '--exclude', 'auth.permission', 
                               '--exclude', 'sessions.session',
                               output=backup_file)
        
        print(f"Database backup created: {backup_file}")
        return backup_file
    except Exception as e:
        print(f"Error creating database backup: {e}")
        return None

def get_current_git_commit():
    """Get the current Git commit hash"""
    try:
        result = subprocess.run(['git', 'rev-parse', 'HEAD'], 
                                capture_output=True, text=True, cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        if result.returncode == 0:
            return result.stdout.strip()[:8]  # Return short hash
        return None
    except Exception as e:
        print(f"Error getting Git commit: {e}")
        return None

def create_backup_with_commit():
    """Create a database backup with Git commit information"""
    git_commit = get_current_git_commit()
    backup_file = create_db_backup()
    
    if backup_file and git_commit:
        # Create a README file with commit info
        readme_file = backup_file.replace('.json', '_README.txt')
        with open(readme_file, 'w') as f:
            f.write(f"Database backup for Git commit: {git_commit}\n")
            f.write(f"Backup created on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Original backup file: {os.path.basename(backup_file)}\n")
        
        print(f"Backup README created: {readme_file}")
        return backup_file, readme_file
    
    return None, None

if __name__ == "__main__":
    create_backup_with_commit()