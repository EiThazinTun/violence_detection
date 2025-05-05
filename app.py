import os
import streamlit as st
import cv2
import yt_dlp as ydl
from utils.detect import detect_violence_in_frame, analyze_with_ollama

# Ensure videos folder exists
os.makedirs("videos", exist_ok=True)

st.title('Violence Detection in Videos')
st.markdown('Upload a video or paste a URL to detect violence.')

uploaded_file = st.file_uploader("Choose a video file", type=["mp4", "mov", "avi"])
video_url = st.text_input("Or paste a video URL from YouTube, Facebook, TikTok")

video_path = None

# Handle file upload
if uploaded_file:
    video_path = os.path.join("videos", uploaded_file.name)
    with open(video_path, "wb") as f:
        f.write(uploaded_file.read())
    st.success("✅ Video uploaded successfully!")

# Handle video URL
elif video_url:
    try:
        if "youtube.com/shorts/" in video_url:
            video_url = video_url.replace("youtube.com/shorts/", "youtube.com/watch?v=")

        ydl_opts = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': os.path.join('videos', '%(id)s.%(ext)s'),
        }

        with ydl.YoutubeDL(ydl_opts) as downloader:
            info_dict = downloader.extract_info(video_url, download=True)
            video_id = info_dict.get("id", "temp")
            video_ext = info_dict.get("ext", "mp4")
            video_path = os.path.join("videos", f"{video_id}.{video_ext}")
        st.success("✅ Video downloaded successfully!")

    except Exception as e:
        st.error(f"Error downloading video: {e}")

# Start detection
if video_path and os.path.exists(video_path):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        st.error("Error: Could not open video.")
    else:
        frame_count = 0
        detected_violence = False

        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
            frame, detected_objects, found_violence = detect_violence_in_frame(frame)
            if found_violence:
                detected_violence = True
                break
            frame_count += 1
        cap.release()

        # Show video
        st.markdown("### 🎬 Video Preview")
        st.video(video_path)

        if detected_violence:
            st.success("✅ Violence detected in the video!")

            # 🔥 Call LLaMA3 with fixed prompt
            prompt = "Violent activity detected: Person seen with knife or gun in the video. Please summarize this."
            llama_response = analyze_with_ollama(prompt)

            st.markdown("### 🧠 LLaMA3 Analysis")
            st.write(llama_response)
        else:
            st.info("No violence detected.")
