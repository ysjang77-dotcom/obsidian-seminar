import streamlit as st
import pandas as pd
import os
from agent import create_agent_executor

# --- 1. App Configuration ---
st.set_page_config(
    page_title="신뢰성 분석 챗봇 (Reliability Analysis Chatbot)",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 신뢰성 분석 챗봇")
st.write("수명 데이터 파일을 업로드하고, 데이터 컬럼을 설정한 후 대화를 시작하세요.")

# --- 2. Session State Initialization & Agent Creation ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "is_configured" not in st.session_state:
    st.session_state.is_configured = False
if "agent_executor" not in st.session_state:
    # API 키가 성공적으로 로드되었을 때만 에이전트를 생성합니다.
    st.session_state.agent_executor = create_agent_executor()

# --- Helper function to parse and display tool output ---
def parse_and_display_tool_output(tool_output):
    """도구의 반환값을 파싱하여 적절한 Streamlit 컴포넌트로 출력합니다."""
    if not isinstance(tool_output, dict):
        st.write(tool_output)
        return

    if "error" in tool_output:
        st.error(f"오류가 발생했습니다: {tool_output['error']}")

    if "dataframe" in tool_output and tool_output["dataframe"]:
        st.dataframe(pd.DataFrame(tool_output["dataframe"]))

    if "summary_text" in tool_output:
        st.markdown(f"**요약:**\n```\n{tool_output['summary_text']}\n```")
    
    if "results_text" in tool_output:
        st.markdown(f"**분석 결과:**\n```\n{tool_output['results_text']}\n```")

    if "plot_path" in tool_output and os.path.exists(tool_output["plot_path"]):
        st.image(tool_output["plot_path"])

    if "plot_paths" in tool_output:
        for path in tool_output["plot_paths"]:
            if os.path.exists(path):
                st.image(path)

# --- 3. UI - File Upload & Column Mapping ---
uploaded_file = st.file_uploader(
    "수명 데이터 파일(.csv, .xlsx)을 업로드하세요.",
    type=["csv", "xlsx"],
    on_change=lambda: st.session_state.update(is_configured=False, messages=[], agent_memory=None) 
)

if uploaded_file is not None:
    temp_dir = "temp"
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    
    file_path = os.path.join(temp_dir, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    st.session_state.uploaded_file_path = file_path
    
    st.success(f"파일 '{uploaded_file.name}'이 성공적으로 업로드되었습니다.")

    with st.expander("⚙️ 분석 설정 (Configuration)", expanded=not st.session_state.is_configured):
        try:
            df = pd.read_csv(file_path) if file_path.endswith('.csv') else pd.read_excel(file_path)
            st.dataframe(df.head())

            with st.form("column_mapping_form"):
                st.subheader("1. 데이터 컬럼 설정")
                columns = df.columns.tolist()
                time_col = st.selectbox("수명/고장 시간", columns, index=min(0, len(columns)-1))
                status_col = st.selectbox("고장/관측중단 상태", columns, index=min(1, len(columns)-1))
                stress_col = st.selectbox("스트레스/그룹", columns, index=min(2, len(columns)-1))
                
                st.subheader("2. 상태 지시자 설정")
                failure_indicator = st.text_input("고장(Failure) 표시 값", "f")
                censored_indicator = st.text_input("관측중단(Censored) 표시 값", "c")

                if st.form_submit_button("분석 시작"):
                    st.session_state.column_map = {"time": time_col, "status": status_col, "stress": stress_col}
                    st.session_state.status_indicators = {"failure": failure_indicator, "censored": censored_indicator}
                    st.session_state.is_configured = True
                    st.success("설정이 완료되었습니다! 이제 아래 채팅창에서 분석을 시작할 수 있습니다.")
        
        except Exception as e:
            st.error(f"파일을 처리하는 중 오류가 발생했습니다: {e}")


# --- 4. Chat Interface ---
# 에이전트가 성공적으로 생성되었고, 파일 설정이 완료되었을 때만 챗봇 UI를 표시합니다.
if st.session_state.agent_executor and st.session_state.is_configured:
    st.subheader("💬 챗봇")
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            if isinstance(message["content"], dict):
                parse_and_display_tool_output(message["content"])
            else:
                st.markdown(message["content"])

    if prompt := st.chat_input("분석할 내용을 입력하세요... (예: 데이터 요약해줘)"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("생각 중..."):
                try:
                    response = st.session_state.agent_executor.invoke(
                        {"input": prompt}
                    )
                    
                    if "intermediate_steps" in response and response["intermediate_steps"]:
                        for step in response["intermediate_steps"]:
                            _, tool_output = step
                            parse_and_display_tool_output(tool_output)
                    
                    final_answer = response.get("output", "죄송합니다, 답변을 생성하지 못했습니다.")
                    st.markdown(final_answer)
                    
                    st.session_state.messages.append({"role": "assistant", "content": final_answer})

                except Exception as e:
                    error_message = f"에이전트 실행 중 오류가 발생했습니다: {e}"
                    st.error(error_message)
                    st.session_state.messages.append({"role": "assistant", "content": error_message})
elif not st.session_state.agent_executor:
    st.warning("에이전트가 초기화되지 않았습니다. API 키 설정을 확인하세요.")
else:
    st.info("데이터 파일을 업로드하고 분석 설정을 완료하면 챗봇이 활성화됩니다.")