#!/usr/bin/env python3
import cv2
import mediapipe as mp
import numpy as np

VIDEO_PATH = "./video2.mp4"
USE_INTERACTIVE_PICKER = True  # Set to False to use FRAME_INDEX directly
FRAME_INDEX = 895  # Default frame (used if USE_INTERACTIVE_PICKER is False)

mp_pose = mp.solutions.pose
mp_drawing = mp.solutions.drawing_utils

# Simplified skeleton: only key joints (nose, shoulders, elbows, wrists, hips, knees, ankles)
SIMPLE_CONNECTIONS = [
    # Head to shoulders
    (mp_pose.PoseLandmark.NOSE, mp_pose.PoseLandmark.LEFT_SHOULDER),
    (mp_pose.PoseLandmark.NOSE, mp_pose.PoseLandmark.RIGHT_SHOULDER),
    # Torso
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.RIGHT_SHOULDER),
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_HIP),
    (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_HIP),
    (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.RIGHT_HIP),
    # Left arm
    (mp_pose.PoseLandmark.LEFT_SHOULDER, mp_pose.PoseLandmark.LEFT_ELBOW),
    (mp_pose.PoseLandmark.LEFT_ELBOW, mp_pose.PoseLandmark.LEFT_WRIST),
    # Right arm
    (mp_pose.PoseLandmark.RIGHT_SHOULDER, mp_pose.PoseLandmark.RIGHT_ELBOW),
    (mp_pose.PoseLandmark.RIGHT_ELBOW, mp_pose.PoseLandmark.RIGHT_WRIST),
    # Left leg
    (mp_pose.PoseLandmark.LEFT_HIP, mp_pose.PoseLandmark.LEFT_KNEE),
    (mp_pose.PoseLandmark.LEFT_KNEE, mp_pose.PoseLandmark.LEFT_ANKLE),
    # Right leg
    (mp_pose.PoseLandmark.RIGHT_HIP, mp_pose.PoseLandmark.RIGHT_KNEE),
    (mp_pose.PoseLandmark.RIGHT_KNEE, mp_pose.PoseLandmark.RIGHT_ANKLE),
]

# Key landmarks to draw (only main joints)
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

def read_frame(path, frame_idx):
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {path}")
    cap.set(cv2.CAP_PROP_POS_FRAMES, frame_idx)
    ok, frame = cap.read()
    cap.release()
    if not ok:
        raise RuntimeError(f"Could not grab frame {frame_idx}")
    return frame

def analyze_and_annotate_frame(frame, pose):
    """Analyze a frame and return annotated version with pose overlay."""
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    result = pose.process(image_rgb)
    
    annotated = frame.copy()
    h, w, _ = frame.shape
    
    if result.pose_landmarks:
        # Draw only the simplified connections
        for connection in SIMPLE_CONNECTIONS:
            start_idx = connection[0].value
            end_idx = connection[1].value
            start_point = result.pose_landmarks.landmark[start_idx]
            end_point = result.pose_landmarks.landmark[end_idx]
            
            # Only draw if both landmarks are visible
            if start_point.visibility > 0.5 and end_point.visibility > 0.5:
                start = (int(start_point.x * w), int(start_point.y * h))
                end = (int(end_point.x * w), int(end_point.y * h))
                cv2.line(annotated, start, end, (0, 0, 255), 2)
        
        # Draw only key landmarks
        for landmark_idx in KEY_LANDMARKS:
            lm = result.pose_landmarks.landmark[landmark_idx.value]
            if lm.visibility > 0.5:
                x = int(lm.x * w)
                y = int(lm.y * h)
                cv2.circle(annotated, (x, y), 3, (0, 255, 0), -1)
        
        return annotated, True
    else:
        return annotated, False

def pick_frame_interactive(video_path):
    """Interactive video player to pick a frame for analysis.
    
    Controls:
    - Space/Enter: Pause/Play
    - [,] or [.]: Previous/Next frame (single step)
    - [-] or [=]: Jump 10 frames backward/forward
    - 'g': Go to specific frame number
    - 'a': Analyze current frame (save image and show overlay)
    - 't': Toggle pose overlay on/off
    - 'q' or ESC: Quit and return frame number
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise RuntimeError(f"Cannot open video: {video_path}")
    
    # Get video properties
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    
    # Initialize pose detection
    pose = mp_pose.Pose(static_image_mode=True, model_complexity=2)
    
    current_frame = 0
    playing = False
    show_overlay = False
    selected_frame = None
    
    print(f"\n=== Video Frame Picker ===")
    print(f"Total frames: {total_frames}")
    print(f"FPS: {fps:.2f}")
    print(f"\nControls:")
    print(f"  Space/Enter: Play/Pause")
    print(f"  [,] or [.]: Previous/Next frame (single step)")
    print(f"  [-] or [=]: Jump 10 frames backward/forward")
    print(f"  'g': Go to specific frame number")
    print(f"  'a': Analyze & save current frame (toggles overlay)")
    print(f"  't': Toggle pose overlay on/off")
    print(f"  'q' or ESC: Quit and return frame number")
    print(f"========================\n")
    
    while True:
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
        ret, frame = cap.read()
        
        if not ret:
            break
        
        # Apply pose overlay if enabled
        if show_overlay:
            annotated_frame, has_pose = analyze_and_annotate_frame(frame, pose)
            display = annotated_frame
            if not has_pose:
                display = frame.copy()  # Fallback if no pose detected
        else:
            display = frame.copy()
        
        h, w = display.shape[:2]
        
        # Draw info text
        overlay_status = "ON" if show_overlay else "OFF"
        info_text = [
            f"Frame: {current_frame}/{total_frames}",
            f"Time: {current_frame/fps:.2f}s",
            f"Pose Overlay: {overlay_status}",
            "Controls: [Space]Play [,/.]Nav [-]/[=]Jump10 [a]Analyze [t]Toggle [q]Quit"
        ]
        y_offset = 30
        for i, text in enumerate(info_text):
            cv2.putText(display, text, (10, y_offset + i * 25),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        
        # Draw frame indicator bar
        bar_width = int((current_frame / total_frames) * w)
        cv2.rectangle(display, (0, h-10), (bar_width, h), (0, 255, 0), -1)
        cv2.rectangle(display, (0, h-10), (w, h), (255, 255, 255), 2)
        
        cv2.imshow("Video Frame Picker - Press 'a' to analyze, 'q' to quit", display)
        
        # Handle keyboard input
        key = cv2.waitKey(30 if playing else 0) & 0xFF
        
        if key == ord('q') or key == 27:  # 'q' or ESC
            selected_frame = current_frame
            break
        elif key == ord(' ') or key == 13:  # Space or Enter
            playing = not playing
        elif key == ord('a'):  # Analyze and save
            annotated_frame, has_pose = analyze_and_annotate_frame(frame, pose)
            if has_pose:
                # Save annotated frame
                output_filename = f"frame_{current_frame:05d}.jpg"
                cv2.imwrite(output_filename, annotated_frame)
                print(f"Analyzed and saved frame {current_frame} to {output_filename}")
                # Toggle overlay on and update display immediately
                show_overlay = True
                display = annotated_frame
                # Redraw display with overlay
                h, w = display.shape[:2]
                overlay_status = "ON"
                info_text = [
                    f"Frame: {current_frame}/{total_frames}",
                    f"Time: {current_frame/fps:.2f}s",
                    f"Pose Overlay: {overlay_status}",
                    "Controls: [Space]Play [,/.]Nav [-]/[=]Jump10 [a]Analyze [t]Toggle [q]Quit"
                ]
                y_offset = 30
                for i, text in enumerate(info_text):
                    cv2.putText(display, text, (10, y_offset + i * 25),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                bar_width = int((current_frame / total_frames) * w)
                cv2.rectangle(display, (0, h-10), (bar_width, h), (0, 255, 0), -1)
                cv2.rectangle(display, (0, h-10), (w, h), (255, 255, 255), 2)
                cv2.imshow("Video Frame Picker - Press 'a' to analyze, 'q' to quit", display)
            else:
                print(f"No pose detected in frame {current_frame}")
        elif key == ord('t'):  # Toggle overlay
            show_overlay = not show_overlay
            print(f"Pose overlay: {'ON' if show_overlay else 'OFF'}")
        elif key == ord('[') or key == ord(','):  # Alternative: [ or , for previous
            current_frame = max(0, current_frame - 1)
            playing = False
        elif key == ord(']') or key == ord('.'):  # Alternative: ] or . for next
            current_frame = min(total_frames - 1, current_frame + 1)
            playing = False
        elif key == ord('-') or key == ord('_'):  # Alternative: - for jump back
            current_frame = max(0, current_frame - 10)
            playing = False
        elif key == ord('=') or key == ord('+'):  # Alternative: = for jump forward
            current_frame = min(total_frames - 1, current_frame + 10)
            playing = False
        elif key == ord('g'):  # Go to frame
            cv2.destroyAllWindows()  # Close window temporarily for input
            try:
                frame_input = input(f"\nEnter frame number (0-{total_frames-1}): ")
                frame_num = int(frame_input)
                if 0 <= frame_num < total_frames:
                    current_frame = frame_num
                    playing = False
                else:
                    print(f"Invalid frame number. Must be between 0 and {total_frames-1}")
            except ValueError:
                print("Invalid input. Please enter a number.")
            except:
                pass
        
        # Auto-advance if playing
        if playing:
            current_frame += 1
            if current_frame >= total_frames:
                current_frame = 0  # Loop back
    
    cap.release()
    pose.close()
    cv2.destroyAllWindows()
    
    if selected_frame is not None:
        print(f"\nSelected frame: {selected_frame}")
        return selected_frame
    else:
        return current_frame

def main():
    # Let user pick frame interactively or use predefined
    if USE_INTERACTIVE_PICKER:
        selected_frame = pick_frame_interactive(VIDEO_PATH)
        frame_index = selected_frame
    else:
        frame_index = FRAME_INDEX
        print(f"Using predefined frame: {frame_index}")
    
    frame = read_frame(VIDEO_PATH, frame_index)
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
        result = pose.process(image_rgb)

    if not result.pose_landmarks:
        print("No athlete detected.")
        return

    annotated = frame.copy()
    h, w, _ = frame.shape
    
    # Draw only the simplified connections
    for connection in SIMPLE_CONNECTIONS:
        start_idx = connection[0].value
        end_idx = connection[1].value
        start_point = result.pose_landmarks.landmark[start_idx]
        end_point = result.pose_landmarks.landmark[end_idx]
        
        # Only draw if both landmarks are visible
        if start_point.visibility > 0.5 and end_point.visibility > 0.5:
            start = (int(start_point.x * w), int(start_point.y * h))
            end = (int(end_point.x * w), int(end_point.y * h))
            cv2.line(annotated, start, end, (0, 0, 255), 2)
    
    # Draw only key landmarks
    for landmark_idx in KEY_LANDMARKS:
        lm = result.pose_landmarks.landmark[landmark_idx.value]
        if lm.visibility > 0.5:
            x = int(lm.x * w)
            y = int(lm.y * h)
            cv2.circle(annotated, (x, y), 3, (0, 255, 0), -1)

    keypoints = []
    for lm in result.pose_landmarks.landmark:
        keypoints.append((lm.x * w, lm.y * h, lm.visibility))
    keypoints = np.array(keypoints)

    print(keypoints)

    cv2.imshow("MediaPipe Pose", annotated)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # keypoints array now available for angle calculations
    # print(keypoints[:5])  # example

if __name__ == "__main__":
    main()