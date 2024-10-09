from langchain_community.document_loaders import UnstructuredPDFLoader

def load_document(file_path):
    loader = UnstructuredPDFLoader(file_path)
    documents = loader.load()
    return documents
