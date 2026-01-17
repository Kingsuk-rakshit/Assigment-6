import os
import tempfile
from pypdf import PdfReader
from docx import Document
import assemblyai as aai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# PDF Loader

def load_pdf(file) -> str:
    """
    Extract text from a PDF file uploaded via Streamlit.
    """
    reader = PdfReader(file)
    text = []
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text.append(page_text)
    return "\n".join(text)



# DOCX Loader

def load_docx(file) -> str:
    """
    Extract text from a DOCX file uploaded via Streamlit.
    """
    doc = Document(file)
    paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)



# TXT / Transcript Loader

def load_text(file) -> str:
    """
    Load plain text or transcript files.
    """
    return file.read().decode("utf-8", errors="ignore")



# MP4 Video → Transcript (AssemblyAI)

def load_video(file) -> str:
    """
    Transcribe an uploaded MP4 video using AssemblyAI.
    Returns transcript text.
    """
    api_key = os.getenv("ASSEMBLYAI_API_KEY")
    if not api_key:
        raise ValueError("ASSEMBLYAI_API_KEY not found in environment variables")

    aai.settings.api_key = api_key

    # Save uploaded video temporarily
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp:
        tmp.write(file.read())
        video_path = tmp.name

    try:
        transcriber = aai.Transcriber()
        transcript = transcriber.transcribe(video_path)

        if transcript.status == aai.TranscriptStatus.error:
            raise RuntimeError(f"Transcription failed: {transcript.error}")

        return transcript.text

    finally:
        # Clean up temp file
        if os.path.exists(video_path):
            os.remove(video_path)
