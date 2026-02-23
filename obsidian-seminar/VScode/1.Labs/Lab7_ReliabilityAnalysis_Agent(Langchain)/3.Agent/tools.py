# tools.py
import io
import os
import json
import re
import contextlib
from typing import Dict, Any, List, Union

import streamlit as st
from langchain.tools import tool
import pandas as pd

from RA_code_v6 import (
    preprocess_and_summarize_data, find_best_distribution,
    analyze_single_distribution, check_parameter_homogeneity, setup_environment
)

setup_environment()

# --- Argument Parsing Helper Functions ---

def parse_string_input(input_data: Union[str, dict]) -> str:
    """Robustly parses string or dict input from LLM to get the actual string value."""
    if isinstance(input_data, dict):
        # If input is a dict, extract the first value.
        return str(next(iter(input_data.values()))) if input_data else ""
    
    if isinstance(input_data, str):
        try:
            # Try to load if it's a JSON string representing a dict
            parsed = json.loads(input_data.replace("'", '"'))
            if isinstance(parsed, dict):
                return str(next(iter(parsed.values())))
        except (json.JSONDecodeError, TypeError):
            # If it's not a dict-like JSON, return the string itself.
            return input_data.strip()
    
    return str(input_data)

def parse_blives_input(input_data: Union[List, str, None]) -> List[float]:
    """Robustly parses various B-life inputs (e.g., "B10", 10, "10") into a list of floats."""
    if input_data is None: return []
    
    if isinstance(input_data, list):
        processed_list = []
        for item in input_data:
            if isinstance(item, str):
                numbers = re.findall(r'\d+\.?\d*', item)
                if numbers:
                    processed_list.append(float(numbers[0]))
            elif isinstance(item, (int, float)):
                processed_list.append(float(item))
        return processed_list

    if isinstance(input_data, str):
        numbers = re.findall(r'\d+\.?\d*', input_data)
        return [float(num) for num in numbers]
        
    return []

def parse_list_input(input_data: Union[List, str, None]) -> List:
    if input_data is None: return []
    if isinstance(input_data, list): return input_data
    if isinstance(input_data, str):
        try:
            if ":" in input_data:
                parsed_json = json.loads(input_data.replace("'", '"'))
                return next(iter(parsed_json.values()))
            return json.loads(input_data.replace("'", '"'))
        except (json.JSONDecodeError, TypeError):
            return [item.strip() for item in input_data.split(',')]
    return []

# --- Tools ---

@tool
def data_summarizer_tool() -> Dict[str, Any]:
    """사용자가 데이터 요약, 전처리, 또는 그룹별 샘플 수 확인을 요청할 때 사용합니다."""
    st.write("🧰 **Tool Executing:** `data_summarizer_tool`")
    required_keys = ['uploaded_file_path', 'column_map', 'status_indicators']
    if not all(key in st.session_state and st.session_state[key] for key in required_keys):
        return {"error": "파일 업로드 및 컬럼 설정이 완료되지 않았습니다."}
    try:
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            grouped_data_from_func, summary_df = preprocess_and_summarize_data(
                file_path=st.session_state['uploaded_file_path'],
                column_map=st.session_state['column_map'],
                status_indicators=st.session_state['status_indicators']
            )
        
        # --- 데이터 형식 보정 로직 --- #
        # preprocess_and_summarize_data가 반환하는 값의 형식이 pandas Series일 수 있으므로,
        # 모든 도구가 안정적으로 사용할 수 있는 순수 Python list로 변환합니다.
        cleaned_grouped_data = {}
        for group, data in grouped_data_from_func.items():
            cleaned_grouped_data[group] = {
                'failures': list(data['failures']),
                'right_censored': list(data['right_censored'])
            }

        st.session_state['grouped_data'] = cleaned_grouped_data
        # --- 보정 로직 끝 --- #

        return {"dataframe": summary_df.to_dict('records'), "summary_text": output_buffer.getvalue()}
    except Exception as e:
        return {"error": f"데이터 요약 중 오류 발생: {e}"}

@tool
def best_distribution_finder_tool(distributions_to_fit: Union[List[str], str]) -> Dict[str, Any]:
    """사용자가 주어진 데이터셋에 대해서 최적 수명분포, 가장 잘 맞는 분포, 또는 여러 분포 비교를 요청할 때 사용합니다."""
    st.write(f"🧰 **Tool Executing:** `best_distribution_finder_tool`")
    try:
        distributions = parse_list_input(distributions_to_fit)
        if not distributions:
            distributions = ["Weibull_2P", "Lognormal_2P", "Normal_2P", "Exponential_1P"]
    except Exception as e:
        return {"error": f"분포 리스트 파싱 중 오류: {e}"}
    if 'grouped_data' not in st.session_state:
        return {"error": "데이터가 먼저 요약되어야 합니다."}
    try:
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            analysis_results, bic_df = find_best_distribution(st.session_state['grouped_data'], distributions)
        st.session_state['detailed_analysis_results'] = analysis_results
        plot_paths = [os.path.join("results", f) for f in ["probability_plot_all_groups.png", "BIC_comparison.png"]]
        return {"dataframe": bic_df.to_dict('records'), "results_text": output_buffer.getvalue(), "plot_paths": plot_paths}
    except Exception as e:
        return {"error": f"최적 분포 탐색 중 오류 발생: {e}"}

@tool
def detailed_distribution_analyzer_tool(
    group_name: Union[str, dict] = None, 
    distribution_name: str = None, 
    b_lives: Union[List, str] = None, 
    failure_prob_times: Union[List, str] = None
) -> Dict[str, Any]:
    """사용자가 특정 그룹과 분포에 대해 상세 분석, B-수명(B10 등), 또는 고장 확률 계산을 요청할 때 사용합니다. 'group_name'과 'distribution_name'은 필수입니다. 사용자가 그룹 이름을 지정하지 않으면, 다시 질문해야 합니다."""
    st.write(f"🧰 **Tool Executing:** `detailed_distribution_analyzer_tool`")
    
    args = {}
    if isinstance(group_name, dict): args = group_name
    elif isinstance(group_name, str) and group_name.strip().startswith('{'):
        try: args = json.loads(group_name.replace("'", '"'))
        except json.JSONDecodeError: pass

    final_group_name = args.get('group_name', group_name if isinstance(group_name, str) and not group_name.strip().startswith('{') else None)
    final_dist_name = args.get('distribution_name', distribution_name)
    
    if not final_group_name or not final_dist_name:
        return {"error": "필수 인자('group_name', 'distribution_name')가 누락되었습니다. 사용자에게 어떤 그룹을 분석할지 물어보세요."}

    try:
        b_lives_list = parse_blives_input(args.get('b_lives', b_lives))
        failure_prob_times_list = [float(x) for x in parse_list_input(args.get('failure_prob_times', failure_prob_times))]
    except Exception as e:
        return {"error": f"B-수명 또는 고장 확률 시간 리스트 파싱 중 오류: {e}"}

    if 'grouped_data' not in st.session_state:
        return {"error": "데이터가 먼저 요약되어야 합니다."}
        
    try:
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            # 1. analyze_single_distribution으로부터 fitter 객체를 직접 받음
            fitter_obj = analyze_single_distribution(
                st.session_state['grouped_data'], str(final_group_name), final_dist_name, 
                b_lives_list, failure_prob_times_list
            )
        
        # 2. fitter 객체의 .results 속성을 사용하여 DataFrame을 생성
        # 이 부분은 RA_code_v6.py의 analyze_single_distribution이 fitter를 반환한 후
        # print하던 로직을 tool로 옮겨온 것과 같습니다.
        results = {}
        params, values = [], []
        if final_dist_name == "Weibull_2P":
            params.extend(['Alpha', 'Beta'])
            values.extend([fitter_obj.alpha, fitter_obj.beta])
        elif final_dist_name in ["Lognormal_2P", "Normal_2P"]:
            params.extend(['Mu', 'Sigma'])
            values.extend([fitter_obj.mu, fitter_obj.sigma])
        elif final_dist_name == "Exponential_1P":
            params.append('Lambda')
            values.append(fitter_obj.Lambda)
        results['Parameter'] = params
        results['Value'] = values

        if b_lives_list:
            b_life_values = [fitter_obj.distribution.quantile(b/100) for b in b_lives_list]
            results['B-Life'] = [f'B{b}' for b in b_lives_list]
            results['B-Life Value'] = b_life_values
            
        if failure_prob_times_list:
            probs = [fitter_obj.distribution.CDF(t, show_plot=False) for t in failure_prob_times_list]
            results['Time'] = failure_prob_times_list
            results['Failure Probability'] = probs

        results_df = pd.DataFrame({k: pd.Series(v) for k, v in results.items()})

        plot_path = os.path.join("results", f"probability_plot_{final_group_name}_{final_dist_name}.png")
        return {"dataframe": results_df.to_dict('records'), "results_text": output_buffer.getvalue(), "plot_path": plot_path}
    except Exception as e:
        return {"error": f"상세 분포 분석 중 오류 발생: {e}"}

@tool
def parameter_homogeneity_checker_tool(distribution_name: Union[str, dict]) -> Dict[str, Any]:
    """사용자가 특정 분포(Weibull, Lognormal, Normal)를 지정하여 그룹 간 형상모수의 동일성 검토를 요청할 때 사용합니다.
    내부적으로 각 그룹에 대해 해당 분포로 상세 분석을 수행한 후, 그 결과를 바탕으로 모수 동일성을 검토합니다."""
    st.write(f"🧰 **Tool Executing:** `parameter_homogeneity_checker_tool`")

    try:
        dist_name_str = parse_string_input(distribution_name).lower()
    except Exception as e:
        return {"error": f"분포 이름 파싱 중 오류: {e}"}

    # 1. 분포 이름에 따라 검정할 파라미터와 fitter 이름을 결정
    if 'weibull' in dist_name_str:
        parameter_to_check = 'beta'
        selected_dist = 'Weibull_2P'
    elif 'lognormal' in dist_name_str:
        parameter_to_check = 'sigma'
        selected_dist = 'Lognormal_2P'
    elif 'normal' in dist_name_str:
        parameter_to_check = 'sigma'
        selected_dist = 'Normal_2P'
    elif 'exponential' in dist_name_str:
        return {"error": "지수분포는 단일 모수 분포이므로 형상 모수 동일성 검정을 수행할 수 없습니다."}
    else:
        return {"error": f"지원하지 않는 분포입니다: '{dist_name_str}'. Weibull, Lognormal, Normal 중에서 선택해주세요."}

    if 'grouped_data' not in st.session_state or not st.session_state['grouped_data']:
        return {"error": "세션에 grouped_data가 없습니다. 데이터 요약을 먼저 수행해야 합니다."}

    grouped_data = st.session_state['grouped_data']
    
    # 2. 각 그룹에 대해 개별 상세 분석을 수행하여 detailed_analysis_results 객체 생성
    st.write(f"⏳ 각 그룹에 대해 '{selected_dist}' 분포로 상세 분석을 수행합니다...")
    detailed_analysis_results = {}
    try:
        for group_name in grouped_data.keys():
            with io.StringIO() as buf, contextlib.redirect_stdout(buf):
                fitter_result = analyze_single_distribution(
                    grouped_data=grouped_data,
                    group_name=group_name,
                    distribution_name=selected_dist,
                    b_lives=[],
                    failure_prob_times=[]
                )
            # check_parameter_homogeneity가 기대하는 이중 딕셔너리 구조로 저장
            detailed_analysis_results[group_name] = {selected_dist: fitter_result}
            #detailed_analysis_results[group_name] = fitter_result

        st.session_state['detailed_analysis_results'] = detailed_analysis_results
        st.write("✅ 모든 그룹의 상세 분석 완료.")

    except Exception as e:
        return {"error": f"상세 분석 중 오류 발생: {e}"}

    # ###################
    # st.write(f"(1차)🔬 최종 '{parameter_to_check}' 모수 동일성 검정을 실행합니다...")
    # try:
    #     param_values = []
    #     for group, dists in detailed_analysis_results.items():
    #         first_dist_name = next(iter(dists))
    #         fitter = dists[first_dist_name]
            
    #         st.write(fitter)
    #         st.write(fitter.distribution)
    #         st.write(fitter.beta)
    #         st.write(fitter.beta_lower)
    #         st.write(fitter.beta_upper)
            
    #         # --- More robustly check for parameter and its confidence interval ---
    #         if hasattr(fitter, parameter_to_check):
    #             val = getattr(fitter, parameter_to_check)
    #             lower = getattr(fitter, f"{parameter_to_check}_lower", None)
    #             upper = getattr(fitter, f"{parameter_to_check}_upper", None)
                
    #             st.write(val)
    #             st.write(lower)
    #             st.write(upper)
                
    #             param_values.append({'Group': group, 'Parameter': parameter_to_check, 'Value': val, 'Lower CI': lower, 'Upper CI': upper})
                
    #             st.write(param_values)
        
    #     if not param_values: raise ValueError(f"모수 '{parameter_to_check}' 또는 해당 신뢰구간을 찾을 수 없습니다.")
    #     ###################
    # except Exception as e:
    #     return {"error": f"(1차) 모수 동일성 검토 중 오류 발생: {e}"}

    # 3. 생성된 결과를 바탕으로 모수 동일성 검정 실행
    st.write(f"🔬 최종 '{parameter_to_check}' 모수 동일성 검정을 실행합니다...")
    try:
        output_buffer = io.StringIO()
        with contextlib.redirect_stdout(output_buffer):
            results_df = check_parameter_homogeneity(
                analysis_results=detailed_analysis_results,
                parameter_to_check=parameter_to_check
            )
        
        plot_path = os.path.join("results", f"contour_plot_{parameter_to_check}.png")
        return {
            "dataframe": results_df.to_dict('records'), 
            "results_text": output_buffer.getvalue(), 
            "plot_path": plot_path
        }
    except Exception as e:
        return {"error": f"모수 동일성 검토 중 오류 발생: {e}"}
