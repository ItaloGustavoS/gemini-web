import streamlit as st
import pdfplumber
import os
import pandas as pd
import numpy as np
import google.generativeai as genai
from langdetect import detect

# Configuração da API do Google
GOOGLE_API_KEY = "AIzaSyCeenyy-kc_VW9ljErzH2OecYx9NtKt-2U"
genai.configure(api_key=GOOGLE_API_KEY)

# Configuração para geração de texto
generation_config = {
    "temperature": 0,
    "top_p": 0.95,
    "top_k": 64,
    "max_output_tokens": 8192,
}

safety_settings = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_LOW_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_LOW_AND_ABOVE"},
]

system_instruction = "Quando o usuário fizer a pergunta, leia o arquivo pdf fornecido e exiba as informações dele na resposta"

# Gera o texto formatado
model1 = genai.GenerativeModel(
    model_name="gemini-1.5-flash-latest",
    generation_config=generation_config,
    system_instruction=system_instruction,
    safety_settings=safety_settings,
)

# Configuração do Streamlit
st.title("FAM Help - Document Processor and Query Bot")

# Função para calcular embeddings
model = "models/text-embedding-004"

# Inicializando o chat na sessão
if "chat" not in st.session_state:
    st.session_state.chat = model1.start_chat(history=[])


# Função para mapear o papel do chat para o Streamlit
def role_to_streamlit(role):
    return "assistant" if role == "model" else role


# Função para detectar o idioma do texto
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"  # Retorna inglês como padrão se a detecção falhar


# Função para extrair e salvar o conteúdo de um PDF
@st.cache_data
def extrair_e_salvar_conteudo(pdf_path, output_dir, max_size=9999):
    documents = []
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        current_text = []
        current_size = 0
        part_num = 1
        for page_number, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            text_size = len(text.encode("utf-8"))
            if current_size + text_size > max_size:
                # Salvando o texto atual em um arquivo antes de exceder o limite
                part_file_path = os.path.join(
                    output_dir,
                    f"{os.path.splitext(os.path.basename(pdf_path))[0]}_part{part_num}.txt",
                )
                with open(part_file_path, "w", encoding="utf-8") as f:
                    f.write("\n".join(current_text))
                documents.append(
                    {
                        "Titulo": f"{os.path.splitext(os.path.basename(pdf_path))[0]} Parte {part_num}",
                        "Conteudo": "\n".join(current_text),
                        "Parte": part_num,
                    }
                )
                current_text = [text]  # Iniciar novo texto
                current_size = text_size
                part_num += 1
            else:
                current_text.append(text)
                current_size += text_size
        # Salvando qualquer texto restante após a última página
        if current_text:
            part_file_path = os.path.join(
                output_dir,
                f"{os.path.splitext(os.path.basename(pdf_path))[0]}_part{part_num}.txt",
            )
            with open(part_file_path, "w", encoding="utf-8") as f:
                f.write("\n".join(current_text))
            documents.append(
                {
                    "Titulo": f"{os.path.splitext(os.path.basename(pdf_path))[0]} Parte {part_num}",
                    "Conteudo": "\n".join(current_text),
                    "Parte": part_num,
                }
            )
    return documents


# Lógica para lidar com múltiplos arquivos
@st.cache_data
def process_multiple_files(uploaded_files, base_dir):
    all_documents = []
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)

    for uploaded_file in uploaded_files:
        file_path = os.path.join(base_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        documents = extrair_e_salvar_conteudo(file_path, base_dir)
        all_documents.extend(documents)

    return all_documents


# Função para calcular embeddings de um documento
@st.cache_data
def embed_fn(title, text):
    # Limitar o tamanho do texto para 9500 bytes para evitar exceder o limite de 10000 bytes quando incluídos metadados
    byte_limit = 9500
    encoded_text = text.encode("utf-8")
    if len(encoded_text) > byte_limit:
        text = encoded_text[:byte_limit].decode("utf-8", errors="ignore")
        st.write(
            f"Alerta: O conteúdo do documento '{title}' foi truncado para se ajustar ao limite de tamanho da API."
        )

    if text.strip():  # Verifica se o texto não está vazio
        try:
            return genai.embed_content(
                model=model, content=text, title=title, task_type="RETRIEVAL_DOCUMENT"
            )["embedding"]
        except Exception as e:
            st.error(f"Erro ao gerar embedding para o documento '{title}': {e}")
            return np.zeros(1)  # Retorna um vetor de zeros como placeholder
    else:
        st.write(f"Erro: O conteúdo do documento '{title}' está vazio.")
        return np.zeros(1)


# Função para gerar e buscar consulta
@st.cache_data
def gerar_e_buscar_consulta(consulta, base, model):
    embedding_da_consulta = genai.embed_content(
        model=model, content=consulta, title="Consulta", task_type="RETRIEVAL_DOCUMENT"
    )["embedding"]
    produtos_escalares = np.dot(np.stack(base["Embeddings"]), embedding_da_consulta)
    indice = np.argmax(produtos_escalares)
    return base.iloc[indice]["Conteudo"]


# Interface do Streamlit para carregar arquivos PDF
uploaded_files = st.file_uploader(
    "Carregue seus arquivos PDF aqui:", type="pdf", accept_multiple_files=True
)
base_dir = "tempDir"

# Verifica se foram carregados arquivos PDF
if uploaded_files:
    if not os.path.exists(base_dir):
        os.makedirs(base_dir)
    all_documents = []

    # Processa cada arquivo PDF carregado
    for uploaded_file in uploaded_files:
        file_path = os.path.join(base_dir, uploaded_file.name)
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        # Extrai e salva o conteúdo do PDF
        documents = extrair_e_salvar_conteudo(file_path, base_dir)
        all_documents.extend(documents)

    # Se houver documentos, cria um DataFrame e calcula os embeddings
    if all_documents:
        df = pd.DataFrame(all_documents)
        df["Embeddings"] = df.apply(
            lambda row: embed_fn(row["Titulo"], row["Conteudo"]), axis=1
        )
        st.write(df)

        for message in st.session_state.chat.history:
            with st.chat_message(role_to_streamlit(message.role)):
                st.markdown(message.parts[0].text)

# Interface para a consulta do usuário
if prompt := st.chat_input("Digite sua consulta aqui:"):
    st.chat_message("user").markdown(prompt)
    # Enviando a mensagem do usuário e recebendo a resposta
    with st.spinner("Processando Resposta..."):
        response = st.session_state.chat.send_message(prompt)
        # Detecta o idioma da consulta
        language_code = detect_language(prompt)
        # Realiza a busca
        resultado = gerar_e_buscar_consulta(prompt, df, model)
        # Gera a resposta com o modelo Gemini 1.5 Pro
        response_obj = model1.generate_content(prompt)

    # Exibindo a resposta do assistente
    with st.chat_message("assistant"):
        st.markdown(response.text)
