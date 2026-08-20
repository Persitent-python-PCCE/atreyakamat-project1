# SeatMeUp

Basic Flask, SQLAlchemy, and MySQL setup for the SeatMeUp ticket booking system.

## Setup

### 1. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2. Install requirements

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3. Configure MySQL

Copy `.env.example` to `.env` and set the MySQL values:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your MySQL username, password, host, port, and database name. Create the `seatmeup` database in MySQL before starting the application.

### 4. Start Flask

```powershell
flask --app app run --debug
```

### 5. Verify Flask is running

Open <http://127.0.0.1:5000/> in a browser or run:

```powershell
Invoke-WebRequest http://127.0.0.1:5000/
```

The response should contain `SeatMeUp is running.`.

### Verify the MySQL connection

With the virtual environment active and `.env` configured, run:

```powershell
flask --app app shell
```

Then enter:

```python
from sqlalchemy import text
from app import db
with db.engine.connect() as connection:
    connection.execute(text("SELECT 1"))
```

A successful command returns a SQLAlchemy result object without an exception. An error usually means the MySQL server is not running, the database does not exist, or the credentials in `.env` are incorrect.
