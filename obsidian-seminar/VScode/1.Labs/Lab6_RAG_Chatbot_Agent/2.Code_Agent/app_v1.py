# ==============================================================================
# 1. 환경 설정 및 라이브러리 임포트 (Environment Setup & Import Libraries)
# ==============================================================================
import os
import streamlit as st
from dotenv import load_dotenv
import asyncio

# LangChain 관련 라이브러리
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS

# asyncio 이벤트 루프 설정 (Streamlit 비동기 문제 해결)
# 현재 스레드에 이벤트 루프가 있는지 확인하고, 없으면 새로 생성하여 설정합니다.
# 이는 langchain의 비동기 기능이 Streamlit 환경에서 정상적으로 동작하도록 보장합니다.
try:
    asyncio.get_running_loop()
except RuntimeError:  # 'RuntimeError: There is no current event loop...'
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

# .env 파일에서 환경 변수를 로드합니다.
# 이 함수는 스크립트 시작 부분에서 한 번만 호출하면 됩니다.
load_dotenv()

# FAISS 인덱스 경로와 임베딩 모델 이름을 상수로 정의합니다.
FAISS_INDEX_PATH = "faiss_index"
EMBEDDING_MODEL = "models/gemini-embedding-001"
LLM_MODEL = "gemini-2.5-flash" # Use a faster model for better interactivity

# ==============================================================================
# 2. RAG 체인 초기화 함수 (Initialize RAG Chain Function)
# ==============================================================================

@st.cache_resource(show_spinner="전문가 시스템을 준비하는 중입니다...")
def get_rag_chain():
    """
    Streamlit의 캐시 리소스를 사용하여 RAG 체인을 초기화하고 반환합니다.
    이 함수는 앱이 처음 실행될 때 한 번만 호출되어 모델과 VectorDB 로딩의
    비효율을 방지합니다.
    """
    try:
        # --- API 키 및 필수 경로 확인 ---
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("'.env' 파일에 GOOGLE_API_KEY가 설정되지 않았습니다.")
        if not os.path.exists(FAISS_INDEX_PATH):
            raise FileNotFoundError(f"FAISS 인덱스 폴더 '{FAISS_INDEX_PATH}'를 찾을 수 없습니다. 먼저 VectorDB를 생성해야 합니다.")

        # --- 1. 임베딩 모델 및 LLM 초기화 ---
        embeddings = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL)
        llm = ChatGoogleGenerativeAI(model=LLM_MODEL, temperature=0, convert_system_message_to_human=True)

        # --- 2. 로컬 FAISS VectorDB 로드 ---
        # allow_dangerous_deserialization=True는 로컬 환경의 pkl 파일을 신뢰할 때 사용합니다.
        vectorstore = FAISS.load_local(
            FAISS_INDEX_PATH, 
            embeddings, 
            allow_dangerous_deserialization=True
        )

        # --- 3. Retriever 생성 ---
        # VectorDB를 사용하여 관련 문서를 검색하는 Retriever를 생성합니다.
        retriever = vectorstore.as_retriever(search_kwargs={"k": 5})

        # --- 4. 시스템 프롬프트 정의 (페르소나 적용) ---
        # 신뢰성 공학 전문가의 페르소나를 정의하는 시스템 프롬프트입니다.
        system_prompt = """
        당신은 수십 년 경력의 신뢰성 공학(Reliability Engineering) 전문가입니다. 당신의 임무는 주어진 기술 문서(Context)를 바탕으로 사용자의 질문에 대해 매우 논리적이고, 체계적이며, 심층적인 답변을 제공하는 것입니다.

        **답변 생성 규칙:**
        1.  **전문가적 분석:** 단순히 정보를 요약하지 말고, 각 정보의 인과관계, 중요도, 잠재적 리스크 등을 분석하여 전문가적 견해를 포함하세요.
        2.  **객관적 근거 제시:** 답변의 모든 내용은 반드시 주어진 [Context]에 근거해야 하며, 어떤 문서를 참고했는지 출처(source)를 명확하게 명시해야 합니다.
        3.  **추가 추론 및 제안:** 사용자가 추가 분석을 요청하면, 과거 대화 내용을 모두 고려하여 종합적인 결론을 도출하고, 필요하다면 추가적인 분석 방법이나 대책을 제안하세요.
        4.  **모르는 정보:** [Context]에 없는 내용에 대한 질문에는 "주어진 정보만으로는 답변하기 어렵습니다."라고 명확히 밝히세요.
        """

        # --- 5. 프롬프트 템플릿 생성 (대화 기록 포함) ---
        # 대화 기록(chat_history)과 사용자 질문(human_input)을 처리하는 프롬프트 템플릿을 구성합니다.
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "질문: {human_input}\n\n참고할 문서:\n{context}"),
        ])

        # --- 6. 검색된 문서 포맷팅 함수 ---
        def format_docs(docs):
            # 검색된 문서 객체를 프롬프트에 맞게 하나의 문자열로 포맷팅합니다.
            return "\n\n".join(f"출처: {doc.metadata.get('source', 'N/A')}\n---\n{doc.page_content}" for doc in docs)

        # --- 7. RAG 체인 구성 (LCEL) ---
        # LangChain Expression Language (LCEL)를 사용하여 RAG 파이프라인을 구성합니다.
        rag_chain = (
            RunnablePassthrough.assign(
                context=lambda x: format_docs(retriever.invoke(x["human_input"])),
            )
            | prompt
            | llm
            | StrOutputParser()
        )
        
        return rag_chain

    except (ValueError, FileNotFoundError) as e:
        # 설정 오류 발생 시 사용자에게 안내 메시지를 표시하고 앱 실행을 중단합니다.
        st.error(f"초기화 중 오류가 발생했습니다: {e}")
        return None
    except Exception as e:
        # 기타 예외 처리
        st.error(f"알 수 없는 오류가 발생했습니다: {e}")
        return None

# ==============================================================================
# 3. Streamlit UI 기본 구조 설정 (Streamlit UI Base Setup)
# ==============================================================================

# --- 페이지 설정 ---
st.set_page_config(page_title="신뢰성 분석 전문가 챗봇", page_icon="🤖")
st.title("🤖 신뢰성 분석 전문가 챗봇")
st.markdown("""
안녕하세요! 저는 신뢰성 기술자료 DB를 기반으로 심층 분석을 제공하는 AI 챗봇입니다.
파노라마 선루프, 볼펜 등 다양한 제품의 고장 분석 보고서에 대해 질문해보세요.
""")

# --- 대화 기록(Session State) 초기화 ---
if "messages" not in st.session_state:
    st.session_state.messages = [
        AIMessage(content="안녕하세요! 저는 신뢰성 분석 전문가입니다. 무엇을 도와드릴까요?")
    ]

# --- RAG 체인 가져오기 ---
# 캐싱된 RAG 체인을 로드합니다. 오류 발생 시 rag_chain은 None이 됩니다.
rag_chain = get_rag_chain()

# ==============================================================================
# 4. 대화 내용 표시 및 사용자 입력 처리 (Display & Process Conversation)
# ==============================================================================

# --- 이전 대화 내용 표시 ---
for message in st.session_state.messages:
    if isinstance(message, AIMessage):
        with st.chat_message("AI"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human"):
            st.markdown(message.content)

# --- 사용자 입력 처리 ---
# 사용자가 채팅 입력창에 메시지를 입력하면 아래 코드가 실행됩니다.
if prompt := st.chat_input("질문을 입력해주세요."):
    # RAG 체인이 성공적으로 로드되었는지 확인
    if rag_chain:
        # 사용자 메시지를 대화 기록에 추가하고 화면에 표시
        st.session_state.messages.append(HumanMessage(content=prompt))
        with st.chat_message("Human"):
            st.markdown(prompt)

        # AI 답변 생성 및 표시 (스트리밍 방식)
        with st.chat_message("AI"):
            # st.write_stream은 스트리밍 출력을 처리하고, 전체 응답을 반환합니다.
            # 이를 통해 사용자는 답변이 생성되는 과정을 실시간으로 볼 수 있습니다.
            full_response = st.write_stream(rag_chain.stream({
                "human_input": prompt,
                "chat_history": st.session_state.messages
            }))
        
        # AI 메시지를 대화 기록에 추가 (스트리밍이 완료된 전체 메시지)
        st.session_state.messages.append(AIMessage(content=full_response))
    else:
        # RAG 체인 로드 실패 시 사용자에게 안내
        st.error("챗봇 시스템이 정상적으로 초기화되지 않았습니다. 설정을 확인해주세요.")
