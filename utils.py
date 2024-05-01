from dotenv import load_dotenv
from langchain_community.llms.huggingface_endpoint import HuggingFaceEndpoint
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain.chains.llm import LLMChain
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores.docarray import DocArrayInMemorySearch
from langchain_community.embeddings.huggingface import HuggingFaceEmbeddings
from prompts import QuestionAnswerTemplate
from operator import itemgetter

# from langchain_community

load_dotenv()
repo_id = "mistralai/Mistral-7B-Instruct-v0.2"

def load_llm(repo_id):
    #load the LLM
    llm = HuggingFaceEndpoint(
        repo_id=repo_id, temperature=0.5
    )
    return llm


def create_vector_store_from_pdf(data_path):
    #load the pdf
    loader = PyPDFLoader(data_path)
    pages = loader.load_and_split()


    #create the vector emmbeddings
    vectorstore = DocArrayInMemorySearch.from_documents(
        pages,
        embedding=HuggingFaceEmbeddings()
    )

    #build a retriever
    retriever = vectorstore.as_retriever()

    return retriever


def retrieve(input, data_path):
   llm = load_llm(repo_id=repo_id)
   prompt = PromptTemplate.from_template(template=QuestionAnswerTemplate)
   retriever = create_vector_store_from_pdf(data_path)
   chain = (
                {
                    "context" : itemgetter("question") | retriever,
                    "question" : itemgetter("question")
                }
                | prompt
                | llm
            )
   result =  chain.invoke({"question" : input})
   return result
