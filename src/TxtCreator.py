import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os
import tldextract
from PyPDF2 import PdfReader  # Import PdfReader from PyPDF2
from langchain_text_splitters import CharacterTextSplitter
from langchain_community.llms import Ollama
from langchain.chains.summarize import load_summarize_chain
from langchain_community.document_loaders import TextLoader
from langchain_core.documents import Document
from langchain.prompts import PromptTemplate
import os

class TxtCreator:
    def __init__(self, base_url):
        self.base_url = base_url
        self.urls = set()
        self.pdf_urls = set()
        self.visited = set()
        self.session = requests.Session()
        self.domain = self.extract_domain(base_url)
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'
        })
        self.pdf_reader = os.environ.get('PDF_READER', "false")

    def extract_domain(self, url):
        extracted = tldextract.extract(url)
        return "{}.{}".format(extracted.domain, extracted.suffix)

    def get_urls(self):
        queue = [self.base_url]
        ignore_keywords = ['login', 'signin', 'sign-up', 'register', 'auth']
        while queue:
            current_url = queue.pop(0)
            if current_url in self.visited:
                continue
            self.visited.add(current_url)
            try:
                response = self.session.get(current_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                links = soup.find_all("a")
                for link in links:
                    href = link.get('href')
                    if href:
                        full_url = urljoin(current_url, href)
                        # Ensure the URL is well-formed
                        parts = full_url.split("/")
                        if len(parts) > 2 and ":" in parts[2]:  # Check if the host part includes a port
                            continue
                        if any(keyword in full_url.lower() for keyword in ignore_keywords):
                            continue
                        if full_url not in self.visited and not any(href.startswith(x) for x in ['#', 'javascript:', 'mailto:', 'tel:']):
                            if href.lower().endswith(".pdf") and self.pdf_reader != "false":
                                self.pdf_urls.add(full_url)
                            else:
                                if self.extract_domain(full_url) == self.domain:
                                    print(f"Found URL: {full_url}")
                                    queue.append(full_url)
                                    self.urls.add(full_url)
            except Exception as e:
                print(f"Failed to process {current_url}: {str(e)}")


    def download_pdf(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            os.makedirs("data/pdf", exist_ok=True)
            file_name = os.path.basename(url)
            file_path = os.path.join("data/pdf", file_name)
            with open(file_path, "wb") as f:
                f.write(response.content)
            print(f"Downloaded {file_name}")
            return file_path  # Return the file path for further processing
        except requests.RequestException as e:
            print(f"Error downloading PDF from {url}: {e}")
            return None
    def summarizer(self, text, type):
        document = text
        def get_text_chunks_langchain(text):
            text_splitter = CharacterTextSplitter(chunk_size=500, chunk_overlap=100)
            docs = [Document(page_content=x) for x in text_splitter.split_text(text)]
            return docs


        llm = Ollama(
                    base_url=os.environ.get('OLLAMA_SERVER', 'http://10.50.0.11:11434'),
                    model=os.environ.get('MODEL_NAME_SUMMARIZE', 'mistral'),
                    temperature = float(os.environ.get('MODEL_TEMPERATURE', '0'))
                )
        prompt_template = """Write a concise summary in first-person plural of the following:
        {text}
        CONCISE SUMMARY:"""
        prompt = PromptTemplate.from_template(prompt_template)
        refine_template ="""
         "Your job is to produce a final summary in first-person plural\n"
    "We have provided an existing summary up to a certain point: {existing_answer}\n"
    "We have the opportunity to refine the existing summary"
    "(only if needed) with some more context below.\n"
    "------------\n"
    "{text}\n"
    "------------\n"
    "Given the new context, refine the original summary"
    "If the context isn't useful, return the original summary.
    REFINED SUMMARY:"
        """
        refine_prompt = PromptTemplate(template=refine_template, input_variables=["text", "existing_answer"])
        if type == "refine":
            chain = load_summarize_chain(llm, chain_type=type, refine_prompt=refine_prompt, question_prompt=prompt )
        else:
            chain = load_summarize_chain(llm, chain_type=type, verbose=True)
        return chain.run(get_text_chunks_langchain(document))
    def create_txt(self):
        content = ""
        for url in self.urls:
            try:
                response = self.session.get(url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
                main_content = soup.find("body")
                if main_content:
                    text = main_content.getText("\n")
                    if(len(text) < 10000):
                        text_summarized = self.summarizer(text, "refine")
                    else:
                        text_summarized = self.summarizer(text, "map_reduce")
                    content += text_summarized.strip() +"\n"+"Source: "+ url + "\n\n"
            except requests.RequestException as e:
                print(f"Error processing URL {url}: {e}")

        for pdf_url in self.pdf_urls:
            pdf_path = self.download_pdf(pdf_url)
            if pdf_path:
                try:
                    reader = PdfReader(pdf_path)
                    for page in reader.pages:
                        
                        content += self.summarizer(page.extract_text(), "map_reduce") + "\n\n"
                except Exception as e:
                    print(f"Error reading PDF {pdf_path}: {e}")

        os.makedirs("data", exist_ok=True)
        file_path = os.path.join("data", "data.txt")
        try:
            with open(file_path, "w") as f:
                content = content.replace("..", "")
                f.write(content)
        except IOError as e:
            print(f"Error writing content to file: {e}")

    def run(self):
        self.get_urls()
        self.create_txt()
        print("Data collection complete.")
