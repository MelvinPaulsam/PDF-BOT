import streamlit as st

def main():
    st.set_page_config(page_title="Chat with pdfs",page_icon=":books:")
    st.header("Chat with pdfs")
    st.text_input("Ask qs to your docs:")
    with st.sidebar:
        st.subheader("Your documents")
        st.file_uploader("Uplod pdfs here and click on 'Process'")
        st.button("Process")

   

if __name__=='__main__' :
    main()