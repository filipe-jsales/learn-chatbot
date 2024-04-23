
from langchain import hub
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import chainlit as cl
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader
from webscrapper import TxtCreator


txt_creator = TxtCreator("https://www.webera.com/")
txt_creator.run()

llm = Ollama(
        base_url="http://10.50.0.11:11434",
        model="mistral",
        verbose=True,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    )

rag_prompt_mistral = hub.pull("rlm/rag-prompt-mistral")

# print(rag_prompt_mistral)
DATA_PATH = "data/data.txt"
DB_PATH = "vectorstores/db/"
template = "[INST]You are an assistant for question-answering tasks and guide costumers of the website. Act like you're an Employee of the organization of the content provided. Use the following pieces of retrieved context to answer the question. If you don't know the answer, just say that you don't know. Keep the answer concise. Answer the questions with few phrases as possible.[/INST] </s> \n[INST] Question: {question} \nContext: {context} \nAnswer: [/INST]"
prompt = PromptTemplate.from_template(template)
prompt.input_variables = ['context', 'question']
# print(prompt)

def create_vector_db():
    loader = TextLoader(DATA_PATH)
    documents = loader.load()
    # print(f"Processed {len(documents)} pdf files")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500,
    chunk_overlap=0)
    texts = text_splitter.split_documents(documents)
    vectorstore = Chroma.from_documents(
        documents=texts, embedding=OllamaEmbeddings(base_url="http://10.50.0.11:11434", model="mistral"), persist_directory=DB_PATH
    )
    vectorstore.persist()
 

create_vector_db()


def load_model():
    llm = Ollama(
        base_url="http://10.50.0.11:11434",
        model="mistral",
        verbose=True,
        callback_manager=CallbackManager([StreamingStdOutCallbackHandler()]),
    )
    return llm


def retrieval_qa_chain(llm, vectorstore):

    qa_chain = RetrievalQA.from_chain_type(
        llm,
        retriever=vectorstore.as_retriever(),
        chain_type_kwargs={"prompt": prompt},
        return_source_documents=True,
    )
    return qa_chain


def qa_bot():
   DB_PATH = "vectorstores/db/"
   llm = load_model()
   vectorstore = Chroma(
        persist_directory=DB_PATH, embedding_function=OllamaEmbeddings(base_url="http://10.50.0.11:11434", model="mistral")
    )
  
   vectorstore.persist()

   qa = retrieval_qa_chain(llm, vectorstore)
   return qa


@cl.on_chat_start
async def start():
    
    chain = qa_bot()
    welcome_message = cl.Message(content="Starting the bot...")
    await welcome_message.send()
    welcome_message.content = (
        "Hi, Welcome to Chat With Documents using Ollama (mistral model) and LangChain."
    )
    await welcome_message.update()
    cl.user_session.set("chain", chain)


@cl.on_message
async def main(message):
   
    chain = cl.user_session.get("chain")
    cb = cl.AsyncLangchainCallbackHandler()
    cb.answer_reached = True
    res = await chain.acall(message.content, callbacks=[cb])
    answer = res["result"]
    source_documents = res["source_documents"]

    text_elements = []  

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        


    await cl.Message(content=answer, elements=text_elements).send()