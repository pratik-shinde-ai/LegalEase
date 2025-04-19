import streamlit as st
import os
from dotenv import load_dotenv
from document_processor import process_document
from llm_integration import LLMIntegration
import tiktoken

def num_tokens_from_string(string: str, encoding_name: str = "cl100k_base") -> int:
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens

def main():
    load_dotenv()
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        st.error("Please check your .env file.")
        return

    st.title("Multilingual Document Summary")

    llm = LLMIntegration()

    input_language = st.selectbox("Select input document language", ["English", "Hindi Devanagari", "Marathi"])
    output_language = st.selectbox("Select output summary language", ["English", "Hindi Devanagari", "Marathi"])

    uploaded_files = st.file_uploader("Choose PDF, DOCX, or image files", type=["pdf", "docx", "png", "jpg", "jpeg", "tiff", "bmp"], accept_multiple_files=True)

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            file_extension = os.path.splitext(file_name)[1].lower()
            temp_file_path = f"temp_document{file_extension}"
            with open(temp_file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())

            try:
                document_text = process_document(temp_file_path)
                
                token_count = num_tokens_from_string(document_text)
                if token_count > 8000:
                    st.warning(f"Document text exceeds API limit (8000 tokens). Current token count: {token_count}. The text will be truncated.")
                    document_text = document_text[:int(len(document_text) * (8000 / token_count))]
                    st.info(f"Truncated token count: {num_tokens_from_string(document_text)}")
                else:
                    st.info(f"Document token count: {token_count}")

                st.subheader(f"Summary for {file_name}")
                
                with st.spinner("Analyzing the document..."):
                    analysis = llm.analyze_document(document_text, input_language, output_language)

                if analysis:
                    st.write("**Summary:**")
                    st.write(analysis.get("summary", "No summary available"))
                    st.write("**Key Points:**")
                    for point in analysis.get("key_points", []):
                        st.write(f"• {point}")
                    st.write("**Legal Implications:**")
                    for implication in analysis.get("legal_implications", []):
                        st.write(f"• {implication}")
                    st.write("**Recommended Actions:**")
                    for action in analysis.get("recommended_actions", []):
                        st.write(f"• {action}")
                else:
                    st.error("Failed to analyze the document. Please try again.")
                    st.write("Error details:")
                    st.write(f"Document text (first 500 characters): {document_text[:500]}...")
                    st.write(f"Token count: {num_tokens_from_string(document_text)}")
            except ValueError as e:
                st.error(f"Error processing document: {e}")
            finally:
                if os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

if __name__ == "__main__":
    main()
