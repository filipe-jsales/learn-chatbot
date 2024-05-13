import TxtCreator
import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from metadataExtractor import EntityExtractor
from pathlib import Path
extractor = EntityExtractor()

def create_vector_db():
    try:


        data_path = os.environ.get('DATA_PATH', 'data/data.txt')
        db_path = os.environ.get('DB_PATH', 'vectorstores/db/')
        chunk_size = int(os.environ.get('CHUNK_SIZE', '1000'))
        chunk_overlap = int(os.environ.get('CHUNK_OVERLAP', '100'))
        model_name = os.environ.get('MODEL_NAME_DB', 'nomic-embed-text')
        ollama_server = os.environ.get('OLLAMA_SERVER', 'http://10.50.0.11:11434')
        model_temperature = float(os.environ.get('MODEL_TEMPERATURE', '0'))
        collection_name = os.environ.get('COLLECTION_NAME', 'vector_db')


        loader = TextLoader(data_path)
        documents = loader.load()
        text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        texts = text_splitter.split_documents(documents) 
        all_metadata = {}

        for idx, doc in enumerate(texts):
            if hasattr(doc, 'page_content') and hasattr(doc, 'metadata'):
                page_content = doc.page_content
                metadata = extractor.get_inverted_dict(page_content)
                link = extractor.extract_source_link(page_content)
                
                
                if 'metadata' in doc and isinstance(doc.metadata, dict):
                    doc.metadata.update({'source': link})
                elif 'metadata' not in doc:
                    doc.metadata = {'source': link}
                         
        for text in texts:
            print(text)
        vectorstore = Chroma.from_documents(
            documents=texts,
            embedding=OllamaEmbeddings(base_url=ollama_server, model=model_name, temperature=model_temperature),
            persist_directory=db_path, collection_name=collection_name
        )
        vectorstore.persist()
        print(f"Vector database created with {len(texts)} entries.")
    except Exception as e:
        print(f"Error creating vector database: {e}")
        
def is_folder_empty(path):
    return not any(Path(path).iterdir())

def main():
    db_path = os.environ.get('DB_PATH')
    if not is_folder_empty(db_path):
        print("Database already exists. Skipping creation.")
        return
    url = os.environ.get('WEBSITE_URL', 'https://webera.com/')
    TxtCreator.TxtCreator(url).run()
    create_vector_db()

if __name__ == "__main__":
    main()
