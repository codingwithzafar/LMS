# Railway deploy (Backend + Frontend)

Quyidagi yo'l bilan siz loyihani Railway'ga chiqarasiz.

## 1) Backend (Django) — Railway

1. Railway'da **New Project → Deploy from GitHub Repo** qiling.
2. **Add Service → Database → Postgres** qo'shing.
3. Backend service uchun **Settings → Root Directory** ni `backend` qilib qo'ying.
4. Backend service **Variables** ga quyidagilarni kiriting:

   - `DJANGO_SECRET_KEY` = (uzun random)
   - `DJANGO_DEBUG` = `0`
   - `DJANGO_ALLOWED_HOSTS` = `.railway.app,localhost,127.0.0.1`
   - `CORS_ALLOWED_ORIGINS` = `https://<FRONTEND_DOMAIN>`
   - `CSRF_TRUSTED_ORIGINS` = `https://<FRONTEND_DOMAIN>,https://<BACKEND_DOMAIN>`

   **Eslatma:** Railway Postgres qo'shganda `DATABASE_URL` avtomatik beriladi — backend `settings.py` uni o'zi ishlatadi.

5. Backend service **Start Command** (agar so'rasa):

   ```
   bash start.sh
   ```

6. Deploy bo'lgandan keyin admin yaratish uchun (Railway → service → Shell):

   ```
   python manage.py createsuperuser
   ```

### Media (upload qilingan fayllar) haqida
Railway **ephemeral filesystem**: server restart bo'lsa `backend/media/` ichidagi fayllar yo'qolishi mumkin.

**Prod uchun tavsiya:** S3 (Cloudflare R2 / AWS S3) ga ko'chirish. Hozircha demo/test uchun Railway'da ishlaydi, lekin ommaga chiqqanda S3 ga o'tkazish shart.

---

## 2) Frontend (Vue/Vite) — Railway

1. Railway'da **Add Service → Deploy from GitHub Repo** (yoki shu project ichida yangi service) qiling.
2. Frontend service uchun **Root Directory** ni `frontend` qiling.
3. Frontend service **Variables** ga:

   - `VITE_API_BASE` = `https://<BACKEND_DOMAIN>`

4. **Build Command**:

   ```
   npm ci && npm run build
   ```

5. **Start Command**:

   ```
   npm run preview -- --host 0.0.0.0 --port $PORT
   ```

---

## 3) Telefon (mobile) uchun
- UI responsive ishlaydi (grid va chat layout mobilga mos). 
- Frontend domain'ni backend `CORS_ALLOWED_ORIGINS` ga qo'shishni unutmang.

---

## 4) Tez test
1. Frontend ochiladi
2. Login/registration
3. Teacher guruh yaratadi, student qo'shadi
4. Chat direct + group ishlaydi
5. Homework upload/download ishlaydi
