import streamlit as st
import speech_recognition as sr
import google.generativeai as genai
from google.generativeai import GenerativeModel
import time
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
import io
import pandas as pd

# Configure Google Gemini API
GENAI_API_KEY = "AIzaSyCdPyNKD65zpfamZoPclmUKiFpGqh1THF8"
genai.configure(api_key=GENAI_API_KEY)
model = GenerativeModel(model_name="gemini-1.5-pro-latest")

# Function to get audio input from the user (still present but optional now)
def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.write("🎙 Listening...")
        audio = r.listen(source)
        said = ""
        try:
            said = r.recognize_google(audio)
            st.write("You said:", said)
        except sr.UnknownValueError:
            st.write("Sorry, I did not understand that.")
        except sr.RequestError:
            st.write("Speech recognition service is unavailable.")
    return said

# Function to interact with Gemini
def chat_with_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.write("Error communicating with Gemini API:", e)
        return ""

# Function to extract text from PDF using PyMuPDF
def extract_text_from_pdf(uploaded_pdf):
    text = ""
    try:
        with fitz.open(stream=uploaded_pdf.read(), filetype="pdf") as doc:
            for page in doc:
                text += page.get_text()
    except Exception as e:
        st.error(f"Failed to extract text: {e}")
    return text

# Function to create chatbot personalities
def create_personality_bot(bot_type, user_input):
    if bot_type == "Friendly Bot":
        prompt = f"Act like a friendly assistant and respond warmly to: {user_input}"
    elif bot_type == "Professional Bot":
        prompt = f"Act like a professional business assistant and answer formally: {user_input}"
    elif bot_type == "Funny Bot":
        prompt = f"Add a touch of humor and act like a fun chatbot. User asked: {user_input}"
    else:
        prompt = user_input
    return chat_with_gemini(prompt)

# UI Function for BizBrain AI Chatbot
def bizbrain_ai_chatbot():
    chatbot_type = st.selectbox("Choose your chatbot personality:", ["Friendly Bot", "Professional Bot", "Funny Bot"])
    option = st.radio("Choose your input method:", ("Text", "Voice"))

    if option == "Text":
        user_input = st.text_input("You:", key="text_input")
        if st.button("Send"):
            if user_input:
                st.write("You:", user_input)
                response = create_personality_bot(chatbot_type, user_input)
                st.write("BizBrain AI:", response)
    else:
        if st.button("🎤 Speak"):
            user_input = get_audio()
            if user_input:
                response = create_personality_bot(chatbot_type, user_input)
                st.write("BizBrain AI:", response)

# UI Function for AI Content Generator
def ai_content_generator():
    st.subheader("✍️ AI Content Generator")

    content_type = st.radio("Select content type:", 
                            ["Formal Letter", "Formal Email", "Story Creation", "Blog Writing", "Social Media Post"])

    content_input = st.text_area("Enter the topic / purpose / keywords:")

    if st.button("Generate"):
        if content_type == "Formal Letter":
            prompt = f"Write a formal letter regarding: {content_input}"
        elif content_type == "Formal Email":
            prompt = f"Compose a professional email about: {content_input}"
        elif content_type == "Story Creation":
            prompt = f"Create a short and engaging story based on: {content_input}"
        elif content_type == "Blog Writing":
            prompt = f"Write an informative and well-structured blog post on: {content_input}"
        elif content_type == "Social Media Post":
            prompt = f"Generate a catchy and engaging social media post about: {content_input}"
        else:
            prompt = content_input

        response = chat_with_gemini(prompt)
        st.subheader("📝 Generated Output")
        st.write(response)

# UI Function for Student Productivity Toolkit
def student_productivity_toolkit():
    st.subheader("📚 Student Productivity Toolkit")

    tool = st.radio("Choose a feature:", ["Image Analysis", "PDF Analysis", "CSV Data Analysis"])

    if tool == "Image Analysis":
        uploaded_images = st.file_uploader("Upload image(s) to analyze text", type=["png", "jpg", "jpeg"], accept_multiple_files=True)

        if uploaded_images:
            for uploaded_file in uploaded_images:
                image = Image.open(uploaded_file)
                st.image(image, caption=f"Uploaded: {uploaded_file.name}", use_column_width=True)

                with st.spinner("Analyzing Image..."):
                    extracted_text = pytesseract.image_to_string(image)
                st.success("Text Extracted:")
                st.text_area(f"Text from {uploaded_file.name}", extracted_text, height=200)

    elif tool == "PDF Analysis":
        uploaded_pdfs = st.file_uploader("Upload PDF(s) to analyze text", type=["pdf"], accept_multiple_files=True)

        if uploaded_pdfs:
            for pdf_file in uploaded_pdfs:
                with st.spinner(f"Extracting text from {pdf_file.name}..."):
                    pdf_text = extract_text_from_pdf(pdf_file)
                st.success(f"Text extracted from {pdf_file.name}:")
                st.text_area(f"Text from {pdf_file.name}", pdf_text, height=300)

    elif tool == "CSV Data Analysis":
        uploaded_csv = st.file_uploader("Upload CSV file to analyze data", type=["csv"])

        if uploaded_csv:
            try:
                df = pd.read_csv(uploaded_csv, encoding_errors='ignore')
                st.write("📋 Uploaded CSV Data:")
                st.dataframe(df)

                query = st.text_input("Ask a question about the CSV data:", key="csv_query")
                if st.button("Analyze CSV") and query:
                    csv_prompt = f"Analyze the following data and answer the question: {query}\n\n{df.head(10).to_string()}"
                    csv_response = chat_with_gemini(csv_prompt)
                    st.write("BizBrain AI:", csv_response)

            except Exception as e:
                st.error(f"Error reading CSV file: {e}")

# Main function
def main():
    st.set_page_config(page_title="BizBrain AI", page_icon="🧠")
    st.title("🧠 BizBrain AI")

    user_name = st.text_input("Enter your name:", key="name")
    if user_name:
        st.subheader(f"Hi {user_name}! 👋")

    selected_tool = st.radio("Choose a Tool:", ["Student Productivity Toolkit", "AI Content Generator", "BizBrain AI Chatbot"], horizontal=True)

    if selected_tool == "Student Productivity Toolkit":
        student_productivity_toolkit()
    elif selected_tool == "AI Content Generator":
        ai_content_generator()
    elif selected_tool == "BizBrain AI Chatbot":
        bizbrain_ai_chatbot()

if __name__ == "__main__":
    main()
