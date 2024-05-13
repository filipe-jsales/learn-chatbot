from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_community.llms import Ollama
from langchain.callbacks.manager import CallbackManager
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
import chainlit as cl
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
import os
import json
import uuid

chat_history = ""
i = 1

def store_conversation(history, question, answer, session_id):
    global i
    global chat_history
    chat_history += f"Session ID: {session_id}\n"
    chat_history += f"Previous question {i}: {question}\n Previous answer {i}: {answer}\n"
    i += 1
    chat_data = {
        "session_id": session_id,
        "history": chat_history.split("\n"),
        "question": question,
        "answer": answer,
    }
    file_path = "chat_history.json"
    with open(file_path, "w") as json_file:
        json.dump(chat_data, json_file)

    print("Chat history saved to:", file_path)

session_id = str(uuid.uuid4())
print("Session ID:", session_id)

def load_model():
    try:
        model_name = os.environ.get('MODEL_NAME', 'mistral')
        ollama_server = os.environ.get('OLLAMA_SERVER', 'http://10.50.0.11:11434')
        llm = Ollama(
            base_url=ollama_server,
            model=model_name,
            verbose=True,
            callback_manager=CallbackManager([StreamingStdOutCallbackHandler()])
        )
        return llm
    except Exception as e:
        print(f"Error loading the model: {e}")

def retrieval_qa_chain(llm, vectorstore):
    
    template = os.environ.get('PROMPT_TEMPLATE', "<s>[INST]You are an assistant for question-answering tasks about the organization and guide costumers of the website. Act like you're an Employee of the organization of the content provided. Use the following pieces of retrieved context to answer the question and only answer questions about the context. If you don't know the answer and the question is not related with the context or organization, just say that you don't know. Keep the answer concise and just give relevant informations about the question. It's very important to not give sensive informations[/INST]  \n[INST] Question: {question} \nContext: {context} \nAnswer: [/INST]</s>")
    
    prompt = PromptTemplate.from_template(template)
    prompt.input_variables = ['context', 'question']
    
    try:
        qa_chain = RetrievalQA.from_chain_type(
            llm,
            retriever=vectorstore.as_retriever(),
            chain_type_kwargs={"prompt": prompt},
            return_source_documents=True
        )
        return qa_chain
    except Exception as e:
        print(f"Error creating the QA chain: {e}")

def qa_bot():

    db_path = os.environ.get('DB_PATH', "vectorstores/db/")
    model_name = os.environ.get('MODEL_NAME_DB', 'nomic-embed-text')
    ollama_server = os.environ.get('OLLAMA_SERVER', 'http://10.50.0.11:11434')
    model_temperature = float(os.environ.get('MODEL_TEMPERATURE', '0'))
    collection_name = os.environ.get('COLLECTION_NAME', 'vector_db')

    llm = load_model()
    vectorstore = Chroma(
        persist_directory=db_path, embedding_function=OllamaEmbeddings(base_url=ollama_server, model=model_name, temperature=model_temperature), collection_name=collection_name
    )

    vectorstore.persist()

    qa = retrieval_qa_chain(llm, vectorstore)
  
    return qa


    
    
  
  
@cl.on_chat_start
async def start():
    try:
        chain = qa_bot()
        cl.user_session.set("chain", chain)
    except Exception as e:
        print(f"Error during chat start: {e}")
        
@cl.on_message
async def main(message):
    try:
        greeting_responses = {
            "hi": "Hello! How can I assist you today?",
            "hello": "Hi there! What can I do for you?"
        }
        
        message_content = message.content.strip().lower()
        if len(chat_history) > 0:
            message.content = f"Based on the previous message history, its feedback and on the context, give me a more precise answer, but focus on the new question.\n Previous messages: \n{chat_history}\n New question: {message_content}"
        if len(message_content) > 20000 :
            await cl.Message(content="Sorry, I can't process messages longer than 10000 characters.").send()
        print(message.content)
        if message_content in greeting_responses:
            await cl.Message(content=greeting_responses[message_content]).send()
            return
        
        chain = cl.user_session.get("chain")
        cb = cl.AsyncLangchainCallbackHandler()
        cb.answer_reached = True
        res = await chain.ainvoke(message.content, callbacks=[cb])
        answer = res["result"]
        
        source_documents = res["source_documents"]
        text_elements = []  
        if source_documents:
            for source_idx, source_doc in enumerate(source_documents):
                source_name = source_doc.metadata['source']
                
                text_elements.append(
                    cl.Text(content=source_doc.page_content, name=source_name)
                )
            source_names = [text_el.name for text_el in text_elements if len(text_el.name) > 0]

            # if source_names:

            #     answer += f"Here some links for you: {', '.join(source_names)}"

            # else:
            #     answer += ""
        conversation_history = cl.user_session.get("conversation_history", [])
        store_conversation(conversation_history, message_content, res["result"], session_id)
        cl.user_session.set("conversation_history", conversation_history)
        
        await cl.Message(content=answer, elements=text_elements).send()
    except Exception as e:
        print(f"Error during message handling: {e}")
