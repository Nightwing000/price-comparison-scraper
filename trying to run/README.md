# Price Comparison Web Scraper

This project is a backend service for scraping product prices from e-commerce websites and exposing the aggregated data via a RESTful API.

This project was built using Python 3.10, FastAPI, SQLAlchemy (with SQLite), and BeautifulSoup.

## Project Structure

* `src/app/`: Contains all the application source code.
    * `main.py`: The main FastAPI application entrypoint.
    * `api.py`: Defines all API endpoints (`/search`, `/admin`).
    * `core.py`: Configuration management (Pydantic settings).
    * `database.py`: SQLAlchemy setup, all DB models, and CRUD functions.
    * `scraper.py`: The core web scraping logic and HTML parsers.
    * `scheduler.py`: The `APScheduler` logic for automated scraping jobs.
* `tests/`: Contains all tests.
    * `conftest.py`: Pytest fixtures (e.g., test database, API client).
    * `test_unit.py`: Unit tests (e.g., testing parser logic with mock HTML).
    * `test_integration.py`: Integration tests (e.g., testing API endpoints).
    * `test_system.py`: End-to-end system tests.
* `.github/workflows/`: Contains the CI/CD pipeline configuration.
* `pylintrc`: Configuration for the Pylint linter.
* `pytest.ini`: Configuration for Pytest and the `pytest-cov` coverage tool.

## How to Run Locally

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Setup Instructions

1.  **Navigate to the project directory:**
    ```powershell
    cd "trying to run"
    ```

2.  **Create a virtual environment:**
    ```powershell
    python -m venv venv
    ```

3.  **Activate the virtual environment:**
    ```powershell
    .\venv\Scripts\Activate
    ```

4.  **Install dependencies:**
    ```powershell
    pip install -r requirements.txt
    ```

5.  **Set environment variables (Optional):**
    
    You can create a `.env` file in the project root or set environment variables directly:
    
    ```powershell
    $env:ADMIN_API_KEY="my-secret-key"
    $env:CLIENT_API_KEY="my-client-key"
    $env:DATABASE_URL="sqlite+aiosqlite:///./test.db"
    ```
    
    Or create a `.env` file:
    ```
    ADMIN_API_KEY=my-secret-key
    CLIENT_API_KEY=my-client-key
    DATABASE_URL=sqlite+aiosqlite:///./test.db
    ```

6.  **Run the application:**
    ```powershell
    uvicorn src.app.main:app --reload
    ```

7.  **Access the API:**
    - API will be running at `http://127.0.0.1:8000`
    - Interactive documentation at `http://127.0.0.1:8000/docs`

## Running Tests

To run all tests with coverage:

```powershell
pytest
```

To run specific test files:

```powershell
pytest tests/test_unit.py
pytest tests/test_integration.py
pytest tests/test_system.py
```

## Running Linter

To check code quality with pylint:

```powershell
pylint src/app --rcfile=pylintrc
```

## Running Security Scan

To run security scan with bandit:

```powershell
bandit -r src
```

## API Endpoints

All API keys are passed via the `x-api-key` header.

### Client Endpoints (Requires `CLIENT_API_KEY`)

* **`GET /api/v1/search`**: Search for products.
    * **Query Param:** `q` (string) - The product name to search for.
    * **Success Response (200):**
        ```json
        [
          {
            "id": 1,
            "name": "Example Product",
            "price": 99.99,
            "url": "http://example.com/product/1",
            "scraped_at": "2025-11-10T12:00:00Z"
          }
        ]
        ```

### Admin Endpoints (Requires `ADMIN_API_KEY`)

* **`POST /api/v1/admin/target`**: Add a new scrape target.
    * **Request Body:**
        ```json
        {
          "name": "Mock Store",
          "base_url": "http://example.com/products",
          "name_selector": "h1.product-title",
          "price_selector": "span.product-price",
          "url_selector": "a.product-link"
        }
        ```
    * **Success Response (201):** The newly created target object.

* **`GET /api/v1/admin/logs`**: Get the 10 most recent scrape logs.
    * **Success Response (200):**
        ```json
        [
          {
            "id": 1,
            "target_name": "Mock Store",
            "status": "success",
            "products_found": 5,
            "created_at": "2025-11-10T12:05:00Z"
          }
        ]
        ```

* **`POST /api/v1/admin/trigger-scrape`**: Manually trigger scraping job for all targets.
    * **Success Response (202):** `{"message": "Scraping job triggered successfully."}`

## CI/CD Pipeline

This project uses a 5-stage CI/CD pipeline defined in `.github/workflows/ci_pipeline.yml`.

1.  **Build:**
    * **What:** Installs Python and all project dependencies from `requirements.txt`.
    * **Tools:** `pip`

2.  **Lint:**
    * **What:** Runs a static code analysis to check for code quality and style issues.
    * **Tools:** `pylint`
    * **Quality Gate:** The pipeline will fail if the `pylint` score is below **7.5/10**.

3.  **Security:**
    * **What:** Runs a security scanner to find common vulnerabilities in the Python code.
    * **Tools:** `bandit`
    * **Quality Gate:** The pipeline will fail if `bandit` finds any high-severity issues.

4.  **Test & Coverage:**
    * **What:** Runs the entire test suite (unit, integration, system) and generates a code coverage report.
    * **Tools:** `pytest`, `pytest-cov`
    * **Quality Gate:** The pipeline will fail if code coverage is below **75%**.

5.  **Create-Artifact (Deployment):**
    * **What:** If all previous stages pass, this job creates a `deployment.zip` artifact.
    * **Contents:**
        * All source code (`src/`)
        * The `README.md` and `requirements.txt`
        * All CI/CD reports (lint, security, coverage)
    * **This artifact is the "deployment" deliverable as per the project rubric.**

## Project Features

- ✅ RESTful API with FastAPI
- ✅ Asynchronous web scraping with httpx and BeautifulSoup
- ✅ Scheduled automated scraping jobs with APScheduler
- ✅ SQLite database with SQLAlchemy ORM
- ✅ API key authentication for security
- ✅ Comprehensive test suite (unit, integration, system)
- ✅ CI/CD pipeline with quality gates
- ✅ Code quality checks with Pylint
- ✅ Security scanning with Bandit
- ✅ 75%+ code coverage

## Development Notes

- The application uses async/await patterns throughout for better performance
- Database migrations can be added using Alembic in production
- The scheduler runs every 4 hours by default (configurable via environment variable)
- Import errors in the IDE are normal before installing dependencies

## Troubleshooting

**Import errors showing in VS Code:**
- These are expected before dependencies are installed
- Run `pip install -r requirements.txt` to resolve

**Application won't start:**
- Make sure virtual environment is activated
- Check that all dependencies are installed
- Verify Python 3.10+ is being used

**Tests failing:**
- Ensure test database is not locked
- Delete `test.db` and `default.db` files if they exist
- Re-run tests

## License

This project is for educational purposes as part of a Software Engineering course.
