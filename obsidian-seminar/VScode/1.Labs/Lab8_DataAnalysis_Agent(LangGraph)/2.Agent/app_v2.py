import streamlit as st
import pandas as pd
from typing import Tuple, List, Dict, Any
import numpy as np
import reliability
from reliability.Fitters import (
    Fit_Weibull_2P,
    Fit_Lognormal_2P,
    Fit_Exponential_1P,
    Fit_Normal_2P,
    Fit_Gamma_2P
)
from reliability.Probability_plotting import (
    Weibull_probability_plot,
    Lognormal_probability_plot,
    Exponential_probability_plot,
    Normal_probability_plot,
    Gamma_probability_plot
)
import matplotlib.pyplot as plt
import io
import os
from functools import partial

# --- LangChain 및 LangGraph 관련 임포트 ---
from langchain.agents import Tool, AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, END

# --- 0. 환경 설정 및 API 키 확인 ---
# .env 파일이 있다면 로드 (예: 로컬 개발 환경)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass # dotenv가 설치되지 않아도 괜찮음

# Streamlit secrets 또는 환경 변수에서 API 키 확인
if 'GOOGLE_API_KEY' not in os.environ:
    try:
        os.environ['GOOGLE_API_KEY'] = st.secrets['GOOGLE_API_KEY']
    except (KeyError, AttributeError):
        st.error("오류: GOOGLE_API_KEY가 설정되지 않았습니다. Streamlit secrets 또는 환경 변수를 설정해주세요.")
        st.stop()

# --- 1. 데이터 전처리 함수 ---
def load_and_preprocess_data(uploaded_file) -> Tuple[List[float], List[float]]:
    """
    업로드된 파일을 읽고 전처리하여 failures와 right_censored 리스트를 생성합니다.
    """
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
    except Exception as e:
        raise ValueError(f"파일을 읽는 중 오류가 발생했습니다: {e}")

    if 'time' not in df.columns or 'censor' not in df.columns:
        raise ValueError("데이터에 'time'과 'censor' 컬럼이 모두 포함되어야 합니다.")

    failures = df[df['censor'] == 0]['time'].tolist()
    right_censored = df[df['censor'] == 1]['time'].tolist()
    return failures, right_censored

# --- 2. 핵심 분석 도구 함수 ---
# 함수 이름 변경 (func -> func_name)하여 @tool로 정의된 도구와 구분
def summarize_data_func(failures: list, right_censored: list) -> dict:
    """
    데이터의 기본 통계 정보를 요약합니다.
    """
    num_failures = len(failures)
    num_right_censored = len(right_censored)
    total_samples = num_failures + num_right_censored
    censoring_rate = (num_right_censored / total_samples) * 100 if total_samples > 0 else 0
    all_data = failures + right_censored
    stats = {
        "총 샘플 수": total_samples, "고장 수": num_failures,
        "우측관측중단 수": num_right_censored, "중도절단 비율 (%)": f"{censoring_rate:.2f}",
        "평균": np.mean(all_data) if all_data else 0, "표준편차": np.std(all_data) if all_data else 0,
        "최소값": np.min(all_data) if all_data else 0, "최대값": np.max(all_data) if all_data else 0,
    }
    return stats

def find_best_distribution_func(failures: list, right_censored: list) -> dict:
    """
    주어진 데이터에 대해 여러 분포를 피팅하고 BIC가 가장 낮은 최적 분포를 찾습니다.
    각 후보 분포의 상세 추정 결과(파라미터, BIC, AICc 등)를 함께 반환합니다.
    """
    distributions = {
        "Weibull_2P": Fit_Weibull_2P, "Lognormal_2P": Fit_Lognormal_2P,
        "Exponential_1P": Fit_Exponential_1P, "Normal_2P": Fit_Normal_2P, "Gamma_2P": Fit_Gamma_2P,
    }
    param_names_map = {
        "Weibull_2P": ["Alpha", "Beta"], "Lognormal_2P": ["Mu", "Sigma"],
        "Exponential_1P": ["Lambda"], "Normal_2P": ["Mu", "Sigma"],
        "Gamma_2P": ["Alpha", "Beta"],
    }
    
    results_list = []
    if not failures and not right_censored:
        return {"best_distribution_name": "No data", "bic_results": pd.DataFrame()}

    for name, fitter_class in distributions.items():
        try:
            fitter = fitter_class(failures=failures, right_censored=right_censored)
            
            # 파라미터 값을 문자열로 포맷팅
            params_list = []
            for param_name in param_names_map[name]:
                p_name_lower = param_name.lower()
                attr_name = 'lambda_' if p_name_lower == 'lambda' else p_name_lower
                param_value = getattr(fitter, attr_name)
                params_list.append(f"{param_name}={param_value:.4f}")
            params_str = ", ".join(params_list)

            results_list.append({
                "Distribution": name,
                "BIC": fitter.BIC,
                "AICc": fitter.AICc,
                "Log-likelihood": fitter.loglik,
                "Parameters": params_str
            })
        except Exception:
            # 특정 분포 피팅에 실패하더라도 계속 진행
            results_list.append({
                "Distribution": name, "BIC": np.inf, "AICc": np.inf,
                "Log-likelihood": np.nan, "Parameters": "Fit Failed"
            })

    results_df = pd.DataFrame(results_list)
    results_df = results_df.sort_values(by="BIC").reset_index(drop=True)
    
    best_dist_name = results_df.iloc[0]["Distribution"]
    
    # bic_results 키를 유지하되, 상세 결과가 담긴 데이터프레임을 전달
    return {"best_distribution_name": best_dist_name, "bic_results": results_df}

def analyze_distribution_func(failures: list, right_censored: list, dist_name: str, p_values: list, t_values: list, cl: float) -> Dict[str, Any]:
    """
    지정된 분포에 대해 상세 분석을 수행하고 결과를 반환합니다.
    """
    # 타입 안정성 확보: dist_name이 문자열이 아닐 경우 오류 발생
    if not isinstance(dist_name, str):
        raise TypeError(f"Distribution name must be a string, but got {type(dist_name)}")

    fitter_map = {
        "Weibull_2P": Fit_Weibull_2P, "Lognormal_2P": Fit_Lognormal_2P,
        "Exponential_1P": Fit_Exponential_1P, "Normal_2P": Fit_Normal_2P, "Gamma_2P": Fit_Gamma_2P,
    }
    
    dist_name_mapping = {
        "weibull": "Weibull_2P", "lognormal": "Lognormal_2P", "exponential": "Exponential_1P",
        "normal": "Normal_2P", "gamma": "Gamma_2P", "weibull_2p": "Weibull_2P",
        "lognormal_2p": "Lognormal_2P", "exponential_1p": "Exponential_1P",
        "normal_2p": "Normal_2P", "gamma_2p": "Gamma_2P",
    }
    
    final_dist_name = dist_name_mapping.get(dist_name.lower(), dist_name)

    if final_dist_name not in fitter_map:
        raise ValueError(f"지원하지 않는 분포입니다: {dist_name}")

    # 각 분포의 파라미터 이름을 명시적으로 정의하여 안정성 확보
    param_names_map = {
        "Weibull_2P": ["Alpha", "Beta"],
        "Lognormal_2P": ["Mu", "Sigma"],
        "Exponential_1P": ["Lambda"],
        "Normal_2P": ["Mu", "Sigma"],
        "Gamma_2P": ["Alpha", "Beta"],
    }

    fitter = fitter_map[final_dist_name](failures=failures, right_censored=right_censored)
    
    params_data = []
    # 불안정한 fitter.distribution.parameters 대신 명시적으로 정의된 파라미터 이름 리스트 사용
    for param_name in param_names_map[final_dist_name]:
        p_name_lower = param_name.lower()
        # 'lambda' 예약어 충돌 방지
        attr_name = 'lambda_' if p_name_lower == 'lambda' else p_name_lower
        
        point_estimate = getattr(fitter, attr_name)
        lower_ci = getattr(fitter, f"{attr_name}_lower")
        upper_ci = getattr(fitter, f"{attr_name}_upper")
        params_data.append([param_name, point_estimate, lower_ci, upper_ci])
    
    param_df = pd.DataFrame(params_data, columns=['Parameter', 'Point Estimate', 'Lower CI', 'Upper CI'])

    # 각 분포에 맞는 확률지 도시 함수를 명시적으로 매핑합니다.
    plot_func_map = {
        "Weibull_2P": Weibull_probability_plot,
        "Lognormal_2P": Lognormal_probability_plot,
        "Exponential_1P": Exponential_probability_plot,
        "Normal_2P": Normal_probability_plot,
        "Gamma_2P": Gamma_probability_plot,
    }

    fig, ax = plt.subplots()
    # 1. 분포에 맞는 확률지 함수를 호출하여 데이터 포인트를 플로팅합니다.
    plot_func = plot_func_map[final_dist_name]
    plot_func(failures=failures, right_censored=right_censored)
    
    # 2. 적합된 분포의 CDF(누적분포함수) 라인을 같은 플롯에 추가로 그립니다.
    fitter.distribution.CDF(show_plot=True, label=f'Fitted {final_dist_name}')
    ax.set_title(f'{final_dist_name} Probability Plot')
    ax.legend()

    buf = io.BytesIO()
    fig.savefig(buf, format="png")
    buf.seek(0)
    plot_image = buf.getvalue()
    plt.close(fig)

    # CDF 결과가 튜플이 아닐 경우를 대비한 방어 코드
    def get_b_life(p):
        result = fitter.distribution.CDF(CI_type='time', CI_y=p/100, CI=cl)
        return (result, result, result) if isinstance(result, float) else result

    def get_cdf_val(t):
        result = fitter.distribution.CDF(CI_type='reliability', CI_x=t, CI=cl)
        return (result, result, result) if isinstance(result, float) else result

    b_life_data = [[p, *get_b_life(p)] for p in p_values]
    b_life_df = pd.DataFrame(b_life_data, columns=['p', 'Lower', 'Point', 'Upper'])
    
    cdf_data = [[t, *get_cdf_val(t)] for t in t_values]
    cdf_df = pd.DataFrame(cdf_data, columns=['t', 'Lower', 'Point', 'Upper'])
    
    return {
        "parameter_table": param_df, "probability_plot": plot_image,
        "b_life_table": b_life_df, "cdf_table": cdf_df,
    }

# --- 3. LangGraph 워크플로우 정의 ---
class GraphState(TypedDict):
    failures: List[float]; right_censored: List[float]; p_values: List[float]
    t_values: List[float]; cl: float; summary_stats: Dict[str, Any]
    bic_results: pd.DataFrame; best_dist_name: str
    analysis_results: Dict[str, Any]; final_report: str

def summarize_data_node(state: GraphState):
    state['summary_stats'] = summarize_data_func(state['failures'], state['right_censored'])
    return state
def find_best_distribution_node(state: GraphState):
    results = find_best_distribution_func(state['failures'], state['right_censored'])
    state['best_dist_name'] = results['best_distribution_name']
    state['bic_results'] = results['bic_results']
    return state
def analyze_best_distribution_node(state: GraphState):
    # `analyze_distribution_func`에 필요한 인자를 명시적으로 매핑하여 전달
    analysis_args = {
        "failures": state["failures"],
        "right_censored": state["right_censored"],
        "dist_name": state["best_dist_name"],  # state의 'best_dist_name'을 'dist_name'으로 전달
        "p_values": state["p_values"],
        "t_values": state["t_values"],
        "cl": state["cl"],
    }
    state['analysis_results'] = analyze_distribution_func(**analysis_args)
    return state
def generate_report_node(state: GraphState):
    summary_df = pd.DataFrame(list(state['summary_stats'].items()), columns=['항목', '값'])

    # .get()을 사용하여 키가 없는 경우에도 안전하게 접근하고, 기본값으로 빈 DataFrame을 제공
    bic_results_df = state.get('bic_results', pd.DataFrame())
    analysis_results = state.get('analysis_results', {})
    param_table_df = analysis_results.get('parameter_table', pd.DataFrame())
    b_life_table_df = analysis_results.get('b_life_table', pd.DataFrame())
    cdf_table_df = analysis_results.get('cdf_table', pd.DataFrame())

    # 데이터프레임이 비어있지 않은 경우에만 markdown으로 변환, 아닐 경우 정보 메시지 표시
    summary_md = summary_df.to_markdown(index=False) if not summary_df.empty else "데이터 요약 정보 없음"
    bic_results_md = bic_results_df.to_markdown(index=False) if not bic_results_df.empty else "BIC 결과 없음"
    param_table_md = param_table_df.to_markdown(index=False) if not param_table_df.empty else "파라미터 정보 없음"
    b_life_table_md = b_life_table_df.to_markdown(index=False) if not b_life_table_df.empty else "B-Life 정보 없음"
    cdf_table_md = cdf_table_df.to_markdown(index=False) if not cdf_table_df.empty else "누적고장확률 정보 없음"

    # 결론 요약 부분도 안전하게 생성
    conclusion_summary = "결론 요약 불가"
    p_values = state.get('p_values')
    t_values = state.get('t_values')
    if p_values and t_values and not b_life_table_df.empty and not cdf_table_df.empty:
        try:
            conclusion_summary = f"""본 분석 결과, 제공된 데이터는 {state.get('best_dist_name', 'N/A')} 분포를 따르는 것으로 나타났습니다. 
B{p_values[0]} 수명은 약 {b_life_table_df['Point'].iloc[0]:.2f} 시간으로 추정되며, {t_values[-1]} 시간까지의 누적 고장 확률은 약 {cdf_table_df['Point'].iloc[-1]*100:.1f}%로 예측됩니다."""
        except (IndexError, KeyError):
            conclusion_summary = "결론 요약에 필요한 데이터가 부족합니다."

    report = f"""### 신뢰성 수명 데이터 분석 최종 보고서
**1. 데이터 요약**
{summary_md}\n\n
**2. 최적 분포 결정**
가장 낮은 BIC 값을 보인 **{state.get('best_dist_name', 'N/A')}** 분포가 최적 분포로 선정되었습니다.
{bic_results_md}\n\n
**3. 최적 분포 분석 결과 ({state.get('best_dist_name', 'N/A')})**
*   **추정 파라미터 ({state.get('cl', 0.95)*100:.0f}% CI):**\n
{param_table_md}\n
*   **확률지:**\n
*(이미지는 UI에서 별도로 표시됩니다)*\n
**4. 신뢰성 측도 ({state.get('cl', 0.95)*100:.0f}% CI)**\n
*   **B-Life:**\n
{b_life_table_md}\n
*   **누적고장확률:**\n
{cdf_table_md}\n
**5. 결론 요약**\n
{conclusion_summary}"""
    state['final_report'] = report
    return state

workflow = StateGraph(GraphState)
workflow.add_node("summarize_data", summarize_data_node)
workflow.add_node("find_best_distribution", find_best_distribution_node)
workflow.add_node("analyze_best_distribution", analyze_best_distribution_node)
workflow.add_node("generate_report", generate_report_node)
workflow.set_entry_point("summarize_data")
workflow.add_edge("summarize_data", "find_best_distribution")
workflow.add_edge("find_best_distribution", "analyze_best_distribution")
workflow.add_edge("analyze_best_distribution", "generate_report")
workflow.add_edge("generate_report", END)
app_graph = workflow.compile()

# --- 4. LangChain 에이전트 및 도구 정의 ---
def run_full_analysis_func(failures: list, right_censored: list, p_values: list, t_values: list, cl: float) -> dict:
    """
    전체 신뢰성 분석 워크플로우를 실행하고 최종 보고서와 확률지 이미지를 반환합니다.
    """
    initial_state = {"failures": failures, "right_censored": right_censored, "p_values": p_values, "t_values": t_values, "cl": cl}
    final_state = app_graph.invoke(initial_state)
    return {
        "report": final_state['final_report'],
        "plot": final_state['analysis_results']['probability_plot']
    }

llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0)

# 시스템 프롬프트를 수정하여 에이전트에게 컨텍스트 제공
system_message = """You are an expert AI assistant for reliability engineering analysis.
Your primary goal is to help users analyze lifetime data using the provided tools.
The user has already uploaded their data, and it is available to all tools. Do not ask for the data.

**Tool Usage Instructions:**
1.  **Distribution Names:** When the user mentions a distribution like 'Weibull' or 'lognormal', you must call the `analyze_distribution` tool. The tool is designed to handle common variations of distribution names (e.g., 'weibull', 'Weibull_2P').
2.  **User Intent:** Carefully analyze the user's request to choose the correct tool:
    *   For a general overview: use `summarize_data`.
    *   To find the best-fitting distribution: use `find_best_distribution`.
    *   To analyze a *specific* distribution: use `analyze_distribution`.
    *   For a complete, automated analysis from start to finish: use `run_full_analysis`.
3.  **Output Formatting:** When presenting results from a tool, especially `analyze_distribution` or `run_full_analysis`, do the following:
    *   Clearly state which distribution was analyzed.
    *   Present all tables (parameters, B-Life, CDF) in a clean markdown format.
    *   Display the probability plot image.
    *   Conclude with a brief, insightful summary of the key findings, such as the estimated B10 life or the failure probability at a certain time.
"""

prompt_template = ChatPromptTemplate.from_messages([
    ("system", system_message),
    ("placeholder", "{chat_history}"),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}"),
])

# --- 5. Streamlit UI 구성 ---
st.title("대화형 신뢰성 분석 AI 에이전트")

with st.sidebar:
    st.title("분석 설정")
    uploaded_file = st.file_uploader("수명 데이터 파일(CSV 또는 XLSX)", type=["csv", "xlsx"])
    confidence_level = st.slider("신뢰수준 (Confidence Level)", 0.50, 0.99, 0.95, 0.01)
    p_values_input = st.text_input("B-Life 백분율 (p) 값 (쉼표로 구분)", "10, 50")
    t_values_input = st.text_input("누적고장확률 시간 (t) 값 (쉼표로 구분)", "100, 500")

    if uploaded_file:
        try:
            st.session_state.failures, st.session_state.right_censored = load_and_preprocess_data(uploaded_file)
            st.success("파일이 성공적으로 로드 및 전처리되었습니다.")
            st.subheader("데이터 요약")
            st.write(f"고장 데이터 수: {len(st.session_state.failures)}")
            st.write(f"우측관측중단 데이터 수: {len(st.session_state.right_censored)}")
        except ValueError as e:
            st.error(f"데이터 처리 오류: {e}")
            st.session_state.clear()

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "안녕하세요! 분석할 데이터를 업로드하고 원하는 분석을 요청해주세요."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        # 컨텐츠 타입에 따라 다르게 렌더링
        if isinstance(message["content"], str):
            st.markdown(message["content"])
        elif isinstance(message["content"], dict) and "plot" in message["content"]:
            st.markdown(message["content"]["report"])
            st.image(message["content"]["plot"], caption="확률지(Probability Plot)")

# --- 6. 사용자 입력 및 에이전트 실행 ---
if prompt := st.chat_input("무엇을 도와드릴까요?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        if "failures" not in st.session_state:
            st.warning("분석을 시작하기 전에 데이터 파일을 업로드해주세요.")
            st.stop()
        try:
            p_values = [float(p.strip()) for p in p_values_input.split(',')]
            t_values = [float(t.strip()) for t in t_values_input.split(',')]
        except ValueError:
            st.error("B-Life와 CDF 시간 값은 쉼표로 구분된 숫자 형식이어야 합니다.")
            st.stop()

        # --- @tool 데코레이터를 사용하여 도구를 정의 ---
        # 이 방식은 함수의 시그니처와 Docstring을 자동으로 파싱하여
        # LangChain 에이전트가 도구의 사용법을 명확하게 이해하도록 만듭니다.
        # 이를 통해 이전의 모든 인자 관련 오류를 근본적으로 해결합니다.
        from langchain.tools import tool

        @tool
        def summarize_data() -> dict:
            """업로드된 수명 데이터의 기본 통계 정보를 요약합니다. 고장 수, 관측중단 수, 평균 수명 등을 계산할 때 사용합니다."""
            return summarize_data_func(
                failures=st.session_state.failures, 
                right_censored=st.session_state.right_censored
            )

        @tool
        def find_best_distribution() -> dict:
            """데이터에 가장 적합한 확률 분포를 찾습니다. 여러 후보 분포(Weibull, Lognormal 등)를 피팅하고 BIC 기준으로 최적 분포를 결정합니다."""
            return find_best_distribution_func(
                failures=st.session_state.failures, 
                right_censored=st.session_state.right_censored
            )

        @tool
        def analyze_distribution(dist_name: str) -> Dict[str, Any]:
            """
            특정 확률 분포에 대한 상세 분석을 수행합니다. 
            파라미터 추정, 신뢰구간 계산, 확률지(probability plot) 생성, B-Life 및 누적고장확률(CDF)을 계산할 때 사용합니다.
            """
            return analyze_distribution_func(
                failures=st.session_state.failures,
                right_censored=st.session_state.right_censored,
                dist_name=dist_name,
                p_values=p_values,
                t_values=t_values,
                cl=confidence_level
            )

        @tool
        def run_full_analysis() -> dict:
            """전체 자동 분석을 수행하고 최종 보고서를 생성합니다. 사용자가 '자동 분석', '전체 분석 실행' 등 포괄적인 분석을 요청할 때 사용합니다."""
            return run_full_analysis_func(
                failures=st.session_state.failures,
                right_censored=st.session_state.right_censored,
                p_values=p_values,
                t_values=t_values,
                cl=confidence_level
            )

        tools_with_data = [
            summarize_data,
            find_best_distribution,
            analyze_distribution,
            run_full_analysis,
        ]
        
        agent = create_tool_calling_agent(llm, tools_with_data, prompt_template)
        agent_executor = AgentExecutor(agent=agent, tools=tools_with_data, verbose=True)
        
        # LangChain에 전달할 chat_history를 AIMessage/HumanMessage 형식으로 변환
        # UI용으로 저장된 dict 객체를 모델이 이해할 수 있는 문자열로 변환
        from langchain_core.messages import HumanMessage, AIMessage

        formatted_history = []
        for msg in st.session_state.messages[:-1]:
            content = msg["content"]
            if msg["role"] == "user":
                formatted_history.append(HumanMessage(content=content))
            elif msg["role"] == "assistant":
                # UI 렌더링을 위해 저장된 dict는 report 부분만 문자열로 추출
                if isinstance(content, dict) and "report" in content:
                    formatted_history.append(AIMessage(content=content["report"]))
                elif isinstance(content, str):
                    formatted_history.append(AIMessage(content=content))
                # 다른 dict 형태가 있다면 문자열로 변환 (안전장치)
                elif isinstance(content, dict):
                    formatted_history.append(AIMessage(content=str(content)))
        
        try:
            response_container = st.empty()
            final_response_object = None

            for chunk in agent_executor.stream({"input": prompt, "chat_history": formatted_history}):
                if "actions" in chunk:
                    response_container.markdown(f"Tool Call: `{chunk['actions'][0].tool}`")
                elif "steps" in chunk:
                    result = chunk["steps"][0].observation
                    final_response_object = result # 최종 결과 저장
                    # 중간 결과 렌더링
                    if isinstance(result, dict):
                        if "best_distribution_name" in result:
                            st.markdown("#### 최적 분포 탐색 결과"); st.dataframe(result["bic_results"])
                            st.info(f"**최적 분포:** {result['best_distribution_name']}")
                        elif "parameter_table" in result:
                            st.markdown("#### 분포 분석 결과"); st.dataframe(result["parameter_table"])
                            st.image(result["probability_plot"], caption="확률지")
                            st.markdown("##### B-Life"); st.dataframe(result["b_life_table"])
                            st.markdown("##### 누적고장확률 (CDF)"); st.dataframe(result["cdf_table"])
                        elif "report" in result and "plot" in result: # 자동 분석 결과
                            st.markdown(result["report"])
                            st.image(result["plot"], caption="확률지")
                        else:
                            st.markdown("#### 데이터 요약"); st.dataframe(pd.DataFrame(list(result.items()), columns=['항목', '값']))
                elif "output" in chunk:
                    final_response_object = chunk["output"]
                    response_container.markdown(final_response_object)
            
            st.session_state.messages.append({"role": "assistant", "content": final_response_object})

        except Exception as e:
            error_message = f"분석 중 오류가 발생했습니다: {e}"
            st.error(error_message)
            st.session_state.messages.append({"role": "assistant", "content": error_message})