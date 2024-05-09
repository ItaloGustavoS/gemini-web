from pathlib import Path
import hashlib
import os
import streamlit as st
import google.generativeai as genai

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
]

genai.configure(api_key="AIzaSyCEk7rv5K2DnnfLwOoQx0uDgU2LTpmycBQ")
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

st.set_page_config(page_title="Gemini AI", page_icon=":computer:")

st.title("Gemini AI :computer:")

if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])


def role_to_streamlit(role):
    if role == "model":
        return "assistant"
    else:
        return role


for message in st.session_state.chat.history:
    with st.chat_message(role_to_streamlit(message.role)):
        st.markdown(message.parts[0].text)

if prompt := st.chat_input("O que você gostaria de saber ?"):
    st.chat_message("user").markdown(prompt)
    response = st.session_state.chat.send_message(prompt)
    with st.chat_message("assistant"):
        st.markdown(response.text)
