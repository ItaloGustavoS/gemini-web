import streamlit as st
import google.generativeai as genai

# Configurações de geração de texto
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 0,
    "max_output_tokens": 8192,
}

# Configurações de segurança
safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
]

# Configurando a API Key
genai.configure(api_key="AIzaSyCEk7rv5K2DnnfLwOoQx0uDgU2LTpmycBQ")

# Inicializando o modelo de geração de texto
model = genai.GenerativeModel(
    model_name="gemini-1.5-pro-latest",
    generation_config=generation_config,
    safety_settings=safety_settings,
)

# Configuração da página do Streamlit
st.set_page_config(page_title="Gemini AI", page_icon=":computer:")

# Título da aplicação
st.title("Gemini AI :computer:")

# Inicializando o chat na sessão
if "chat" not in st.session_state:
    st.session_state.chat = model.start_chat(history=[])


# Função para mapear o papel do chat para o Streamlit
def role_to_streamlit(role):
    return "assistant" if role == "model" else role


# Exibindo o histórico de mensagens
for message in st.session_state.chat.history:
    with st.chat_message(role_to_streamlit(message.role)):
        st.markdown(message.parts[0].text)

# Entrada do usuário
if prompt := st.chat_input("O que você gostaria de saber ?"):
    st.chat_message("user").markdown(prompt)
    # Enviando a mensagem do usuário e recebendo a resposta
    with st.spinner("Processando Resposta..."):
        response = st.session_state.chat.send_message(prompt)
    # Exibindo a resposta do assistente
    with st.chat_message("assistant"):
        st.markdown(response.text)
