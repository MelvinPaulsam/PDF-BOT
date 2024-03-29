import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from langchain.text_splitter import CharacterTextSplitter
from langchain.vectorstores import FAISS
from langchain.embeddings import HuggingFaceInstructEmbeddings
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.chat_models import ChatOpenAI
from langchain.llms import huggingface_hub
from htmlTemplates import css, bot_template, user_template
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
def handle_userinput(user_question):
    response = st.session_state.conversation({'question': user_question})
    st.session_state.chat_history = response['chat_history']

    for i, message in enumerate(st.session_state.chat_history):
        if i % 2 == 0:
            st.write(user_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
        else:
            st.write(bot_template.replace(
                "{{MSG}}", message.content), unsafe_allow_html=True)
def get_conversation_store(vectorstore):
    llm=huggingface_hub(repo_id="google/flan-t5-xxl",model_kwargs={"temperature":0.5,"max_length":512})
    memory=ConversationBufferMemory(memory_key="chat history",return_messages=True)
    conversation_chain=ConversationalRetrievalChain.from_llm(
        llm=llm,retriever=vectorstore.as_retriever(),memory=memory
    )
    return conversation_chain


def main():
    load_dotenv()
    st.set_page_config(page_title="Chat with pdfs",page_icon=":books:")
    if "conversation" not in st.session_state:
        st.session_state.conversation=None
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = None
    st.header("Chat with pdfs")
    user_question=st.text_input("Ask qs to your docs:")
    if user_question:
        handle_userinput(user_question)
    with st.sidebar:
        st.subheader("Your documents")
        pdf_docs=st.file_uploader("Uplod pdfs here and click on 'Process'",accept_multiple_files=True)
        if st.button("Process"):
            with st.spinner("Processing"):
                raw_text=get_pdf_text(pdf_docs)

                text_chunks=get_text_chunks(raw_text)

                vectorstore=get_vectorstore(text_chunks)
                st.session_state.conversation=get_conversation_store(vectorstore)
if __name__=='__main__' :
    main()