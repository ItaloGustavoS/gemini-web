import os
import streamlit as st
import google.generativeai as genai

genai.configure(api_key="AIzaSyCEk7rv5K2DnnfLwOoQx0uDgU2LTpmycBQ")
model = genai.GenerativeModel("models/gemini-1.5-pro-latest")

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
