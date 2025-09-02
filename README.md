# Shomonnoy-Backend
A smart scheduling and coordination platform that helps city authorities manage and streamline road digging and construction works by multiple stakeholders without conflicts.


## Shomonnoy Backend Developer Setup Guide

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd <project-folder>
```

### 2. Create a Virtual Environment
```bash
python -m venv .venv
```
Activate it:
- **Windows:** `.venv\Scripts\activate`
- **Linux/Mac:** `source .venv/bin/activate`

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Set Up PostgreSQL Database
- Install PostgreSQL if not already installed.
- Create a database (e.g., `shomonnoydb`) and a user (e.g., `superadmin`).
- Grant privileges to the user.

### 5. Configure Environment Variables
- Create a `.env` file in the project root (if using `django-environ` or `python-decouple`).
- Add your database credentials:
	```
	DB_NAME=shomonnoydb
	DB_USER=superadmin
	DB_PASSWORD=yourpassword
	DB_HOST=localhost
	DB_PORT=5432
	```
- Update `settings.py` to read from `.env`.

### 6. Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Create a Superuser (for admin access)
```bash
python manage.py createsuperuser
```

### 8. Start the Development Server
```bash
python manage.py runserver
```
Visit `http://127.0.0.1:8000/admin/` to log in.

### 9. Development Workflow
- Pull latest changes: `git pull`
- Create a new branch for your feature: `git checkout -b feature-branch`
- Make changes and commit: `git add . && git commit -m "Your message"`
- Push your branch: `git push origin feature-branch`
- Open a pull request for review.

### 10. Additional Notes
- Never commit secrets or `.env` files.
- Use migrations for all model changes.
- Communicate via repo issues and pull requests.
