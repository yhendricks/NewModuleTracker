# NewModuleTracker

This is a Django project for tracking new modules. It allows users to define different types of PCBs and test configurations, and then create batches of PCBs that are associated with a specific PCB type and test configuration.

## Project Structure

The project is divided into three main Django apps:

*   `pcb_type_app`: Manages the different types of PCBs that can be tracked.
*   `test_config_type_app`: Manages the different types of test configurations that can be used to test PCBs. Each test configuration can have multiple test steps, which can be of different types (e.g., voltage measurement, current measurement, etc.).
*   `batch_app`: Manages batches of PCBs. Each batch is associated with a `PcbType` and a `TestConfigType`.

## Running the project with Docker Compose

To run this project using Docker Compose, follow these steps after cloning the repository:

1.  **Build and start the Docker containers:**
    ```bash
    docker-compose up -d --build
    ```

2.  **Apply database migrations:**
    ```bash
    docker-compose exec web python manage.py migrate
    ```

3.  **Create a development superuser:**
    ```bash
    docker-compose exec web python manage.py shell -c "from create_dev_superuser import create_superuser; create_superuser()"
    ```
    This will create a superuser with the username `admin` and password `admin123`.

The application will be accessible at `http://localhost:8000`.

## Development Conventions

This project follows standard Django conventions. Each app has its own `models.py`, `views.py`, `urls.py`, and `admin.py` files. Templates are stored in the `templates` directory, with subdirectories for each app.

### TODO

*   Add instructions for running tests.