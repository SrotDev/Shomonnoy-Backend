# Project Description
Shomonnoy-Backend is a smart scheduling and coordination platform that helps city authorities manage and streamline road digging and construction works by multiple stakeholders without conflicts.


# Shomonnoy Backend Setup Guide
## Prerequisites

- [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/products/distribution) installed
- Python 3.11 (recommended)
- PostgreSQL installed
- PostgreSQL superuser access (to enable PostGIS)

## Step-by-Step Setup (Recommended: Conda)

### 1. Clone the Repository
```powershell
git clone <repo-url>
cd Shomonnoy-Backend
```

### 2. Create and Activate Conda Environment
```powershell
conda create -n shomonnoy python=3.11
conda activate shomonnoy
```

### 3. Install Core Dependencies via Conda
```powershell
conda install -c conda-forge django djangorestframework psycopg2 gdal python-decouple whitenoise
```

### 4. Install Remaining Dependencies via Pip
```powershell
pip install djangorestframework_simplejwt PyJWT sqlparse tzdata
```

### 5. Set Up PostgreSQL Database
- Open `psql` or PgAdmin as a superuser (e.g., `postgres`).
- Create a database and user:
	```sql
	CREATE DATABASE shomonnoydb;
	CREATE USER superadmin WITH PASSWORD 'yourpassword';
	GRANT ALL PRIVILEGES ON DATABASE shomonnoydb TO superadmin;
	```
- Enable PostGIS extension (run as superuser on the database):
	```sql
	\c shomonnoydb
	CREATE EXTENSION postgis;
	```

### 6. Configure Environment Variables
- Create a `.env` file in the project root (if using `python-decouple`).
	```env
	DB_NAME=shomonnoydb
	DB_USER=superadmin
	DB_PASSWORD=yourpassword
	DB_HOST=localhost
	DB_PORT=5432
	```
- Update `settings.py` to read from `.env` and use:
	```python
	'ENGINE': 'django.contrib.gis.db.backends.postgis',
	```

### 7. Run Migrations
```powershell
python manage.py makemigrations
python manage.py migrate
```

### 8. Create a Superuser (for admin access)
```powershell
python manage.py createsuperuser
```

### 9. Start the Development Server
```powershell
python manage.py runserver
```
Visit `http://127.0.0.1:8000/admin/` to log in.

### 10. Development Workflow
- Pull latest changes: `git pull`
- Create a new branch: `git checkout -b feature-branch`
- Make changes and commit: `git add . && git commit -m "Your message"`
- Push your branch: `git push origin feature-branch`
- Open a pull request for review.

### 11. Additional Notes
- Never commit secrets or `.env` files.
- Use migrations for all model changes.
- Communicate via repo issues and pull requests.
- If you encounter issues with GDAL or psycopg2, always install them via conda.

----