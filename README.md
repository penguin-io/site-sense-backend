# SiteSense - Backend

This is the server handling all the hard work - attendance, AI anomaly detection, etc., written in FastAPI

API docs generated via Swagger are available at HOST/docs

## Instructions

1. Clone the repo
2. Setup a virtual environment - 
```
python -m venv venv
source venv/bin/activate
```
3. Install dependencies - `pip install -r requirements.txt`
4. Start the development server - `uvicorn app.app:app --reload`
5. After creating initial admin user, grant superuser rights with - `UPDATE user set is_superuser = 1 where is_superuser = 0;` with `sqlite3 test.db`
