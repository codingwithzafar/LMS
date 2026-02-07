# Academy LMS — Deploy (prod)

## Data qayerga saqlanyapti?

- **User/Guruh/Vazifa/Submission/Xabar** — Django databasega saqlanadi.
- Devda: odatda **SQLite** (`backend/db.sqlite3`).
- Prodda: **Postgres** tavsiya (Render/Railway beradi) — `DATABASE_URL` bilan.

> Muhim: **File upload** (homework attachment, student submission file) hozir Django `MEDIA_ROOT` ga yoziladi.
> Ko‘p hostinglarda (Render kabi) disk **ephemeral** bo‘lishi mumkin — restart bo‘lsa fayl yo‘qolishi mumkin.
> Prod uchun: persistent disk yoki S3/R2 storage ishlating.

## 1) Backend deploy (Render / Railway)

### Environment variables
Backend servicega `backend/.env.example` dagilarni qo‘ying:
- `DJANGO_SECRET_KEY`
- `DJANGO_DEBUG=0`
- `DJANGO_ALLOWED_HOSTS=your-api-domain.com`
- `DATABASE_URL` (Postgres)
- `CORS_ALLOWED_ORIGINS=https://your-frontend-domain.com`
- `CSRF_TRUSTED_ORIGINS=https://your-frontend-domain.com`

### Build / start
- Install: `pip install -r requirements.txt`
- Migrate: `python manage.py migrate`
- Collect static: `python manage.py collectstatic --noinput`
- Start: `gunicorn config.wsgi:application --bind 0.0.0.0:$PORT`

### Admin
- `python manage.py createsuperuser`

## 2) Frontend deploy (Vercel / Netlify)

Frontend env:
- `VITE_API_BASE=https://your-api-domain.com`

Commands:
- `npm install`
- `npm run build`

## 3) Telefonlardan ishlashi uchun

- Frontend + Backend **https** bo‘lsin (mixed content bo‘lmasin).
- CORS origin to‘g‘ri qo‘yilgan bo‘lsin.
- API domain hamma telefondan ochiladigan bo‘lsin.

## 4) Tez tekshiruv (go-live)

1. Login/Register
2. Teacher: group create, add students
3. Teacher: homework create + attachment upload
4. Student: homework download + submit (text + file)
5. Teacher: submission ko‘rish, grade/comment
6. Chat: direct + group

