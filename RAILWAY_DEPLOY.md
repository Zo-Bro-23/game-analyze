# Deploying to Railway

This guide will walk you through deploying your video pose analysis web app to Railway.

## Prerequisites

- GitHub account (or Git repository)
- Railway account (free at [railway.app](https://railway.app))
- Your code pushed to a Git repository

## Step 1: Prepare Your Code

### 1.1 Create a Procfile

Create a file named `Procfile` (no extension) in your project root:

```
web: gunicorn web_app_backend:app --bind 0.0.0.0:$PORT
```

### 1.2 Update Backend for Production

The backend needs a few changes for Railway:

1. Use environment variable for port
2. Add gunicorn to requirements
3. Configure CORS for your domain

### 1.3 Update Requirements

Make sure `requirements_web.txt` includes gunicorn:

```
flask==3.0.0
flask-cors==4.0.0
opencv-python==4.8.1.78
mediapipe==0.10.8
numpy==1.26.2
werkzeug==3.0.1
gunicorn==21.2.0
```

## Step 2: Set Up Railway

### 2.1 Create Railway Account

1. Go to [railway.app](https://railway.app)
2. Sign up with GitHub (recommended)
3. Verify your email

### 2.2 Create New Project

1. Click "New Project"
2. Select "Deploy from GitHub repo"
3. Choose your repository
4. Railway will detect it's a Python project

### 2.3 Configure Build Settings

Railway should auto-detect Python, but verify:

1. Go to your project settings
2. Check "Build Command" (usually auto-detected)
3. Check "Start Command" (should use Procfile)

## Step 3: Configure Environment Variables

### 3.1 Set Port (Optional)

Railway automatically sets `PORT` environment variable, but you can verify:

1. Go to your project → Variables
2. Railway sets `PORT` automatically
3. No need to add it manually

### 3.2 Configure CORS (Important)

Update your backend to allow your Railway domain:

1. Go to your project → Settings → Domains
2. Copy your Railway domain (e.g., `your-app.railway.app`)
3. Add it to CORS configuration in backend

## Step 4: Update Backend Code

### 4.1 Update Port Configuration

Make sure your backend uses the `PORT` environment variable:

```python
import os
port = int(os.environ.get('PORT', 5000))
app.run(host='0.0.0.0', port=port)
```

### 4.2 Update CORS

Allow your Railway domain and localhost for testing:

```python
from flask_cors import CORS

# Allow Railway domain and localhost
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-app.railway.app",
            "http://localhost:8000",
            "http://localhost:3000"
        ]
    }
})
```

## Step 5: Deploy

### 5.1 Push to GitHub

```bash
git add .
git commit -m "Prepare for Railway deployment"
git push origin main
```

### 5.2 Railway Auto-Deploys

Railway will automatically:

1. Detect your Python project
2. Install dependencies from `requirements_web.txt`
3. Run your app using the Procfile
4. Deploy to a public URL

### 5.3 Monitor Deployment

1. Go to your Railway project
2. Click on "Deployments" tab
3. Watch the build logs
4. Wait for "Deploy Successful"

## Step 6: Get Your URL

### 6.1 Get Railway Domain

1. Go to your project → Settings → Domains
2. Copy your Railway domain
3. It will look like: `your-app.railway.app`

### 6.2 Test Your API

Test your API endpoint:

```bash
curl https://your-app.railway.app/api/health
```

You should get: `{"status":"healthy"}`

## Step 7: Update Frontend

### 7.1 Update API URL

Update `web_app_frontend.html`:

```javascript
// Change this:
const API_BASE = "http://localhost:5000/api";

// To your Railway URL:
const API_BASE = "https://your-app.railway.app/api";
```

### 7.2 Deploy Frontend

You have several options:

#### Option A: Serve from Railway (Simple)

1. Add frontend files to your repository
2. Serve them from Flask:

```python
@app.route('/')
def index():
    return send_from_directory('.', 'web_app_frontend.html')
```

#### Option B: Deploy to Netlify/Vercel (Recommended)

1. Create account on [Netlify](https://netlify.com) or [Vercel](https://vercel.com)
2. Connect your GitHub repo
3. Deploy frontend separately
4. Update API URL to Railway backend

#### Option C: Use GitHub Pages

1. Push frontend to GitHub
2. Enable GitHub Pages
3. Update API URL to Railway backend

## Step 8: Configure Storage

### 8.1 Railway Storage

Railway provides ephemeral storage (resets on redeploy). For persistent storage:

1. Use Railway's Volume (paid feature)
2. Or use cloud storage (S3, etc.)

### 8.2 Update Backend for Cloud Storage

For production, use cloud storage:

```python
import boto3

# Use S3 or similar for video storage
s3_client = boto3.client('s3')
bucket_name = os.environ.get('S3_BUCKET')
```

## Step 9: Monitor and Debug

### 9.1 View Logs

1. Go to Railway project → Deployments
2. Click on latest deployment
3. View logs in real-time

### 9.2 Common Issues

#### Port Already in Use

- Railway sets `PORT` automatically
- Make sure you're using `os.environ.get('PORT')`

#### CORS Errors

- Check CORS configuration
- Verify frontend URL is allowed

#### Build Fails

- Check `requirements_web.txt`
- Verify Python version (Railway uses 3.11 by default)

#### App Crashes

- Check logs for errors
- Verify all dependencies are installed
- Check file permissions

## Step 10: Custom Domain (Optional)

### 10.1 Add Custom Domain

1. Go to project → Settings → Domains
2. Click "Add Domain"
3. Enter your domain
4. Follow DNS configuration instructions

### 10.2 Update CORS

Add your custom domain to CORS:

```python
CORS(app, resources={
    r"/api/*": {
        "origins": [
            "https://your-custom-domain.com",
            "https://your-app.railway.app"
        ]
    }
})
```

## Troubleshooting

### Build Fails

**Error**: `ModuleNotFoundError: No module named 'mediapipe'`

**Solution**:

- Check `requirements_web.txt` includes all dependencies
- Verify Python version compatibility
- Check build logs for specific errors

### App Won't Start

**Error**: `Port already in use`

**Solution**:

- Use `PORT` environment variable
- Don't hardcode port number
- Use gunicorn with `--bind 0.0.0.0:$PORT`

### CORS Errors

**Error**: `CORS policy: No 'Access-Control-Allow-Origin'`

**Solution**:

- Update CORS configuration
- Add your frontend URL to allowed origins
- Check Railway domain is correct

### Video Upload Fails

**Error**: `File too large` or `Upload failed`

**Solution**:

- Check file size limits
- Use cloud storage for large files
- Increase timeout settings

## Cost Considerations

### Railway Free Tier

- $5 free credit per month
- 500 hours of usage
- 100 GB bandwidth
- Ephemeral storage only

### Paid Plans

- $5/month for Hobby plan
- $20/month for Pro plan
- Includes persistent storage
- More resources

## Next Steps

1. ✅ Deploy backend to Railway
2. ✅ Deploy frontend to Netlify/Vercel
3. ✅ Test end-to-end
4. ✅ Set up monitoring
5. ✅ Add error tracking (Sentry, etc.)
6. ✅ Set up CI/CD
7. ✅ Add authentication
8. ✅ Scale as needed

## Additional Resources

- [Railway Documentation](https://docs.railway.app)
- [Railway Discord](https://discord.gg/railway)
- [Flask Deployment Guide](https://flask.palletsprojects.com/en/3.0.x/deploying/)

## Quick Reference

### Railway CLI (Optional)

Install Railway CLI:

```bash
npm i -g @railway/cli
railway login
railway init
railway up
```

### Environment Variables

Set in Railway dashboard:

- `PORT` - Automatically set by Railway
- `FLASK_ENV` - Set to `production`
- `CORS_ORIGINS` - Your frontend URLs

### Useful Commands

```bash
# View logs
railway logs

# Open shell
railway shell

# View variables
railway variables
```

## Success Checklist

- [ ] Backend deployed to Railway
- [ ] API health check works
- [ ] Frontend deployed and connected
- [ ] Video upload works
- [ ] Frame analysis works
- [ ] CORS configured correctly
- [ ] Custom domain set up (optional)
- [ ] Monitoring set up
- [ ] Error handling in place

Congratulations! Your app is now live on Railway! 🚀
