Frontend (Vite + React)

Run locally:

```powershell
cd "c:\Users\Priyanshu Pandey\.vscode\django learning\frontend"
npm install
npm run dev
```

Notes:
- The frontend reads an `access_token` from `localStorage` for Authorization (JWT from backend).
- API base can be configured with `VITE_API_BASE` env var (defaults to http://127.0.0.1:8000).
- Pages: Dashboard, Ingest (file upload), Review (approve/flag/reject), Audit.
