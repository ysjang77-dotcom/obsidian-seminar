import streamlit as st
import requests

# 백엔드 API 주소
BACKEND_URL = "http://127.0.0.1:8000/analyze/"

st.set_page_config(layout="wide")

st.title("브레이크 패드 수명 분석기")

st.markdown("""
이 앱은 내구시험 데이터와 필드 데이터를 통계적으로 분석하여 **가속계수**를 산출합니다.  
엑셀(xlsx) 또는 CSV 파일을 업로드하고 분석을 시작하세요.
""")

# --- 1. 사용자 입력 ---
with st.sidebar:
    st.header("1. 파일 업로드")
    uploaded_file = st.file_uploader("분석할 데이터 파일을 선택하세요.", type=['xlsx', 'csv'])

    st.header("2. 분석 설정")
    lifetime_col = st.text_input("수명 데이터 컬럼명", "distance(km)")
    type_col = st.text_input("데이터 구분 컬럼명", "type")
    
    st.header("3. 분석 실행")
    run_button = st.button("분석 실행")

# --- 2. API 요청 및 결과 표시 ---
if run_button:
    if uploaded_file is not None:
        with st.spinner("분석 중... 잠시만 기다려 주세요."):
            try:
                files = {'file': (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)}
                data = {'lifetime_column': lifetime_col, 'type_column': type_col}
                response = requests.post(BACKEND_URL, files=files, data=data)

                if response.status_code == 200:
                    st.success("분석이 성공적으로 완료되었습니다!")
                    results = response.json()

                    st.header("종합 분석 보고서")
                    report_url = results.get("report_url")
                    if report_url:
                        report_response = requests.get(report_url)
                        if report_response.status_code == 200:
                            report_text = report_response.text
                            # 보고서의 상대 이미지 경로를 절대 URL로 변경
                            for plot_url in results.get("plot_urls", []):
                                filename = plot_url.split("/")[-1]
                                report_text = report_text.replace(f"({filename})", f"({plot_url})")
                            st.markdown(report_text, unsafe_allow_html=True)
                        else:
                            st.error(f"보고서 내용을 가져올 수 없습니다: {report_url}")

                    st.header("분석 결과 플롯")
                    plot_urls = results.get("plot_urls", [])
                    if plot_urls:
                        for plot_url in plot_urls:
                            st.image(plot_url)
                    
                    with st.expander("백엔드 원본 응답 보기 (JSON)"):
                        st.json(results)

                else:
                    st.error(f"분석에 실패했습니다. (상태 코드: {response.status_code})")
                    st.json(response.json())

            except requests.exceptions.RequestException as e:
                st.error(f"백엔드 서버에 연결할 수 없습니다: {e}")
            except Exception as e:
                st.error(f"예상치 못한 오류가 발생했습니다: {e}")
    else:
        st.warning("분석할 파일을 먼저 업로드해주세요.")