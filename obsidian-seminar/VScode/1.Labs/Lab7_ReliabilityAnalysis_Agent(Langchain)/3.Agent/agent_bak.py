# agent.py
import os
import re
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain import hub
from langchain.schema import AgentFinish, OutputParserException

# tools.py에서 정의한 도구들을 가져옵니다.
from tools import (
    data_summarizer_tool,
    best_distribution_finder_tool,
    detailed_distribution_analyzer_tool,
    parameter_homogeneity_checker_tool,
)

def get_gemini_api_key():
    # ... (function remains the same)
    if "GEMINI_API_KEY" in st.secrets and st.secrets["GEMINI_API_KEY"]:
        return st.secrets["GEMINI_API_KEY"]
    if "GEMINI_API_KEY" in os.environ and os.environ["GEMINI_API_KEY"]:
        return os.environ["GEMINI_API_KEY"]
    return None

def handle_parsing_error(error: OutputParserException) -> AgentFinish:
    """
    LLM의 출력을 파싱하지 못할 때 호출되는 함수입니다.
    오류 메시지에서 LLM의 원본 응답을 추출하여 최종 답변으로 반환합니다.
    """
    # LangChain v0.2.0 이후, llm_output은 error 객체에 직접 포함되지 않을 수 있습니다.
    # 대신, 오류의 문자열 표현에 원본 출력이 포함됩니다.
    error_text = str(error)
    
    # 정규 표현식을 사용하여 `Could not parse LLM output:` 뒤의 내용을 추출합니다.
    match = re.search(r"Could not parse LLM output: `(.*)`", error_text, re.DOTALL)
    
    if match:
        # 정규 표현식으로 추출한 내용을 최종 답변으로 사용합니다.
        final_answer = match.group(1).strip()
    else:
        # 매칭 실패 시, 일반적인 오류 메시지를 표시합니다.
        final_answer = "죄송합니다, 답변을 처리하는 데 문제가 발생했습니다. 질문을 다시 시도해 주세요."
        
    # AgentExecutor가 이해할 수 있는 AgentFinish 형태로 반환합니다.
    return AgentFinish(return_values={"output": final_answer}, log=error_text)


def create_agent_executor():
    """
    LangChain 에이전트 실행기(AgentExecutor)를 생성하고 반환합니다.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        st.error("Gemini API 키를 찾을 수 없습니다.")
        # ... (error message remains the same)
        return None

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash", 
        google_api_key=api_key,
        temperature=0.1,
        convert_system_message_to_human=True
    )

    tools = [
        data_summarizer_tool,
        best_distribution_finder_tool,
        detailed_distribution_analyzer_tool,
        parameter_homogeneity_checker_tool,
    ]

    prompt = hub.pull("hwchase17/react-chat")

    if "agent_memory" not in st.session_state:
        st.session_state.agent_memory = ConversationBufferWindowMemory(
            k=5, memory_key="chat_history", input_key="input",
            output_key="output", return_messages=True
        )
    memory = st.session_state.agent_memory

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent, tools=tools, memory=memory, verbose=True,
        # 파싱 오류 발생 시, 직접 정의한 handle_parsing_error 함수를 사용하도록 설정
        handle_parsing_errors=handle_parsing_error,
        max_iterations=5, return_intermediate_steps=True
    )

    return agent_executor
