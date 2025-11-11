"""
Flask backend for video pose analysis web app.
This reuses your existing analysis code.
"""

from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import cv2
import mediapipe as mp
import numpy as np
import os
import tempfile
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__, static_folder='.')

# Configure CORS - allow all origins since we're serving frontend from same domain
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'mp4', 'avi', 'mov', 'mkv'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# MediaPipe setup (same as your main.py)
mp_pose = mp.solutions.pose

# Simplified skeleton connections (from main.py)
SIMPLE_CONNECTIONS = [
    (mp_pose.PoseLandmark.NOSE, mp_pose.PoseLandmark.LEFT_SHOULDER),
    (mp_pose.PoseLandmark.NOSE, mp_pose.PoseLandmark.RIGHT_SHOULDER),
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER),
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP),
    (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP),
    (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP),
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW),
    (mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST),
    (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW),
    (mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
    (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE),
    (mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE),
    (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE),
    (mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE),
]

KEY_LANDMARKS = [
    mp_pose.PoseLandmark.NOSE,
    mp_pose.PoseLandmark.LEFT_SHOULDER,
    mp_pose.PoseLandmark.RIGHT_SHOULDER,
    mp_pose.PoseLandmark.LEFT_ELBOW,
    mp_pose.PoseLandmark.RIGHT_ELBOW,
    mp_pose.PoseLandmark.LEFT_WRIST,
    mp_pose.PoseLandmark.RIGHT_WRIST,
    mp_pose.PoseLandmark.LEFT_HIP,
    mp_pose.PoseLandmark.RIGHT_HIP,
    mp_pose.PoseLandmark.LEFT_KNEE,
    mp_pose.PoseLandmark.RIGHT_KNEE,
    mp_pose.PoseLandmark.LEFT_ANKLE,
    mp_pose.PoseLandmark.RIGHT_ANKLE,
]


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def analyze_frame(frame, pose):
    """Analyze a frame and return annotated version with pose overlay."""
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(image_rgb)
    
    annotated = frame.copy()
    h, w, _ = frame.shape
    
    keypoints = []
    
    if result.pose_landmarks:
        # Draw connections
        for connection in SIMPLE_CONNECTIONS:
            start_idx = connection[0].value
            end_idx = connection[1].value
            start_point = result.pose_landmarks.landmark[start_idx]
            end_point = result.pose_landmarks.landmark[end_idx]
            
            if start_point.visibility > 0.5 and end_point.visibility > 0.5:
                start = (int(start_point.x * w), int(start_point.y * h))
                end = (int(end_point.x * w), int(end_point.y * h))
                cv2.line(annotated, start, end, (0, 0, 255), 2)
        
        # Draw landmarks
        for landmark_idx in KEY_LANDMARKS:
            lm = result.pose_landmarks.landmark[landmark_idx.value]
            if lm.visibility > 0.5:
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(annotated, (x, y), 3, (0, 255, 0), -1)
        
        # Extract keypoints
        for lm in result.pose_landmarks.landmark:
            keypoints.append({
                'x': float(lm.x * w),
                'y': float(lm.y * h),
                'z': float(lm.z * w),
                'visibility': float(lm.visibility)
            })
        
        return annotated, keypoints, True
    else:
        return annotated, [], False


@app.route('/')
def index():
    """Serve the frontend HTML file."""
    return send_from_directory('.', 'web_app_frontend.html')


@app.route('/api/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})


@app.route('/api/upload', methods=['POST'])
def upload_video():
    """Upload video and return video metadata."""
    if 'video' not in request.files:
        return jsonify({'error': 'No video file'}), 400
    
    file = request.files['video']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not allowed_file(file.filename):
        return jsonify({'error': 'Invalid file type'}), 400
    
    filename = secure_filename(file.filename)
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    
    # Get video metadata
    cap = cv2.VideoCapture(filepath)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    duration = total_frames / fps if fps > 0 else 0
    cap.release()
    
    return jsonify({
        'filename': filename,
        'total_frames': total_frames,
        'fps': fps,
        'width': width,
        'height': height,
        'duration': duration
    })


@app.route('/api/video/<filename>/frame/<int:frame_index>', methods=['GET'])
def get_frame(filename, frame_index):
    """Get a specific frame from the video."""
    # frame_index is already in the URL path
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Video not found'}), 404
    
    cap = cv2.VideoCapture(filepath)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return jsonify({'error': 'Frame not found'}), 404
    
    # Encode frame as JPEG
    _, buffer = cv2.imencode('.jpg', frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return jsonify({
        'frame_index': frame_index,
        'image': f'data:image/jpeg;base64,{frame_base64}'
    })


@app.route('/api/video/<filename>/analyze', methods=['POST'])
def analyze_frame_endpoint(filename):
    """Analyze a specific frame and return annotated image and keypoints."""
    data = request.json
    frame_index = data.get('frame_index', 0)
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Video not found'}), 404
    
    # Read frame
    cap = cv2.VideoCapture(filepath)
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
    ret, frame = cap.read()
    cap.release()
    
    if not ret:
        return jsonify({'error': 'Frame not found'}), 404
    
    # Analyze frame
    pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)
    annotated_frame, keypoints, has_pose = analyze_frame(frame, pose)
    pose.close()
    
    # Encode annotated frame as JPEG
    _, buffer = cv2.imencode('.jpg', annotated_frame)
    frame_base64 = base64.b64encode(buffer).decode('utf-8')
    
    return jsonify({
        'frame_index': frame_index,
        'has_pose': has_pose,
        'keypoints': keypoints,
        'annotated_image': f'data:image/jpeg;base64,{frame_base64}'
    })


@app.route('/api/video/<filename>/analyze-batch', methods=['POST'])
def analyze_batch_frames(filename):
    """Analyze multiple frames at once."""
    data = request.json
    frame_indices = data.get('frame_indices', [])
    filepath = os.path.join(UPLOAD_FOLDER, secure_filename(filename))
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'Video not found'}), 404
    
    if len(frame_indices) > 50:  # Limit batch size
        return jsonify({'error': 'Too many frames (max 50)'}), 400
    
    cap = cv2.VideoCapture(filepath)
    pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)
    
    results = []
    for frame_index in frame_indices:
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_index)
        ret, frame = cap.read()
        if ret:
            annotated_frame, keypoints, has_pose = analyze_frame(frame, pose)
            _, buffer = cv2.imencode('.jpg', annotated_frame)
            frame_base64 = base64.b64encode(buffer).decode('utf-8')
            results.append({
                'frame_index': frame_index,
                'has_pose': has_pose,
                'keypoints': keypoints,
                'annotated_image': f'data:image/jpeg;base64,{frame_base64}'
            })
    
    cap.release()
    pose.close()
    
    return jsonify({'results': results})


if __name__ == '__main__':
    # Use PORT environment variable (Railway sets this automatically)
    # Default to 5000 for local development
    port = int(os.environ.get('PORT', 5000))
    # Disable debug mode in production
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug)

