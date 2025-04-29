# Archi-N-Tier Admin Flask

A Flask-based admin interface for the Archi-N-Tier application.

## Setup

1. Create a virtual environment with uv:

    ```
    uv venv
    source .venv/bin/activate  # On Windows: .venv\Scripts\activate
    ```

2. Install the dependencies with uv:

    ```
    uv pip install -r requirements.txt
    ```

3. Install additional packages:

    ```
    uv add python-dotenv
    ```

4. Run the application:

    ```
    python main.py
    ```

5. Open your browser and navigate to http://127.0.0.1:5000/

## Project Structure

-   `main.py` - Entry point for the Flask application
-   `templates/` - HTML templates
    -   Uses Tailwind CSS via CDN
-   `static/` - Static files (CSS, JavaScript, images)
    -   `js/` - JavaScript files
-   `.env-example` - Example environment configuration
