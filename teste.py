import base64
import streamlit as st
from vertexai.generative_models import GenerativeModel, Part
import vertexai.preview.generative_models as generative_models


def generate_content(
    image_data, document_data, question, generation_config, safety_settings
):
    with st.spinner("Gerando conteúdo..."):
        model = GenerativeModel("gemini-1.5-pro-preview-0409")
        responses = model.generate_content(
            [
                Part.from_data(mime_type="image/jpeg", data=image_data),
                Part.from_data(mime_type="application/pdf", data=document_data),
                question,
            ],
            generation_config=generation_config,
            safety_settings=safety_settings,
            stream=True,
        )

        for response in responses:
            st.write(response.text, unsafe_allow_html=True)


def main():
    st.title("Gerador de Conteúdo")

    image_file = st.file_uploader("Carregar imagem (JPEG)", type=["jpg", "jpeg"])
    document_file = st.file_uploader("Carregar documento (PDF)", type="pdf")
    question = st.text_input("Digite sua pergunta sobre a imagem e o documento")

    if st.button("Gerar Conteúdo"):
        if image_file is not None and document_file is not None and question != "":
            image_data = base64.b64encode(image_file.read()).decode("utf-8")
            document_data = base64.b64encode(document_file.read()).decode("utf-8")

            generation_config = {
                "max_output_tokens": 8192,
                "temperature": 1,
                "top_p": 0.95,
            }

            safety_settings = {
                generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
                generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_LOW_AND_ABOVE,
            }

            generate_content(
                image_data, document_data, question, generation_config, safety_settings
            )
        else:
            st.warning(
                "Por favor, carregue uma imagem, um documento e faça uma pergunta."
            )


if __name__ == "__main__":
    main()
