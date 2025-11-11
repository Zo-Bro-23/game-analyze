# Web App Setup Guide

This guide will help you set up the video pose analysis web application.

## Prerequisites

- Python 3.9+
- pip (Python package manager)
- A modern web browser

## Installation

### 1. Install Python Dependencies

```bash
pip install -r requirements_web.txt
```

### 2. Start the Backend Server

```bash
python web_app_backend.py
```

The server will start on `http://localhost:5000`

### 3. Open the Frontend

Open `web_app_frontend.html` in your web browser, or serve it using a simple HTTP server:

```bash
# Python 3
python -m http.server 8000

# Then open: http://localhost:8000/web_app_frontend.html
```

## Usage

1. **Upload Video**: Drag and drop a video file or click to browse
2. **Navigate Frames**: Use the slider or previous/next buttons
3. **Analyze Frame**: Click "Analyze Frame" to detect pose
4. **Toggle Overlay**: Turn on/off the pose skeleton overlay
5. **Play/Pause**: Control video playback

## API Endpoints

### `POST /api/upload`

Upload a video file.

**Request**: FormData with `video` file
**Response**: Video metadata (frames, fps, dimensions)

### `GET /api/video/<filename>/frame/<frame_index>`

Get a specific frame from the video.

**Response**: Base64 encoded image

### `POST /api/video/<filename>/analyze`

Analyze a specific frame.

**Request**: JSON with `frame_index`
**Response**: Annotated image and keypoints

### `POST /api/video/<filename>/analyze-batch`

Analyze multiple frames at once.

**Request**: JSON with `frame_indices` array
**Response**: Array of results

## Deployment

### Option 1: Railway (Easiest)

1. Create account at [railway.app](https://railway.app)
2. Connect your GitHub repository
3. Railway will automatically detect Python and deploy

### Option 2: Heroku

1. Install Heroku CLI
2. Create `Procfile`:
   ```
   web: python web_app_backend.py
   ```
3. Deploy:
   ```bash
   heroku create your-app-name
   git push heroku main
   ```

### Option 3: AWS/GCP/Azure

- Use EC2/Compute Engine/Virtual Machines
- Install Python dependencies
- Run the Flask app with gunicorn:
  ```bash
  pip install gunicorn
  gunicorn -w 4 -b 0.0.0.0:5000 web_app_backend:app
  ```

## Production Considerations

1. **Use a Production Server**: Replace Flask's development server with gunicorn or uWSGI
2. **Add Authentication**: Protect your API endpoints
3. **File Storage**: Use cloud storage (S3, etc.) instead of local storage
4. **Caching**: Cache analyzed frames to avoid reprocessing
5. **Rate Limiting**: Limit API requests per user
6. **Error Handling**: Add comprehensive error handling and logging
7. **Security**: Validate file types and sizes, sanitize filenames

## Troubleshooting

### Port Already in Use

```bash
# Change port in web_app_backend.py
app.run(debug=True, port=5001)
```

### CORS Errors

Make sure `flask-cors` is installed and CORS is enabled in the backend.

### Video Not Loading

- Check file format (MP4, AVI, MOV supported)
- Check file size (default limit is 500MB)
- Check browser console for errors

### Analysis Fails

- Check that MediaPipe is installed correctly
- Check server logs for errors
- Verify video file is valid

## Next Steps

- Add user authentication
- Add database for storing analysis results
- Add batch processing for entire videos
- Add export functionality (JSON, CSV)
- Add angle calculations
- Add pose comparison features
