# -*- coding: utf-8 -*-
import os
import logging
import platform
from typing import List, Dict, Any, Union, Tuple

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import font_manager
from reliability.Fitters import (
    Fit_Weibull_2P, Fit_Lognormal_2P, Fit_Normal_2P,
    Fit_Exponential_1P
)

# --- 전역 설정 ---
RESULTS_DIR = "results"
LOG_FILE = "analysis_log.log"
DISTRIBUTION_MAP = {
    "Weibull_2P": Fit_Weibull_2P, "Lognormal_2P": Fit_Lognormal_2P,
    "Normal_2P": Fit_Normal_2P, "Exponential_1P": Fit_Exponential_1P,
}
FRIENDLY_DIST_MAP = {
    "weibull": "Weibull_2P", "weibull_2p": "Weibull_2P",
    "lognormal": "Lognormal_2P", "lognormal_2p": "Lognormal_2P",
    "normal": "Normal_2P", "normal_2p": "Normal_2P",
    "exponential": "Exponential_1P", "exponential_1p": "Exponential_1P",
    "Weibull_2P": "Weibull_2P", "Lognormal_2P": "Lognormal_2P",
    "Normal_2P": "Normal_2P", "Exponential_1P": "Exponential_1P",
}

# --- 헬퍼 함수 ---
def setup_environment():
    if not os.path.exists(RESULTS_DIR): os.makedirs(RESULTS_DIR)
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s [%(levelname)s] - %(message)s",
        handlers=[logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'), logging.StreamHandler()]
    )
    try:
        system_os = platform.system()
        if system_os == 'Windows':
            font_name = font_manager.FontProperties(fname="c:/Windows/Fonts/malgun.ttf").get_name()
            plt.rc('font', family=font_name)
        elif system_os == 'Darwin':
            plt.rc('font', family='AppleGothic')
        plt.rc('axes', unicode_minus=False)
    except Exception:
        logging.warning("한글 폰트 설정을 찾지 못했습니다.")

# --- 1단계: 데이터 전처리 및 요약 ---
def preprocess_and_summarize_data(
    file_path: str, column_map: Dict[str, str], status_indicators: Dict[str, Union[str, int]], **kwargs
) -> Tuple[Dict[str, Dict[str, list]], pd.DataFrame]:
    df = pd.read_excel(file_path) if file_path.endswith('.xlsx') else pd.read_csv(file_path)
    df_renamed = df.rename(columns={v: k for k, v in column_map.items()})
    failure_indicator = str(status_indicators['failure'])
    df_renamed['status_bool'] = df_renamed['status'].astype(str).apply(lambda x: x == failure_indicator)
    
    summary_list, grouped_data = [], {}
    for group, data in df_renamed.groupby('stress'):
        failures = data[data['status_bool']]['time'].tolist()
        right_censored = data[~data['status_bool']]['time'].tolist()
        grouped_data[group] = {'failures': failures, 'right_censored': right_censored}
        summary_list.append({'Group': group, 'Total Samples': len(data), 'Failures': len(failures), 'Censored': len(right_censored)})
    
    summary_df = pd.DataFrame(summary_list)
    print("--- 데이터 요약 ---\
" + summary_df.to_string(index=False))
    return grouped_data, summary_df

# --- 2단계: 최적 수명분포 탐색 ---
def find_best_distribution(
    grouped_data: Dict[str, Dict[str, list]], distributions_to_fit: List[str]
) -> Tuple[Dict[str, Any], pd.DataFrame]:
    analysis_results, bic_scores = {}, []
    fig, ax = plt.subplots(figsize=(10, 7))

    for group_name, data in grouped_data.items():
        analysis_results[group_name] = {}
        for dist_friendly in distributions_to_fit:
            dist_official = FRIENDLY_DIST_MAP.get(dist_friendly.lower().strip())
            if dist_official and dist_official in DISTRIBUTION_MAP:
                fitter = DISTRIBUTION_MAP[dist_official](**data)
                analysis_results[group_name][dist_official] = fitter
                bic_scores.append({'Group': group_name, 'Distribution': dist_official, 'BIC': fitter.BIC})
                # The CDF function plots on the currently active axes, so we don't pass ax directly.
                fitter.distribution.CDF(label=f'{group_name} - {dist_official}')
            else:
                logging.warning(f"Distribution '{dist_friendly}' not found.")
    
    ax.set_title('전체 그룹 수명분포 확률도'); ax.set_xlabel('Time'); ax.set_ylabel('Probability of Failure')
    ax.legend(); ax.grid(True)
    fig.savefig(os.path.join(RESULTS_DIR, "probability_plot_all_groups.png")); plt.close(fig)

    if not bic_scores: return analysis_results, pd.DataFrame()
    bic_df = pd.DataFrame(bic_scores)
    print("\n--- 분포별 BIC (작을수록 좋음) ---\
" + bic_df.to_string(index=False))
    
    try:
        fig, ax = plt.subplots(figsize=(10, 6))
        bic_df.pivot(index='Group', columns='Distribution', values='BIC').plot(kind='bar', ax=ax)
        ax.set_title('그룹별 분포 적합도 (BIC)'); ax.set_ylabel('BIC Score'); ax.tick_params(axis='x', rotation=0)
        fig.savefig(os.path.join(RESULTS_DIR, "BIC_comparison.png")); plt.close(fig)
    except Exception as e:
        logging.warning(f"Could not create BIC pivot plot: {e}")
    return analysis_results, bic_df

# --- 3단계: 단일 분포 상세 분석 ---
def analyze_single_distribution(
    grouped_data: Dict, group_name: str, distribution_name: str,
    b_lives: List = None, failure_prob_times: List = None
) -> object: # Return type is now the fitter object
    found_key = group_name if group_name in grouped_data else int(group_name) if str(group_name).isdigit() and int(group_name) in grouped_data else None
    if found_key is None:
        raise ValueError(f"그룹 '{group_name}'을 찾을 수 없습니다. 사용 가능: {list(grouped_data.keys())}")

    dist_official = FRIENDLY_DIST_MAP.get(distribution_name.lower().strip())
    if not dist_official:
        raise ValueError(f"분포 '{distribution_name}'을 지원하지 않습니다.")

    plt.close('all')
    fitter = DISTRIBUTION_MAP[dist_official](**grouped_data[found_key], show_plot=True, print_results=False)

    ax = getattr(fitter, "probability_plot", plt.gca())
    ax.set_title(f'{found_key} - {dist_official} Probability Plot')
    ax.grid(True)
    fig = ax.get_figure()
    fig.set_size_inches(10, 7)
    fig.savefig(os.path.join(RESULTS_DIR, f"probability_plot_{found_key}_{dist_official}.png"))
    plt.close(fig)

    # --- DYNAMIC PARAMETER AND B-LIFE HANDLING ---
    results = {}
    params, values = [], []

    # 분포 종류에 따라 올바른 모수를 동적으로 가져옵니다.
    if dist_official == "Weibull_2P":
        params.extend(['Alpha', 'Beta'])
        values.extend([fitter.alpha, fitter.beta])
    elif dist_official in ["Lognormal_2P", "Normal_2P"]:
        params.extend(['Mu', 'Sigma'])
        values.extend([fitter.mu, fitter.sigma])
    elif dist_official == "Exponential_1P":
        params.append('Lambda')
        values.append(fitter.Lambda)
    
    results['Parameter'] = params
    results['Value'] = values

    if b_lives:
        # b_life 대신 quantile 메서드를 사용하고, B-수명(B10)을 확률(0.1)로 변환합니다.
        b_life_values = [fitter.distribution.quantile(b/100) for b in b_lives]
        results['B-Life'] = [f'B{b}' for b in b_lives]
        results['B-Life Value'] = b_life_values
        
    if failure_prob_times:
        probs = [fitter.distribution.CDF(t, show_plot=False) for t in failure_prob_times]
        results['Time'] = failure_prob_times
        results['Failure Probability'] = probs

    results_df = pd.DataFrame({k: pd.Series(v) for k, v in results.items()})
    print(f"\n--- {found_key} 그룹 {dist_official} 분석 결과 ---\
" + results_df.to_string(index=False))
    return fitter # Return the fitter object itself



# --- 4단계: 모수 동일성 검토 ---
def check_parameter_homogeneity(
    analysis_results: Dict, parameter_to_check: str
) -> pd.DataFrame:

    param_values = []
    for group, dists in analysis_results.items():
        first_dist_name = next(iter(dists))
        fitter = dists[first_dist_name]
        
        # --- More robustly check for parameter and its confidence interval ---
        if hasattr(fitter, parameter_to_check):
            val = getattr(fitter, parameter_to_check, None)
            lower = getattr(fitter, f"{parameter_to_check}_lower", None)
            upper = getattr(fitter, f"{parameter_to_check}_upper", None)
            param_values.append({'Group': group, 'Parameter': parameter_to_check, 'Value': val, 'Lower CI': lower, 'Upper CI': upper})
    
    if not param_values: raise ValueError(f"모수 '{parameter_to_check}' 또는 해당 신뢰구간을 찾을 수 없습니다.")
    param_df = pd.DataFrame(param_values)
    print(f"\n--- 그룹별 {parameter_to_check} 모수 비교 ---\
" + param_df.to_string(index=False))

    fig, ax = plt.subplots(figsize=(10, 6))
    for _, row in param_df.iterrows():
        ax.errorbar(x=[row['Group']], y=[row['Value']], yerr=[[row['Value'] - row['Lower CI']], [row['Upper CI'] - row['Value']]], fmt='o', capsize=5, label=row['Group'])
    ax.set_title(f'{parameter_to_check} 모수 동일성 검토 (95% 신뢰구간)'); ax.set_ylabel(f'{parameter_to_check} 값')
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    fig.savefig(os.path.join(RESULTS_DIR, f"contour_plot_{parameter_to_check}.png")); plt.close(fig)
    
    return param_df
