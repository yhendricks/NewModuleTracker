import os
import sys
import django
from django.core.management import execute_from_command_line
from django.core import management

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moduletrack.settings')
django.setup()

def restore_db_from_backup(backup_file):
    """Restore the database from a backup file"""
    try:
        # First, flush the database to remove all existing data
        management.call_command('flush', interactive=False)
        
        # Load the data from the backup file
        management.call_command('loaddata', backup_file)
        
        print(f"Database successfully restored from: {backup_file}")
    except Exception as e:
        print(f"Error restoring database: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python restore_backup.py <backup_file.json>")
        sys.exit(1)
    
    backup_file = sys.argv[1]
    if not os.path.exists(backup_file):
        print(f"Backup file does not exist: {backup_file}")
        sys.exit(1)
    
    restore_db_from_backup(backup_file)