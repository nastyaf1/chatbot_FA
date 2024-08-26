import requests
from bs4 import BeautifulSoup as bs
from urllib.parse import urlparse
from langchain_community.document_loaders import WebBaseLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter


'''
собираем docs
domain guidetojapanese.org
63 ссылки указывающих на домен
'''

def site_parcer(url):
    url_p = urlparse(url)
    domain = '{uri.scheme}://{uri.netloc}/'.format(uri=url_p)
    resp = requests.get(url)
    soup = bs(resp.text, 'html.parser')
    for link in soup.find_all('a'):
        temp = link.get('href')
        if temp is not None and domain in temp:
            j_links.append(temp)


def more_urls():
    for i in range(1,8):
        page_number=i
        link = fr"https://guidetojapanese.org/learn/category/grammar-guide/page/{page_number}/"
        link2 = fr"https://guidetojapanese.org/learn/category/complete-guide/page/{page_number}/"
        if requests.get(link).status_code == 200:
            j_links.append(link)
        if requests.get(link2).status_code == 200:
            j_links.append(link2)


j_links = []

url = r"https://guidetojapanese.org/learn/category/complete-guide/"
url2 = r"https://guidetojapanese.org/learn/category/grammar-guide/"

# добавляем url  j_links
site_parcer(url)
site_parcer(url2)
more_urls()

j_links = list(set(j_links))
print(len(j_links), j_links)
# loader for j_links
loader = WebBaseLoader(j_links) # max 63
loader.requests_per_second = 1
docs_from_urls = loader.aload()

print("j_links - загружены через j_parcer\n")

docs = docs_from_urls

text_splitter = RecursiveCharacterTextSplitter(chunk_size=400, chunk_overlap=50)
splits = text_splitter.split_documents(docs)

