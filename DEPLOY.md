# Put it on GitHub and get a live link

You end up with **one link** (the frontend) that anyone can open. Backend + database run on Render (free),
frontend runs on Vercel (free). Total time: about 15 minutes.

## 1. Push to GitHub

Create an empty repo on github.com (e.g. `campus-placement`, no README), then in the project folder:

```bash
git init
git add .
git commit -m "Campus placement system: company cards, approval workflow, two reports"
git branch -M main
git remote add origin https://github.com/<your-username>/campus-placement.git
git push -u origin main
```

(`.gitignore` already keeps `venv`, `node_modules`, `db.sqlite3` and `.env` out of the repo.)

## 2. Backend + database on Render

1. render.com -> **New +** -> **Blueprint** -> connect the GitHub repo. Render reads `render.yaml`
   and creates the API service and a Postgres database.
2. When asked, set **ADMIN_PASSWORD** (the admin login password). Leave **FRONTEND_URL** empty for now.
3. Wait for the deploy to finish. Your API link looks like `https://campus-placement-api.onrender.com`.
   The build automatically runs migrations and loads the demo data.

## 3. Frontend on Vercel

1. vercel.com -> **Add New Project** -> import the same repo.
2. **Root Directory:** `frontend`. Framework: Vite (auto-detected).
3. **Environment variable:** `VITE_API_URL` = `https://campus-placement-api.onrender.com/api`
4. Deploy. Your link is e.g. `https://campus-placement.vercel.app` <- **this is the link you share.**

## 4. Connect the two

In Render -> your API service -> **Environment** -> set `FRONTEND_URL` = your Vercel link
(no trailing slash) -> save (it redeploys). Now login works from the live site.

## Notes

- Render's free plan sleeps after ~15 min idle, so the first request after a break takes ~30-60 s. Open the
  link once before presenting.
- Free Render Postgres databases expire after a limited period; fine for a college demo.
- The demo passwords in the README are public once the repo is public. Change `ADMIN_PASSWORD`, and set
  `SEED_DEMO_DATA=false` in Render if you want an empty system.
