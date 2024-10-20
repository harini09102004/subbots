import streamlit as st
import os
from PIL import Image
import google.generativeai as genai
import pyttsx3
import schedule
import time
import threading
import re  # Import regex here
from engine.command import allCommands
import speech_recognition as sr
import MyAlarm  # Import MyAlarm before usage

# Configure API key for Google Generative AI
genai.configure(api_key="AIzaSyBjARp9j3dMyRlsfOFoC59kI9UJX15dZ_M")
model = genai.GenerativeModel('gemini-1.5-flash')

# Initialize pyttsx3 engine
engine = pyttsx3.init()

# Global variable to control speaking
is_speaking = False

# Function to convert text to speech
def speak(response):
    global is_speaking
    if is_speaking:  # Stop ongoing speech if already speaking
        engine.stop()  # Stop any ongoing speech
    is_speaking = True  # Set speaking state to True
    response = str(response)  # Ensure the response is a string
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)  # Adjust voice if needed
    engine.setProperty('rate', 174)  # Speed of speech

    # Function to handle speaking in a thread
    def speak_thread():
        engine.say(response)
        engine.runAndWait()
        global is_speaking
        is_speaking = False  # Set speaking state to False after speaking

    # Start speaking in a new thread
    threading.Thread(target=speak_thread).start()

# Function to stop speaking
def stop_speaking():
    global is_speaking
    is_speaking = False
    engine.stop()  # Stop the speech engine

# Function to take voice command using speech recognition
def takecommand():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        print('Listening....')
        r.pause_threshold = 1
        r.adjust_for_ambient_noise(source)
        audio = r.listen(source, 10, 6)  # Listening with a timeout

    try:
        print('Recognizing...')
        query = r.recognize_google(audio, language='en-in')  # Language set for India
        print(f"User said: {query}")
        time.sleep(2)
        return query
    except Exception as e:
        print("Error recognizing: ", e)
        return ""  # If no valid command is detected, return empty string

# Function to interact with Gemini API
def get_gemini_response(input_text, image_data, prompt):
    response = model.generate_content([input_text, image_data[0], prompt])
    return response.text

# Function to process uploaded image
def input_image_details(uploaded_file):
    if uploaded_file is not None:
        bytes_data = uploaded_file.getvalue()
        image_parts = [
            {
                "mime_type": uploaded_file.type,
                "data": bytes_data
            }
        ]
        return image_parts
    else:
        raise FileNotFoundError("No file was uploaded")

# Streamlit UI
st.set_page_config(page_title="DiagnoBot")
st.sidebar.header("DiagnoBot")
st.sidebar.write("Prescription Analysis Assistant")
st.sidebar.write("""Disclaimer: I am an AI-powered prescription reader. While I can provide information on medications and possible conditions, my advice is not a substitute for professional medical guidance. 
Always consult a licensed healthcare provider for accurate diagnosis and treatment.""")
st.sidebar.write("Powered by Mithra")
st.header("Diagnobot")
st.subheader("""Hello! I'm DiagnoBot, A good friend of Mithra!""")
st.subheader("I will provide you with insights based on the prescription from your doctor!")

input_text = st.text_input("How can I help you?", key="input")
uploaded_file = st.file_uploader("Please upload your prescription given by your doctor", type=["jpg", "jpeg", "png"])

# Display uploaded image
if uploaded_file is not None:
    image = Image.open(uploaded_file)
    st.image(image, caption="Uploaded image", use_column_width=True)

# Create columns for buttons
col1, col2, col3, col4, col5, col6, col7 = st.columns([1, 1, 1, 1, 1, 1, 1])  # Adjust column sizes as needed

# Place buttons in columns
with col1:
    submit = st.button("Start Analysis")  # Button to submit input

with col7:
    stop_button = st.button("Stop Analysis")  # Button to stop speaking

input_prompt = """You are an expert in reading handwritten and digital prescriptions.
I am developing a healthcare AI system that can diagnose diseases and provide insights into prescribed medications.
Using the details from the uploaded prescription, perform the following tasks:
Disease Detection: Based on the prescription, identify the likely disease or condition the patient has. Analyze the medications listed, their dosages, and any other information provided to make a diagnosis.
Medication Uses: For each medication listed in the prescription, provide a detailed description of its uses. Explain what conditions or symptoms it treats, and provide any relevant information about how it works.
How many times the doctor has told to take medicine in the prescription?
What disease the patient might have? Also, study the prescription given and understand all the given data. When asked for what medicine should be taken and how many times a day, give the result in this format: "Take X mg of Y, 3 times a day."
"""

# Handle AI response when the user submits the input
if submit:
    image_data = input_image_details(uploaded_file)
    response = get_gemini_response(input_prompt, image_data, input_text)
    
    # Modify response to avoid specific output
    filtered_response = re.sub(r'\*\*[\w\s]+\*\*: Take [\d.]+ml of [\w\s]+', 'The prescribed medication information is available.', response)
    
    st.write(filtered_response)
    print(f"AI Response: {filtered_response}")
    speak(filtered_response)

# Stop speaking if the stop button is pressed
if stop_button:
    stop_speaking()
