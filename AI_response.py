import os
import sys
import google.generativeai as genai
from langchain_community.vectorstores import FAISS
from langchain.chains.question_answering import load_qa_chain
from langchain_core.prompts import PromptTemplate
from langchain_google_genai import GoogleGenerativeAIEmbeddings, GoogleGenerativeAI

os.environ["GOOGLE_API_KEY"] = 'GOOGLE_API_KEY'
genai.configure(api_key="GOOGLE_API_KEY")
gemini_model = genai.GenerativeModel(model_name = "gemini-pro")

llm = GoogleGenerativeAI(model="gemini-pro", temperature=0.7, max_length = 10000)
embeddings = GoogleGenerativeAIEmbeddings(model = "models/embedding-001")


def format_splits(outer_splits):
    formatted_chunks = []
    for split in outer_splits:
        formatted_chunks.append(split.page_content)
    return formatted_chunks


if not os.path.exists(sys.path[0] + '\\faiss_context'):
    from Parser import splits
    chunks = format_splits(splits)
    vector_search = FAISS.from_texts(chunks, embedding=embeddings)
    vector_search.save_local("faiss_context")
    print("Файл faiss_context создан")
else:
    vector_search = FAISS.load_local("faiss_context", embeddings, allow_dangerous_deserialization=True)


#information extractor
template = """ You are extracting information from a japanese language textbook. Answer the question using provided context, 
trying to make your answer understandable for a russian speaker. 
Give detailed answers, try to extract maximum amount of relevant information from the provided context. 
Answer the questions in russian, but provide grammatical examples in japanese with added translation into russian. 
Provide transliteration for examples both in russian letters and hiragana.
Context: {context}
Question: {question}
Answer:"""
prompt = PromptTemplate(template = template, input_variables = ["context"])


chain = load_qa_chain(llm, chain_type="stuff", prompt=prompt)

questionnaire = ["Who is the author of the provided texts ?", "What are the first 10 vocabulary examples ?",
                 "How to better learn kanji ?", "How to count in japanese ?","Как вежливо пожелать доброго утра ?",
                 "How is Inclusive Topic Particle used ?", "How does 眠い reads and what does it mean ?",
                 "What's special about kanji 的 ?", "Types of verbs.", "Какие личные местоимения есть в японском ?",
                 "Katakana with cyrilic transliteration"]

def gemini_answer(user_input):
    docs = vector_search.similarity_search(user_input)
    return chain.invoke({'input_documents': docs, "question": user_input})['output_text']


