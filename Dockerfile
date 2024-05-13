FROM webera/python

WORKDIR /app

COPY ./src/ .

RUN pip install langchain \
                chainlit \
                langchainhub \
                chromadb \
                pypdf \
                bs4 \
                tldextract \
                PyPDF2 \
                spacy \
                transformers

RUN python -m spacy download en_core_web_sm
