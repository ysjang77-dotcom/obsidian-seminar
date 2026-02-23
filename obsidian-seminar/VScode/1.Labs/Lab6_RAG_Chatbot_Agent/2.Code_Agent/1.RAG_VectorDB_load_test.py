import os
import shutil
from dotenv import load_dotenv

# LangChain 관련 라이브러리 임포트
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain.text_splitter import MarkdownHeaderTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser

# --- 0. 환경 설정 및 테스트 데이터 준비 ---

def setup_environment():
    """
    스크립트 실행에 필요한 환경을 설정합니다. 
    .env 파일 로드, 'docs' 폴더 및 샘플 마크다운 파일을 생성합니다.
    """
    # .env 파일에서 환경 변수(예: GOOGLE_API_KEY)를 로드합니다.
    load_dotenv()
    
    # Google API 키 존재 여부를 확인합니다.
    if not os.getenv("GOOGLE_API_KEY"):
        raise ValueError("GOOGLE_API_KEY가 .env 파일에 설정되지 않았습니다.")

    # 데이터 소스가 될 'docs' 폴더를 생성합니다.
    docs_path = "docs"
    if not os.path.exists(docs_path):
        os.makedirs(docs_path)

# --- RAG 파이프라인 함수 ---

def initialize_vectorstore(docs_path="docs", vectorstore_path="faiss_index"):
    """
    VectorDB를 초기화합니다.
    - 지정된 경로에 VectorDB 파일이 있으면 로드합니다.
    - 없으면 문서를 로드, 분할, 임베딩하여 새로 생성하고 저장합니다.
    """
    # Step 3: Embedding 모델 초기화
    # Google의 Gemini 임베딩 모델을 사용합니다.
    embeddings = GoogleGenerativeAIEmbeddings(model="models/gemini-embedding-001")

    # 핵심 요구사항: VectorDB 파일이 존재하면 재사용
    if os.path.exists(vectorstore_path):
        print(f"'{vectorstore_path}'에서 기존 VectorDB를 로드합니다.")
        try:
            # allow_dangerous_deserialization=True는 로컬 환경 신뢰를 전제로 합니다.
            return FAISS.load_local(vectorstore_path, embeddings, allow_dangerous_deserialization=True)
        except Exception as e:
            print(f"VectorDB 로드 실패: {e}. 새로 생성합니다.")
            # 손상된 인덱스 파일일 수 있으므로 삭제 후 새로 생성 진행
            shutil.rmtree(vectorstore_path)

    print("기존 VectorDB가 없습니다. 새로 생성합니다.")
    
    # Step 1: Document Load
    # 'docs' 폴더 내의 모든 .md 파일을 로드합니다.
    print(f"'{docs_path}' 폴더에서 Markdown 문서를 로드합니다.")
    loader = DirectoryLoader(docs_path, glob="**/*.md", loader_cls=UnstructuredMarkdownLoader)
    documents = loader.load()

    # Step 2: Text Split
    # Markdown 헤더를 기준으로 텍스트를 의미 단위로 분할합니다.
    print("헤더 기준으로 문서를 분할합니다.")
    headers_to_split_on = [("#", "Header 1"), ("##", "Header 2"), ("###", "Header 3"), ("####", "Header 4")]
    markdown_splitter = MarkdownHeaderTextSplitter(headers_to_split_on=headers_to_split_on, strip_headers=False)
    
    all_splits = []
    for doc in documents:
        # 파일별로 텍스트 분할 실행
        splits = markdown_splitter.split_text(doc.page_content)
        # 분할된 청크(chunk)에 원본 파일 경로(source) 메타데이터를 추가합니다.
        for split in splits:
            split.metadata['source'] = doc.metadata.get('source', 'N/A')
        all_splits.extend(splits)
        
    if not all_splits:
        raise ValueError("문서 분할에 실패했거나 분할할 콘텐츠가 없습니다. 'docs' 폴더에 .md 파일이 있는지 확인하세요.")

    # Step 4: VectorDB Store
    # 분할된 텍스트를 임베딩하여 FAISS VectorDB에 저장합니다.
    print("분할된 문서를 임베딩하고 VectorDB에 저장합니다.")
    vectorstore = FAISS.from_documents(documents=all_splits, embedding=embeddings)
    
    # 생성된 VectorDB를 파일로 저장하여 재사용할 수 있도록 합니다.
    print(f"생성된 VectorDB를 '{vectorstore_path}'에 저장합니다.")
    vectorstore.save_local(vectorstore_path)
    
    return vectorstore

def create_rag_chain(vectorstore):
    """
    주어진 VectorDB를 기반으로 RAG 체인을 생성합니다.
    """
    # Step 5: Retrieval
    # VectorDB를 사용하여 질문과 관련된 문서를 검색하는 Retriever를 생성합니다.
    retriever = vectorstore.as_retriever(search_kwargs={"k": 10})
    
    # Step 6: Prompt & LLM
    # LLM으로 Gemini Pro 모델을 사용합니다.
    llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0, convert_system_message_to_human=True)

    # LLM에게 전달할 프롬프트 템플릿을 정의합니다.
    prompt_template = """
당신은 주어진 문서를 바탕으로 질문에 답변하는 신뢰성공학 전문 AI 어시스턴트입니다. 매우 논리적이며 구체적이고 상세한 답변을 제공해주세요. 컨텍스트를 벗어난 내용은 답변하지 마세요. 답변을 할 때는 어떤 문서를 참고했는지 출처를 반드시 명시해주세요.

[Context]
{context}

[Question]
{question}

[Answer]
"""
    prompt = ChatPromptTemplate.from_template(prompt_template)
    
    # 검색된 문서(docs) 객체를 프롬프트에 맞게 문자열로 포맷팅하는 함수입니다.
    def format_docs(docs):
        # 각 문서의 내용과 출처(메타데이터)를 조합하여 하나의 문자열로 만듭니다.
        return "\n\n".join(f"출처: {doc.metadata.get('source', 'N/A')}\n내용: {doc.page_content}" for doc in docs)

    # Step 7: Output (LCEL을 사용한 체인 구성)
    # LangChain Expression Language (LCEL)를 사용하여 RAG 파이프라인을 구성합니다.
    rag_chain = (
        {"context": retriever | format_docs, "question": RunnablePassthrough()}
        | prompt
        | llm
        | StrOutputParser()
    )
    
    return rag_chain

# --- 메인 실행 블록 ---

def main():
    """
    전체 RAG 프로세스를 실행하고 사용자 질문에 답변합니다.
    """
    try:
        # 0. 환경 설정 및 샘플 데이터 생성
        setup_environment()
        
        # 1. VectorDB 초기화 (파일이 있으면 로드, 없으면 생성)
        vectorstore = initialize_vectorstore()
        
        # 2. RAG 체인 생성
        rag_chain = create_rag_chain(vectorstore)
        
        # 3. RAG 체인을 사용하여 질문하고 답변받기
        print("\n--- 첫 번째 질문 ---")
        question_1 = "파노라마 썬루프의 누수관련 고장현상을 모두 조사해줘."
        print(f"[질문]: {question_1}")
        
        answer_1 = rag_chain.invoke(question_1)
        
        print("\n[답변]:")
        print(answer_1)
        
        print("\n--- 두 번째 질문 ---")
        question_2 = "파워윈도우 스위치의 대표적인 고장현상을 조사해줘."
        print(f"[질문]: {question_2}")

        answer_2 = rag_chain.invoke(question_2)
        
        print("\n[답변]:")
        print(answer_2)
        
    except Exception as e:
        print(f"스크립트 실행 중 오류가 발생했습니다: {e}")

if __name__ == "__main__":
    main()