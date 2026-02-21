from langchain_community.document_loaders import PyPDFLoader, TextLoader

def load_document(file_path: str) -> str:

    if file_path.endswith('.pdf'):
        loader = PyPDFLoader(file_path)
    elif file_path.endswith('.txt'):
        loader = TextLoader(file_path)
    else:
        raise ValueError("Only PDF/TXT supported")
    
    docs = loader.load()
    return "\n".join([doc.page_content for doc in docs])

def load_pasted_text(text: str) -> str:
    
    #Return pasted text as is
    
    return text.strip()