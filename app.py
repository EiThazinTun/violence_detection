import os
import streamlit as st
import cv2
from pytube import YouTube
import yt_dlp as ydl
from utils.detect import detect_violence_in_frame, download_video, analyze_with_ollama


# Streamlit UI setup
st.title('Violence Detection in Videos')
st.markdown('Upload a video or paste a URL to detect violence.')

# Video uploader
uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])
video_url = st.text_input("Or paste a video URL from YouTube, Facebook, TikTok")

# Handle video upload
if uploaded_file is not None:
    # Save uploaded video to the "videos" folder
    video_path = os.path.join("videos", uploaded_file.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())

    # Process the uploaded video for detection
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("Error: Could not open video.")

    frame_count = 0
    detected_violence = False
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect violence in the frame
        _, _, found_violence = detect_violence_in_frame(frame)

        if found_violence:
            detected_violence = True
            break  # Stop the video processing once violence is detected

        frame_count += 1

    cap.release()

    # Display final message
    if detected_violence:
        st.success("Violence detected in the video!")
    else:
        st.info("No violence detected.")

elif video_url:
    # Handle URL input for videos (e.g., YouTube, Facebook, TikTok)
    video_path = None

    # Handle YouTube video download with yt-dlp
if "youtube.com" in video_url or "youtu.be" in video_url or "youtube.com/shorts" in video_url:
    try:
        ydl_opts = {
            'outtmpl': os.path.join('videos', '%(title)s.%(ext)s'),  # Save with proper name
        }
        with ydl.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(video_url, download=True)
            video_path = os.path.join("videos", f"{info_dict['title']}.mp4")
    except Exception as e:
        st.error(f"Error downloading YouTube video: {e}")

elif "tiktok.com" in video_url or "facebook.com" in video_url:
        # Handle other video URLs (use yt-dlp for TikTok, Facebook, etc.)
        try:
            ydl_opts = {
                'outtmpl': os.path.join('videos', '%(title)s.%(ext)s'),  # Save with proper name
            }
            with ydl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(video_url, download=True)
                video_path = os.path.join("videos", f"{info_dict['title']}.mp4")
        except Exception as e:
            st.error(f"Error downloading video from URL: {e}")

if video_path:
        # Process the downloaded video for detection
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            st.error("Error: Could not open video.")
        
        frame_count = 0
        detected_violence = False
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            # Detect violence in the frame
            _, _, found_violence = detect_violence_in_frame(frame)

            if found_violence:
                detected_violence = True
                break  # Stop the video processing once violence is detected

            frame_count += 1

        cap.release()

        # Display final message
        if detected_violence:
            st.success("Violence detected in the video!")
        else:
            st.info("No violence detected.")
