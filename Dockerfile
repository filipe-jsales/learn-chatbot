FROM ubuntu:latest
RUN apt-get update && apt-get upgrade -y
RUN apt-get install python3 python3-pip git -y
RUN pip install \
    langchain \
    chainlit \
    langchainhub \
    gpt4all \
    chromadb \
    unstructured \
    markdown 

WORKDIR /app


ENTRYPOINT [ "chainlit", "run", "-w", "rag.py"  ]