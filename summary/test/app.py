import streamlit as st
import fitz  # PyMuPDF
import docx
from sumy.parsers.plaintext import PlaintextParser
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.tokenizers import Tokenizer
import nltk
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM

nltk.download('punkt', quiet=True)

@st.cache_resource
def load_t5_model():
    tokenizer = AutoTokenizer.from_pretrained('t5-base')
    model = AutoModelForSeq2SeqLM.from_pretrained('t5-base')
    return tokenizer, model

t5_tokenizer, t5_model = load_t5_model()

def process_document(file):
    if file.name.endswith(".pdf"):
        doc = fitz.open(stream=file.read(), filetype="pdf")
        return "".join(page.get_text() for page in doc)
    elif file.name.endswith(".docx"):
        doc = docx.Document(file)
        return "\n".join(para.text for para in doc.paragraphs)
    else:
        raise ValueError("Unsupported file type")

def extractive_summarize(text, sentences_count=5):
    parser = PlaintextParser.from_string(text, Tokenizer("english"))
    summarizer = LsaSummarizer()
    summary = summarizer(parser.document, sentences_count)
    return [str(sentence) for sentence in summary]

def abstractive_summarize(text, max_length=200):
    chunks = [text[i:i+1000] for i in range(0, len(text), 1000)]
    summaries = []
    for chunk in chunks:
        inputs = t5_tokenizer.encode("summarize: " + chunk, return_tensors="pt", max_length=512, truncation=True)
        summary_ids = t5_model.generate(inputs, max_length=max_length, min_length=50, length_penalty=2.0, num_beams=4, early_stopping=True)
        summary = t5_tokenizer.decode(summary_ids[0], skip_special_tokens=True)
        summaries.append(summary)
    return '. '.join(summaries).split('. ')

def main():
    st.title("Enhanced Legal Document Summarizer")
    uploaded_file = st.file_uploader("Upload a PDF or DOCX file", type=["pdf", "docx"])

    if uploaded_file:
        try:
            text = process_document(uploaded_file)
            
            st.subheader("Key Points (Extractive Summary)")
            for point in extractive_summarize(text):
                st.markdown(f"• {point}")

            st.subheader("Simplified Overview (Abstractive Summary)")
            for point in abstractive_summarize(text):
                st.markdown(f"• {point}")
        except ValueError as e:
            st.error(str(e))

if __name__ == "__main__":
    main()