# Academy LMS Monorepo (Django + Vue)

## Structure
- `backend/` Django REST API (JWT auth)
- `frontend/` Vue 3 + Vite app

## Quick start (Windows)
### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

Open: http://localhost:5173

## Auth flow
- Login: `POST /api/auth/login/` (username + password) -> returns access/refresh
- Me: `GET /api/auth/me/` (Bearer access token)

## Teacher dashboard
- `GET /api/teacher/dashboard/` -> groups + schedules + students_count

## Admin create teacher
- `POST /api/admin/teachers/` (ADMIN only) -> create TEACHER user

## Notes
- DB is SQLite for quick start. Switch to Postgres later.
- CORS is enabled for Vite dev server at port 5173.
