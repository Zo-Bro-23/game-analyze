# Railway Deployment - Quick Start

## 🚀 Deploy in 5 Minutes

### Step 1: Prepare Files

Make sure you have these files in your project:

- ✅ `web_app_backend.py` - Flask backend
- ✅ `requirements_web.txt` - Python dependencies
- ✅ `Procfile` - Railway start command
- ✅ `runtime.txt` - Python version (optional)

### Step 2: Push to GitHub

```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

### Step 3: Deploy on Railway

1. Go to [railway.app](https://railway.app)
2. Click "New Project"
3. Select "Deploy from GitHub repo"
4. Choose your repository
5. Railway will auto-detect Python and deploy!

### Step 4: Get Your URL

1. Go to your project → Settings → Domains
2. Copy your Railway URL (e.g., `your-app.railway.app`)
3. Test: `https://your-app.railway.app/api/health`

### Step 5: Update Frontend

In `web_app_frontend.html`, change:

```javascript
// Change this line:
const API_BASE = "http://localhost:5000/api";

// To your Railway URL:
const API_BASE = "https://your-app.railway.app/api";
```

### Step 6: Configure CORS (Important!)

In Railway dashboard:

1. Go to your project → Variables
2. Add new variable:
   - Key: `CORS_ORIGINS`
   - Value: `https://your-frontend-url.com,http://localhost:8000`
3. Save and redeploy

## ✅ That's It!

Your app should now be live on Railway!

## 🔧 Troubleshooting

### Build Fails

- Check `requirements_web.txt` has all dependencies
- Check Railway logs for errors

### CORS Errors

- Update `CORS_ORIGINS` environment variable
- Include your frontend URL

### App Won't Start

- Check `Procfile` is correct
- Verify port is set correctly (Railway sets `PORT` automatically)

## 📚 More Details

See `RAILWAY_DEPLOY.md` for comprehensive guide.
