# Price Comparison Web Scraper

**Project ID:** P60  
**Course:** UE23CS341A  
**Academic Year:** 2025  
**Semester:** 5th Sem  
**Campus:** EC  
**Branch:** CSE  
**Section:** D  
**Team:** GKIsh

This project is a backend service for scraping product prices from e-commerce websites and exposing the aggregated data via a RESTful API.

This project was built using Python 3.10, FastAPI, SQLAlchemy (with SQLite), and BeautifulSoup.

## 🧑‍💻 Development Team (GKIsh)

- [@KartikPalcharla](https://github.com/KartikPalcharla) - Scrum Master
- [@Nightwing000](https://github.com/Nightwing000) - Developer Team
- [@gogodoesnotcode](https://github.com/gogodoesnotcode) - Developer Team
- [@Ishan-Mishra21](https://github.com/Ishan-Mishra21) - Developer Team

## 👨‍🏫 Teaching Assistant

- [@dredblackblue](https://github.com/dredblackblue)
- [@shreyavijay2022](https://github.com/shreyavijay2022)
- [@Meenakshi4d5f](https://github.com/Meenakshi4d5f)
- [@tejaswiniv27](https://github.com/tejaswiniv27)
- [@Shriya285](https://github.com/Shriya285)

## 👨‍⚖ Faculty Supervisor

- *No valid faculty GitHub username found*

## 📁 Project Structure

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
    * `test_database.py`: Database layer tests.
    * `test_scraper.py`: Scraper component tests.
    * `test_scheduler.py`: Scheduler component tests.
    * `test_main.py`: Application entry point tests.
* `.github/workflows/`: Contains the CI/CD pipeline configuration.
* `.pylintrc`: Configuration for the Pylint linter.
* `pytest.ini`: Configuration for Pytest and the `pytest-cov` coverage tool.

## 🚀 How to Run Locally

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)

### Installation

1.  **Clone the repository:**
    bash
    git clone https://github.com/pestechnology/PESU_EC_CSE_D_P60_Web_Scraper_for_Price_Comparison_GKIsh.git
    cd PESU_EC_CSE_D_P60_Web_Scraper_for_Price_Comparison_GKIsh
    

2.  **Create a virtual environment and install dependencies:**
    bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    pip install -r requirements.txt
    

3.  **Run the application:**
    The application uses environment variables for configuration (see `src/app/core.py`). You can set them in your terminal:
    bash
    # Linux/Mac
    export ADMIN_API_KEY="my-secret-key"
    export CLIENT_API_KEY="my-client-key"
    export DATABASE_URL="sqlite:///./test.db"

    # Windows PowerShell
    $env:ADMIN_API_KEY="my-secret-key"
    $env:CLIENT_API_KEY="my-client-key"
    $env:DATABASE_URL="sqlite:///./test.db"

    # Run the server
    uvicorn src.app.main:app --reload
    

4.  **Access the API:**
    The API will be running at `http://127.0.0.1:8000`.
    You can access the automatic interactive documentation at `http://127.0.0.1:8000/docs`.

## 📡 API Endpoints

All API keys are passed via the `x-api-key` header.

### Client Endpoints (Requires `CLIENT_API_KEY`)

* **`GET /api/v1/search`**: Search for products.
    * **Query Param:** `q` (string) - The product name to search for.
    * **Success Response (200):**
        json
        [
          {
            "id": 1,
            "name": "Example Product",
            "price": 99.99,
            "url": "http://example.com/product/1",
            "scraped_at": "2025-11-10T12:00:00Z"
          }
        ]
        

### Admin Endpoints (Requires `ADMIN_API_KEY`)

* **`POST /api/v1/admin/target`**: Add a new scrape target.
    * **Request Body:**
        json
        {
          "name": "Mock Store",
          "base_url": "http://example.com/products",
          "name_selector": "h1.product-title",
          "price_selector": "span.product-price",
          "url_selector": "a.product-link"
        }
        
    * **Success Response (201):** The newly created target object.

* **`POST /api/v1/admin/scrape`**: Trigger scraping for all targets.
    * **Success Response (200):**
        json
        {
          "message": "Scraping started"
        }
        

* **`GET /api/v1/admin/logs`**: Get the 10 most recent scrape logs.
    * **Success Response (200):**
        json
        [
          {
            "id": 1,
            "target_name": "Mock Store",
            "status": "success",
            "products_found": 5,
            "created_at": "2025-11-10T12:05:00Z"
          }
        ]
        

## 🧪 Testing

Run the test suite with coverage:

bash
# Run all tests with coverage report
pytest tests/ -v

# Run tests with coverage threshold check (75% minimum)
pytest tests/ --cov=src/app --cov-report=html --cov-report=term

# Run specific test files
pytest tests/test_unit.py -v
pytest tests/test_integration.py -v
pytest tests/test_system.py -v


Current test coverage: **91.49%** (exceeds 75% requirement)

## 🔄 CI/CD Pipeline

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

## 🛠 Development Guidelines

### Branching Strategy
- `main`: Production-ready code
- `develop`: Development branch
- `feature/*`: Feature branches
- `bugfix/*`: Bug fix branches
- `test/*`: Test-related branches

### Commit Messages
Follow conventional commit format:
- `feat:` New features
- `fix:` Bug fixes
- `docs:` Documentation changes
- `style:` Code style changes
- `refactor:` Code refactoring
- `test:` Test-related changes

### Code Review Process
1. Create feature branch from `develop`
2. Make changes and commit
3. Create Pull Request to `develop`
4. Request review from team members
5. Merge after approval

## 📄 License

This project is developed for educational purposes as part of the PES University UE23CS341A curriculum.

---

**Course:** UE23CS341A  
**Institution:** PES University  
**Academic Year:** 2025  
**Semester:** 5th Sem