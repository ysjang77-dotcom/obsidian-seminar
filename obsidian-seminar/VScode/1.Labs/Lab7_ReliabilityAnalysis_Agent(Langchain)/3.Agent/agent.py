import os
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents import AgentExecutor, create_react_agent
from langchain.memory import ConversationBufferWindowMemory
from langchain.prompts import ChatPromptTemplate

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

def create_agent_executor():
    """
    LangChain 에이전트 실행기(AgentExecutor)를 생성하고 반환합니다.
    """
    api_key = get_gemini_api_key()
    if not api_key:
        st.error("Gemini API 키를 찾을 수 없습니다.")
        st.info("Please add your Gemini API key to the .streamlit/secrets.toml file.")
        st.stop()

    llm = ChatGoogleGenerativeAI(
        model="gemini-1.5-flash", 
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

    # 페르소나와 대화 형식을 포함하는 새로운 프롬프트 템플릿
    prompt_template = """Assistant is a large language model trained by Google.

### 페르소나 (Persona) ###
저는 수십 년간의 경험을 가진 세계 최고 수준의 신뢰성 분석 전문가입니다.
저의 목표는 복잡한 통계 개념과 분석 과정을 누구나 이해할 수 있도록 돕는 것입니다.
특히 통계 분석을 처음 접하는 분들을 위해, 저는 마치 친절한 선생님처럼 단계별로, 그리고 아주 상세하게 모든 것을 설명해 드릴 것입니다.
어려운 용어나 개념이 있다면 주저하지 말고 질문해주세요. 어떤 질문이든 환영하며, 여러분이 완벽하게 이해할 때까지 돕겠습니다.
함께 데이터 속에 숨겨진 의미를 찾아가는 즐거운 여정을 시작해 봅시다.

### 도구 사용 지침 (Instructions on Tool Use) ###
To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: The action to take, should be one of [{tool_names}]
Action Input: The input to the action
Observation: The result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Here are the tools you have access to:
{tools}

### 대화 시작 (Begin Conversation) ###
Begin!

Previous conversation history:
{chat_history}

New input: {input}
{agent_scratchpad}
"""
    prompt = ChatPromptTemplate.from_template(prompt_template)

    if "agent_memory" not in st.session_state:
        st.session_state.agent_memory = ConversationBufferWindowMemory(
            k=5, memory_key="chat_history", input_key="input",
            output_key="output", return_messages=True
        )
    memory = st.session_state.agent_memory

    agent = create_react_agent(llm, tools, prompt)

    agent_executor = AgentExecutor(
        agent=agent, tools=tools, memory=memory, verbose=True,
        # 표준 오류 처리 방식을 사용하여 에이전트가 스스로 오류를 수정하도록 유도
        handle_parsing_errors=True,
        max_iterations=10, 
        return_intermediate_steps=True
    )

    return agent_executor
