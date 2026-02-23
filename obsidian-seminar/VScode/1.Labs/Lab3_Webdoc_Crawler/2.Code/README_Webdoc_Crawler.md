# 웹사이트 문서 통합 크롤러

이 Python 스크립트는 지정된 웹페이지에 링크된 모든 하위 `.html` 문서들을 자동으로 크롤링하고, 각 문서의 핵심 내용을 추출하여 하나의 통합된 마크다운(`.md`) 파일로 만들어주는 도구입니다.

## 기능

- 특정 URL에서 하위 문서 링크 자동 추출
    
- 각 문서에서 불필요한 부분(네비게이션, 푸터 등)을 제외한 핵심 콘텐츠만 정제
    
- 정제된 HTML과 최종 통합 마크다운 문서를 `output` 폴더에 저장
    
- 모든 실행 과정을 `output/crawl_log.log` 파일에 기록
    

## 설치 방법

1. 이 프로젝트를 로컬 컴퓨터에 다운로드합니다.
    
2. 터미널 또는 명령 프롬프트를 열고, 프로젝트 폴더로 이동합니다.
    
3. 아래 명령어를 실행하여 필요한 라이브러리를 설치합니다.
    
    ```
    pip install -r requirements.txt
    ```
    

## 사용 방법

터미널에서 아래와 같은 형식으로 스크립트를 실행합니다. `<URL>` 부분에 크롤링을 시작하고 싶은 웹페이지의 전체 주소를 입력하세요.

```
python main.py <URL>
```

### 실행 예시

```
python main.py "https://reliability.readthedocs.io/en/latest/API%20reference.html"
```

실행이 완료되면 `output` 폴더 안에 결과물들이 생성됩니다.

- `integrated_documentation.md`: 모든 문서가 통합된 최종 마크다운 파일
    
- `crawled_html/`: 크롤링된 개별 페이지의 원본 HTML 파일들
    
- `crawl_log.log`: 스크립트 실행 기록
    

## 설정 변경

`main.py` 파일 상단의 **설정(Configuration)** 영역에서 CSS 선택자(`CONTENT_SELECTOR`)나 결과물 폴더명 등을 필요에 맞게 수정할 수 있습니다.