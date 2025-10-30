# ModuleTrack Django Application

## Project Overview

ModuleTrack is a Django-based web application designed to manage and track various electronic modules and their testing configurations. The application provides a comprehensive system for creating, organizing, and managing different types of modules and their associated test procedures.

### Key Features

1. **PCB Type Management** - Track different types of printed circuit boards with their specifications
2. **Test Configuration Management** - Create detailed test configurations with flexible step ordering
3. **User Authentication & Authorization** - Role-based access control with user groups and permissions
4. **Responsive Web Interface** - Bootstrap-based UI with HTMX for dynamic interactions

### Core Technologies

- **Django 5.2** - Python web framework
- **SQLite** - Database backend (development)
- **Bootstrap 5** - Frontend framework for responsive design
- **HTMX** - Dynamic HTML interactions without full page reloads
- **Docker** - Containerization for consistent deployment

## Application Architecture

### Main Components

1. **Main Project (`moduletrack/`)**
   - Core Django project configuration
   - URL routing for the entire application
   - User authentication views
   - Signals and application configuration

2. **PCB Type App (`pcb_type_app/`)**
   - Manages PCB types and their specifications
   - CRUD operations for PCB type management
   - Group-based permissions (`mng_pcb_type`)

3. **Test Configuration Type App (`test_config_type_app/`)**
   - Manages test configurations with flexible step ordering
   - Supports multiple step types:
     - Voltage/Current/Resistance/Frequency measurements
     - Yes/No questions
     - Instructions/User actions
   - Group-based permissions (`mng_test_config_type`)

### Data Models

#### TestConfigType
Represents a test configuration with:
- Unique name and description
- Associated test steps in a specific order

#### TestStep
Represents individual steps in a test configuration:
- Multiple step types (measurements, questions, instructions)
- Configurable parameters based on step type
- Ordered sequence within a test configuration

## Development Environment Setup

### Prerequisites

- Python 3.11+
- Docker and Docker Compose (recommended)
- Git

### Local Development Setup

1. **Clone the Repository**
```bash
git clone <repository-url>
cd ModuleTrack
```

2. **Install Dependencies**
```bash
pip install -r requirements.txt
```

3. **Database Migrations**
```bash
python manage.py migrate
```

4. **Create Superuser**
```bash
python manage.py createsuperuser
```

5. **Run Development Server**
```bash
python manage.py runserver
```

### Docker Setup

1. **Build and Run with Docker Compose**
```bash
docker-compose up --build
```

2. **Access the Application**
- Web interface: http://localhost:8000
- Admin interface: http://localhost:8000/admin

## Building and Running

### Development Mode

```bash
# Start the development server
python manage.py runserver

# Or with Docker
docker-compose up
```

### Production Considerations

1. **Database**: Replace SQLite with PostgreSQL for production
2. **Static Files**: Configure proper static file serving
3. **Security**: Set proper SECRET_KEY and DEBUG settings
4. **HTTPS**: Configure SSL/TLS for secure connections

### Management Commands

```bash
# Create database migrations
python manage.py makemigrations

# Apply database migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Backup database
python create_backup.py

# Restore database
python restore_backup.py <backup_file.json>
```

## Development Conventions

### Code Structure

- **Views**: Function-based views with decorator-based authentication
- **Templates**: Bootstrap-based HTML with HTMX enhancements
- **Models**: Well-defined relationships with proper validation
- **Forms**: Django forms for data validation and processing

### Permissions and Groups

The application uses Django's built-in authentication system with custom groups:

1. **mng_pcb_type** - Permissions for PCB type management
2. **mng_test_config_type** - Permissions for test configuration management

Users must belong to appropriate groups to access management features.

### Template Organization

- **Base Templates** (`templates/base.html`) - Common layout and navigation
- **App-Specific Templates** (`templates/<app_name>/`) - Views for each application
- **Responsive Design** - Mobile-first approach with Bootstrap grid system

## Testing

Currently, the application relies on manual testing through the web interface. Future improvements should include:

1. **Unit Tests** - Test individual components and functions
2. **Integration Tests** - Test workflows and user journeys
3. **UI Tests** - Automated browser-based testing

## Deployment

### Docker Deployment

The application includes Docker configuration for easy deployment:

1. **Build the Image**
```bash
docker-compose build
```

2. **Run the Application**
```bash
docker-compose up -d
```

### Environment Variables

Key environment variables for configuration:
- `DEBUG` - Django debug mode
- `SECRET_KEY` - Django secret key
- `DB_NAME` - Database file path

## Maintenance

### Database Backups

Regular database backups are important for data protection:

```bash
# Create a backup
python create_backup.py

# Restore from backup
python restore_backup.py backup_file.json
```

### Updates and Migrations

When updating the application:

1. Pull the latest code
2. Run migrations: `python manage.py migrate`
3. Restart the server

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Commit with descriptive messages
5. Push to your fork
6. Submit a pull request

Follow the existing code style and conventions. Add tests for new functionality when possible.