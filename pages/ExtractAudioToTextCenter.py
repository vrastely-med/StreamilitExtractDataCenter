import streamlit as st
import whisper
import os
import datetime

st.title("Audio Transcription with Whisper")

st.write("""
This app transcribes audio files using OpenAI's Whisper model.

**Note:** Ensure that 'openai-whisper' and 'ffmpeg' are installed in your system.

- Install Whisper with: `pip install openai-whisper`
- Install FFmpeg from [ffmpeg.org](https://ffmpeg.org/download.html)
""")

# Select the Whisper model size
model_size = st.selectbox("Select Whisper model size:", ["tiny", "base", "small", "medium", "large"])

# Load the Whisper model
st.write(f"Loading Whisper model '{model_size}'...")
model = whisper.load_model(model_size)
st.success(f"Model '{model_size}' loaded.")

# Upload audio files
uploaded_files = st.file_uploader(
    "Upload audio files (mp3, mp4, wmv, wma, wav, m4a):",
    type=["mp3", "mp4", "wmv", "wma", "wav", "m4a"],
    accept_multiple_files=True
)

if uploaded_files:
    total_files = len(uploaded_files)
    progress_bar = st.progress(0)
    for idx, uploaded_file in enumerate(uploaded_files):
        st.write(f"Processing file: {uploaded_file.name}")
        # Save the uploaded file temporarily
        with open(uploaded_file.name, "wb") as f:
            f.write(uploaded_file.getbuffer())
        
        try:
            # Transcribe the audio file
            result = model.transcribe(uploaded_file.name)
            
            # Display the transcription
            st.write(f"**Transcription of {uploaded_file.name}:**")
            st.write(result["text"])
            
            # Save the transcription to a text file
            today_date = datetime.date.today()
            filename_nofiletype = os.path.splitext(uploaded_file.name)[0]
            txt_file_name = f"{today_date}_{filename_nofiletype}.txt"
            
            with open(txt_file_name, "w", encoding="utf-8") as txt_file:
                txt_file.write(result["text"])
            
            st.success(f"Transcription saved as {txt_file_name}")
            
            # Offer the text file for download
            with open(txt_file_name, "rb") as txt_file:
                st.download_button(
                    label=f"Download transcription of {uploaded_file.name}",
                    data=txt_file,
                    file_name=txt_file_name,
                    mime="text/plain"
                )
            
            # Clean up the transcription file
            os.remove(txt_file_name)
            
        except Exception as e:
            st.error(f"An error occurred while processing {uploaded_file.name}: {e}")
        
        finally:
            # Remove the temporary audio file
            os.remove(uploaded_file.name)
        
        # Update the progress bar
        progress = (idx + 1) / total_files
        progress_bar.progress(progress)
else:
    st.info("Please upload audio files to transcribe.")
