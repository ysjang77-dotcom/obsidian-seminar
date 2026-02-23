from IPython.display import display, Markdown, HTML

# --- 보고서 출력 시작 ---
display(HTML("<h1>가속수명시험(ALT) 분석 결과 보고서</h1>"))
display(Markdown(f"**분석 일시:** {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}"))
display(Markdown(f"**분석 대상 파일:** `{FILE_PATH}`"))
    
# --- 분석 파이프라인 실행 ---

# 1단계 실행: 데이터 로딩 및 전처리
display(Markdown("# 가속수명시험(ALT) 분석 결과 보고서"))
failures, right_censored, failure_stresses, right_censored_stresses, df_original = (None,) * 5
try:
    failures, right_censored, failure_stresses, right_censored_stresses, df_original = load_and_preprocess_data(
        filepath=FILE_PATH,
        time_col=COLUMN_MAP['time'],
        stress_col=COLUMN_MAP['stress'],
        censor_col=COLUMN_MAP['censor'],
        failure_code=FAILURE_CODE,
        censor_code=CENSOR_CODE
    )
    if failures is not None:
        display(Markdown("--- \n ## 1단계: 데이터 로딩 및 전처리 결과\n- 데이터 로딩 및 `reliability` 패키지 형식으로의 변환이 성공적으로 완료되었습니다.\n- 상세 내용은 위의 미리보기 및 요약 통계 테이블을 참조하십시오."))
except Exception as e:
    logging.error(f"1단계 실행 중 오류 발생: {e}")
    display(Markdown(f"<font color='red'>**1단계 오류:** 데이터 로딩 및 전처리에 실패했습니다. 파일 경로와 컬럼 이름을 확인해주세요. (오류: {e})</font>"))

# 2단계 실행: 수명 분포 분석
best_dist, dist_fit_results = (None, None)
if failures is not None and len(failures) > 0:
    try:
        # --- ★★★ 코드 수정 부분 ★★★ ---
        # 누락되었던 right_censored_stresses 인자를 추가합니다.
        best_dist, dist_fit_results = find_best_life_distribution(
            failures=failures, 
            right_censored=right_censored, 
            failure_stresses=failure_stresses, 
            right_censored_stresses=right_censored_stresses
        )
        # --- ★★★ 코드 수정 완료 ★★★ ---
        display(Markdown(f"--- \n ## 2단계: 수명 분포 분석 결과\n- 각 스트레스 수준별 데이터에 가장 적합한 분포를 분석한 결과, **{best_dist}** 분포가 전반적으로 가장 적합한 것으로 나타났습니다.\n- 이 분포를 기반으로 다음 단계의 가속성 검정을 진행합니다."))
    except Exception as e:
        logging.error(f"2단계 실행 중 오류 발생: {e}")
        display(Markdown(f"<font color='red'>**2단계 오류:** 수명 분포 분석에 실패했습니다. (오류: {e})</font>"))


# 3단계 실행: 가속성 검정
is_acceleration_valid = False
if best_dist is not None:
    try:
        is_acceleration_valid = perform_acceleration_test(failures, failure_stresses, right_censored, right_censored_stresses, best_dist)
        if is_acceleration_valid:
            display(Markdown(f"--- \n ## 3단계: 가속성 검정 결과\n- 형상모수 변화율이 안정적이며, Likelihood 플롯에서 신뢰구간이 적절히 겹치는 것을 확인했습니다.\n- **가속성이 성립**하는 것으로 판단되며, 가속 수명 모델 수립을 진행할 수 있습니다."))
        else:
            display(Markdown(f"--- \n ## 3단계: 가속성 검정 결과\n- **경고:** 형상모수가 스트레스 수준에 따라 크게 변동하는 것으로 나타났습니다. 이는 스트레스에 따라 고장 메커니즘이 변할 수 있음을 의미하며, 가속 수명 모델의 신뢰도가 낮을 수 있습니다. 결과 해석에 각별한 주의가 필요합니다."))
    except Exception as e:
        logging.error(f"3단계 실행 중 오류 발생: {e}")
        display(Markdown(f"<font color='red'>**3단계 오류:** 가속성 검정에 실패했습니다. (오류: {e})</font>"))


# 4단계 실행: 가속 수명 모델 수립
# --- ★★★ 코드 수정 부분 ★★★ ---
recommended_model_name, fitted_models, alt_results_df = (None, None, None)
if is_acceleration_valid:
    try:
        recommended_model_name, fitted_models, alt_results_df = build_alt_model(
            failures=failures,
            failure_stresses=failure_stresses,
            right_censored=right_censored,
            right_censored_stresses=right_censored_stresses,
            best_dist_name=best_dist,
            use_stress=USE_STRESS
        )
        display(Markdown(f"--- \n ## 4단계: 가속 수명 모델 수립 결과\n- 수명 분포({best_dist})에 대해 적용 가능한 모든 가속 모델을 분석한 결과, BIC 기준 **{recommended_model_name} 모델**이 가장 적합한 것으로 추천되었습니다.\n- 위 플롯과 파라미터 테이블은 추천 모델에 대한 상세 분석 결과입니다."))
    except Exception as e:
        logging.error(f"4단계 실행 중 오류 발생: {e}")
        display(Markdown(f"<font color='red'>**4단계 오류:** 가속 수명 모델 수립에 실패했습니다. (오류: {e})</font>"))



# 5단계 실행: 신뢰성 예측

# 5. 4단계에서 사용할 ALT 모델을 직접 지정할 수 있습니다.
#    'AUTO'로 설정하면 BIC 기준 최적 모델이 자동으로 선택됩니다.
#    수동으로 지정하려면 4단계 결과 테이블에 나온 모델 이름을 입력하세요 (예: 'Weibull_Power').
# CHOSEN_ALT_MODEL = 'AUTO' 
CHOSEN_ALT_MODEL ='Lognormal_Exponential'

if fitted_models is not None and USE_STRESS is not None:
    
    # 사용자가 선택한 모델 또는 BIC 추천 모델을 최종 모델로 확정
    final_model_fit = None
    final_model_name = ''

    if CHOSEN_ALT_MODEL.upper() == 'AUTO':
        final_model_name = recommended_model_name
        final_model_fit = fitted_models[final_model_name]
        logging.info(f"자동 선택에 따라 BIC 기준 최적 모델인 '{final_model_name}'을 사용하여 5단계 예측을 진행합니다.")
    elif CHOSEN_ALT_MODEL in fitted_models:
        final_model_name = CHOSEN_ALT_MODEL
        final_model_fit = fitted_models[final_model_name]
        logging.info(f"사용자 선택에 따라 '{final_model_name}' 모델을 사용하여 5단계 예측을 진행합니다.")
    else:
        logging.warning(f"사용자가 선택한 모델 '{CHOSEN_ALT_MODEL}'을 찾을 수 없습니다. BIC 기준 최적 모델인 '{recommended_model_name}'으로 예측을 진행합니다.")
        final_model_name = recommended_model_name
        final_model_fit = fitted_models[final_model_name]

    if final_model_fit:
        try:
            prediction_df, final_dist = predict_reliability_at_use_condition(
                use_stress=USE_STRESS,
                best_alt_model_fit=final_model_fit,
                failures=failures,
                failure_stresses=failure_stresses,
                right_censored=right_censored,
                right_censored_stresses=right_censored_stresses,
                b_lives_to_predict=B_LIVES_TO_PREDICT,
                times_to_predict=TIMES_TO_PREDICT
            )
            display(Markdown(f"--- \n ## 5단계: 사용 조건 신뢰성 예측 결과\n- 최종 선택된 **{final_model_name}** 모델을 사용하여 사용 조건(스트레스={USE_STRESS})에서의 신뢰성을 예측했습니다.\n- 상세 예측치는 위 테이블을 참조하십시오."))
        except Exception as e:
            logging.error(f"5단계 실행 중 오류 발생: {e}")
            display(Markdown(f"<font color='red'>**5단계 오류:** 신뢰성 예측에 실패했습니다. (오류: {e})</font>"))
# --- ★★★ 코드 수정 완료 ★★★ ---

logging.info("가속수명시험(ALT) 분석을 완료했습니다.")
display(Markdown("--- \n ## 분석 완료 \n 모든 분석 과정이 완료되었습니다. 로그 파일과 `results` 폴더에 저장된 산출물을 확인하십시오."))
