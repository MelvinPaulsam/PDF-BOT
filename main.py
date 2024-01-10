import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceInstructEmbeddings
def get_pdf_text(pdf_docs):
    text=""
    for pdf in pdf_docs:
        p=PdfReader(pdf)
        for i in p.pages:
            text+=i.extract_text()
    return text
def get_text_chunks(text):
    text_spitter=CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len
    )
    chunks=text_spitter.split_text(text)
    return chunks
def get_vectorstore(text_chunks):
    embeddings=HuggingFaceInstructEmbeddings(model_name="hkunlp/instructor-xl")
    vectorstore=FAISS.from_texts(text=text_chunks,embedding=embeddings)
    return vectorstore
    
def main():
    st.set_page_config(page_title="Chat with pdfs",page_icon=":books:")
    st.header("Chat with pdfs")
    st.text_input("Ask qs to your docs:")
    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs=st.file_uploader("Uplod pdfs here and click on 'Process'",accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                raw_text=get_pdf_text(pdf_docs)

                text_chunks=get_text_chunks(raw_text)

                vectorstore=get_vectorstore(text_chunks)
if __name__=='__main__' :
    main()