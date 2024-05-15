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

# Definindo o modelo
model = "models/text-embedding-004"

# Configuração da página do Streamlit
st.set_page_config(page_title="FAM Help")

# Título da aplicação
st.title("FAM Help - Document Processor and Query Bot")


# Função para detectar o idioma do texto
def detect_language(text):
    try:
        return detect(text)
    except:
        return "en"  # Retorna inglês como padrão se a detecção falhar


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
def gerar_e_buscar_consulta(consulta, base, model):
    embedding_da_consulta = genai.embed_content(
        model=model, content=consulta, title="Consulta", task_type="RETRIEVAL_DOCUMENT"
    )["embedding"]
    produtos_escalares = np.dot(np.stack(base["Embeddings"]), embedding_da_consulta)
    indice = np.argmax(produtos_escalares)
    return base.iloc[indice]["Conteudo"]


# Interface do Streamlit para carregar arquivos
uploaded_files = st.file_uploader(
    "Carregue seus arquivos PDF aqui:", type="pdf", accept_multiple_files=True
)
base_dir = "tempDir"
