import asyncio
from PyPDF2 import PdfReader
import docx
import requests
from bs4 import BeautifulSoup
import speech_recognition as sr
from pydub import AudioSegment
from io import BytesIO
from utils import extract_text_from_image, summarize_text, generate_embedding, store_in_vector_db, search_vector_db

async def process_document(doc):
    file = await doc.get_file()
    file_content = await file.download_as_bytearray()
    
    if doc.file_name.endswith('.pdf'):
        return await process_pdf(BytesIO(file_content))
    elif doc.file_name.endswith('.docx'):
        return await process_docx(BytesIO(file_content))
    else:
        return "Unsupported document type"

async def process_pdf(file_obj):
    reader = PdfReader(file_obj)
    if len(reader.pages) > 30:
        return "PDF is too long (over 30 pages)"
    
    text = ""
    for page in reader.pages:
        text += page.extract_text()
    
    if not text:
        # If no text extracted, it might be a scanned PDF
        return await process_scanned_pdf(file_obj)
    
    summary = await summarize_text(text)
    embedding = await generate_embedding(summary)
    await store_in_vector_db(embedding, summary)
    return "PDF processed and stored"

async def process_scanned_pdf(file_obj):
    # Use OCR or GPT-4 Vision here
    text = await extract_text_from_image(file_obj)
    summary = await summarize_text(text)
    embedding = await generate_embedding(summary)
    await store_in_vector_db(embedding, summary)
    return "Scanned PDF processed and stored"

async def process_docx(file_obj):
    doc = docx.Document(file_obj)
    text = "\n".join([para.text for para in doc.paragraphs])
    summary = await summarize_text(text)
    embedding = await generate_embedding(summary)
    await store_in_vector_db(embedding, summary)
    return "DOCX processed and stored"

async def process_photo(photo):
    file = await photo.get_file()
    summary = await extract_text_from_image(file.file_path)
    embedding = await generate_embedding(summary)
    await store_in_vector_db(embedding, summary)
    return f"Photo analyzed and stored: {summary}"

async def process_audio(audio):
    file = await audio.get_file()
    file_content = await file.download_as_bytearray()
    audio_segment = AudioSegment.from_file(BytesIO(file_content))
    audio_segment.export("temp.wav", format="wav")
    
    recognizer = sr.Recognizer()
    with sr.AudioFile("temp.wav") as source:
        audio_data = recognizer.record(source)
        text = recognizer.recognize_google(audio_data)
    
    summary = await summarize_text(text)
    embedding = await generate_embedding(summary)
    await store_in_vector_db(embedding, summary)
    return "Audio transcribed and stored"

async def process_text(text):
    if text.lower().startswith(("what", "how", "why", "when", "where", "who")):
        return f"Query: {text}"
    embedding = await generate_embedding(text)
    await store_in_vector_db(embedding, text)
    return text

async def process_url(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    text = soup.get_text()
    print(text)
    summary = await summarize_text(text)
    embedding = await generate_embedding(f"A link was provided ({url}) and here's the summary of what's in that link:\n{summary}")
    await store_in_vector_db(embedding, summary)
    return "URL content extracted and stored"

async def query_knowledge_base(query):
    embedding = await generate_embedding(query)
    results = await search_vector_db(embedding)
    return f"Here's what I found: {results}"