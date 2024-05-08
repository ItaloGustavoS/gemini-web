import streamlit as st
from pathlib import Path
import hashlib
import google.generativeai as genai
import json


def upload_if_needed(pathname: str) -> list[str]:
    path = Path(pathname)
    hash_id = hashlib.sha256(path.read_bytes()).hexdigest()
    try:
        existing_file = genai.get_file(name=hash_id)
        return [existing_file.uri]
    except:
        pass
    uploaded_files.append(genai.upload_file(path=path, display_name=hash_id))
    return [uploaded_files[-1].uri]


def extract_pdf_pages(pdf_content: bytes) -> list[str]:
    parts = [f"--- INÍCIO DO PDF ---"]
    # Adicione a lógica para ler o conteúdo do PDF e retornar uma lista de páginas aqui.
    # Exemplo simples apenas para demonstração
    pages = pdf_content.split(
        b"\n\n"
    )  # Dividindo o conteúdo do PDF por quebras de linha
    for index, page in enumerate(pages):
        try:
            decoded_page = page.decode("utf-8")  # Tentar decodificar usando utf-8
        except UnicodeDecodeError:
            decoded_page = page.decode(
                "latin-1"
            )  # Se falhar, tentar decodificar usando latin-1
        parts.append(f"--- PÁGINA {index + 1} ---")
        parts.append(decoded_page)
    return parts


def clean_and_format_user_input(user_input: str) -> str:
    # Limpar e formatar a entrada do usuário (remover caracteres especiais, etc.)
    formatted_input = user_input.lower().strip()
    # Implementar lógica de limpeza e formatação específica, se necessário
    return formatted_input


def parse_response_data(response_data: dict) -> str:
    # Processar a resposta do modelo conversacional (extrair o texto da resposta)
    response_text = response_data["predictions"][0]["text"]
    # Implementar lógica de processamento da resposta específica, se necessário
    return response_text


def generate_response(user_input: str, uploaded_files: list[bytes]) -> str:
    # Convertendo cada arquivo carregado para uma string antes de concatená-los
    input_texts = []
    for file in uploaded_files:
        try:
            input_texts.append(file.decode("utf-8"))
        except UnicodeDecodeError:
            try:
                input_texts.append(file.decode("latin-1"))
            except UnicodeDecodeError:
                # Se nenhuma codificação funcionar, adicione um texto vazio
                input_texts.append("")

    input_text = "\n".join(input_texts)
    formatted_input = clean_and_format_user_input(input_text)
    response_data = model.predict_text(formatted_input)
    response_text = parse_response_data(response_data)
    return response_text


# Configuração inicial do Google Generative AI
genai.configure(
    api_key="AIzaSyCEk7rv5K2DnnfLwOoQx0uDgU2LTpmycBQ"
)  # Substitua por sua chave API

# Inicialização das variáveis
uploaded_files = []
model = genai.GenerativeModel(model_name="gemini-1.5-pro-latest")

# Título do aplicativo Streamlit
st.title("Chatbot com Google Generative AI")

# Opção para fazer upload do PDF
uploaded_file = st.file_uploader("Faça upload do PDF", type=["pdf"])

# Lógica para lidar com o upload do PDF
if uploaded_file is not None:
    pdf_content = uploaded_file.read()  # Lendo o conteúdo do arquivo PDF
    pdf_parts = extract_pdf_pages(pdf_content)
    st.write(pdf_parts)

    # Salvar o arquivo carregado
    uploaded_files.append(pdf_content)

# Input do usuário
user_input = st.text_input("Digite sua pergunta aqui:")

# Botão para enviar a pergunta
if st.button("Enviar"):
    response = generate_response(user_input, uploaded_files)
    st.text_area("Resposta do modelo:", value=response, height=200)
