# Academy LMS — Production release checklist

This repo contains:
- `backend/` — Django + DRF + JWT
- `frontend/` — Vite + Vue

## 1) Where your data is saved
Right now (local development), Django uses **SQLite**: `backend/db.sqlite3`.
When you deploy, you must use **PostgreSQL** (or any persistent DB). Otherwise your data will reset on every deploy.

## 2) Deploy backend (recommended: Render / Railway)
### Environment variables
Copy `backend/.env.example` and set these in the hosting panel:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS` (your API domain)
- `DATABASE_URL` (Postgres)
- `CORS_ALLOWED_ORIGINS` (your frontend domains)
- `CSRF_TRUSTED_ORIGINS` (your frontend domains)

### Build / start commands
- Build: `pip install -r requirements.txt`
- Migrate: `python manage.py migrate`
- Collect static: `python manage.py collectstatic --noinput`
- Start: Procfile already has gunicorn command

### Admin
Create admin user:
`python manage.py createsuperuser`
Then open `/admin/`.

## 3) Deploy frontend (Vercel / Netlify)
Set env:
- `VITE_API_BASE` = your backend domain (example `https://api.example.com`)

Build:
- `npm install`
- `npm run build`

## 4) File uploads (homework/submissions)
Currently uploaded files are stored in `backend/media/`.
Many platforms have **ephemeral filesystem**. For production you should:
- attach a persistent disk, OR
- move to S3-compatible storage (MinIO, Cloudflare R2, AWS S3) using `django-storages`.

If you want, I can wire S3/R2 settings into the project.

## 5) Mobile / public access notes
- Your frontend MUST call the production API domain (`VITE_API_BASE`).
- CORS must include your frontend domain(s) or phones won't be able to login.
- Use HTTPS for both frontend and backend.

## 6) Quick self-test before launching
1) Register user / login
2) Teacher creates group, assigns student
3) Teacher creates homework with attachment
4) Student downloads attachment, submits file
5) Teacher sees submission, downloads student file, sets grade + comment
6) Chat: direct + group messages

