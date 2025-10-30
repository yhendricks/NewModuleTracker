import os
import sys
import django
from django.contrib.auth.models import User

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moduletrack.settings')
django.setup()

# Create a superuser with default credentials
def create_superuser():
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin123'  # Use a simple password for development
    
    if User.objects.filter(username=username).exists():
        print(f"User {username} already exists!")
        return
    
    user = User.objects.create_superuser(username, email, password)
    print(f"Superuser {username} created successfully with password: {password}")

if __name__ == "__main__":
    create_superuser()