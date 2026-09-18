# College Portal - Hosting Ready

This copy is prepared for deployment on Render.

## Local
```bash
pip install -r requirements.txt
python app.py
```

## Render
1. Upload/push the contents of this folder to a GitHub repository.
2. In Render, create a **New Web Service** and select that GitHub repository.
3. Render can use `render.yaml`, or set:
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
4. Deploy. Render will give you a public `onrender.com` URL.

Admin login:
- Username: `faruk`
- Password: `admin`

## Important database note
The project currently uses SQLite. This is fine for a demonstration, but Render's normal web-service filesystem is not persistent, so data added after deployment can be lost when the service is redeployed/restarted. For a production portal, move the database to PostgreSQL (or attach persistent storage where supported).

The bundled `instance/database.db` is retained in this hosting-ready copy so the current local data can be used if you commit that file to GitHub. The `.gitignore` has been adjusted so the database is not silently ignored.
