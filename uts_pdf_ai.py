from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.chains.question_answering import load_qa_chain
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI
import google.generativeai as genai
import sys
import os

os.environ['USER_AGENT'] = 'myagent'
os.environ["GOOGLE_API_KEY"] = 'GOOGLE_API_KEY'
genai.configure(api_key="GOOGLE_API_KEY")

# read in your pdf file
file_path = sys.path[0] + '\\uts.pdf'
pdf_reader = PyPDFLoader(file_path).load_and_split()

text = ''
for page in pdf_reader:
    i = str(page)
    text += i

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1000,
    chunk_overlap=200,
    length_function=len
)
texts = text_splitter.split_text(text)
embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

if not os.path.exists(sys.path[0] + '\\pdf_context'):
    vector_pdf_search = FAISS.from_texts(texts, embedding=embeddings)
    vector_pdf_search.save_local("pdf_context")
    print("Файл faiss_context создан")
else:
    vector_pdf_search = FAISS.load_local("pdf_context", embeddings, allow_dangerous_deserialization=True)

llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.7, max_length=10000)

template = """ You need to extract and summarize information in the context. You can expand the topic if asked about one of the subjects in a curriculum.
Base your answer on the provided information about the curriculum. Answer in russian language.
Context: {context}
Question: {question}
Answer:"""
prompt = PromptTemplate(template=template, input_variables=["context"])

chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)


def pdf_smart_search(user_message):
    docs_pdf = vector_pdf_search.similarity_search(user_message, k=7, fetch_k=40)
    return chain.invoke({'input_documents': docs_pdf, "question": user_message})['output_text']
