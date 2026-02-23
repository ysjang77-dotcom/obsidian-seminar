# -*- coding: utf-8 -*-
import os
import logging
import argparse
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup
import html2text

# --- 설정 (Configuration) ---
# 이 부분의 값을 수정하여 스크립트의 동작을 변경할 수 있습니다.

# 결과물이 저장될 기본 폴더 이름
OUTPUT_DIR = "output"
# 크롤링된 원본 HTML 파일이 저장될 폴더 이름
CRAWLED_HTML_DIR = os.path.join(OUTPUT_DIR, "crawled_html")
# 최종 통합 마크다운 문서 파일명
MARKDOWN_FILE = os.path.join(OUTPUT_DIR, "integrated_documentation.md")
# 로그 파일명
LOG_FILE = os.path.join(OUTPUT_DIR, "crawl_log.log")

# HTML에서 실제 내용이 담긴 컨테이너를 식별하기 위한 CSS 선택자
# 예: <main role="main"> 안의 내용만 추출하고 싶을 때 -> "main[role='main']"
# 만약 적절한 선택자를 찾지 못하면, body 전체를 사용합니다.
CONTENT_SELECTOR = "div[role='main']"

# HTTP 요청 시 사용할 헤더
REQUEST_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}


def setup_project_structure():
    """
    결과물 저장을 위한 폴더 구조를 생성합니다.
    'output' 폴더와 'output/crawled_html' 폴더를 확인하고 없으면 생성합니다.
    """
    if not os.path.exists(OUTPUT_DIR):
        os.makedirs(OUTPUT_DIR)
        logging.info(f"'{OUTPUT_DIR}' 폴더를 생성했습니다.")
    if not os.path.exists(CRAWLED_HTML_DIR):
        os.makedirs(CRAWLED_HTML_DIR)
        logging.info(f"'{CRAWLED_HTML_DIR}' 폴더를 생성했습니다.")


def setup_logging():
    """
    로깅 설정을 초기화합니다.
    로그는 파일과 콘솔에 모두 출력됩니다.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE, mode='w', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )


def extract_main_links(base_url: str) -> list[str]:
    """
    주어진 기본 URL 페이지에서 크롤링할 하위 페이지 링크 목록을 추출합니다.

    Args:
        base_url (str): 크롤링을 시작할 최상위 페이지 URL

    Returns:
        list[str]: 크롤링 대상이 되는 전체 URL 주소 목록
    """
    logging.info(f"메인 페이지에서 링크 추출을 시작합니다: {base_url}")
    try:
        response = requests.get(base_url, headers=REQUEST_HEADERS, timeout=10)
        response.raise_for_status()  # HTTP 에러 발생 시 예외 처리
    except requests.exceptions.RequestException as e:
        logging.error(f"메인 페이지를 가져오는 중 오류 발생: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    links = set()  # 중복된 링크를 방지하기 위해 set 사용

    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        # 상대 경로이고, 페이지 내 앵커(#)가 아니며, .html로 끝나는 링크만 필터링
        if not href.startswith(('http://', 'https://', '#')) and href.endswith('.html'):
            # urljoin을 사용하여 상대 경로를 절대 경로로 변환
            full_url = urljoin(base_url, href)
            links.add(full_url)

    logging.info(f"총 {len(links)}개의 유효한 하위 링크를 찾았습니다.")
    return sorted(list(links)) # 정렬된 리스트로 반환


def process_and_save_subpage(page_url: str) -> str:
    """
    하위 페이지를 크롤링하고, 내용을 정제하여 저장한 뒤 마크다운으로 변환합니다.

    Args:
        page_url (str): 크롤링할 하위 페이지의 URL

    Returns:
        str: 마크다운으로 변환된 페이지 콘텐츠. 실패 시 빈 문자열 반환.
    """
    logging.info(f"하위 페이지 처리 중: {page_url}")
    try:
        response = requests.get(page_url, headers=REQUEST_HEADERS, timeout=10)
        response.raise_for_status()
        html_content = response.content
    except requests.exceptions.RequestException as e:
        logging.error(f"페이지를 가져오는 중 오류 발생 ({page_url}): {e}")
        return ""

    soup = BeautifulSoup(html_content, 'html.parser')

    # 1. 핵심 콘텐츠 추출
    content_area = soup.select_one(CONTENT_SELECTOR)
    if not content_area:
        logging.warning(f"'{CONTENT_SELECTOR}' 선택자에 해당하는 콘텐츠 영역을 찾지 못했습니다. body 전체를 사용합니다.")
        content_area = soup.body

    if not content_area:
        logging.error(f"페이지에서 body 태그를 찾을 수 없습니다: {page_url}")
        return ""
        
    # 추출된 핵심 콘텐츠를 문자열로 변환
    refined_html = str(content_area)

    # 2. 정제된 HTML 파일로 저장
    try:
        # URL에서 파일 이름을 추출
        parsed_url = urlparse(page_url)
        filename = os.path.basename(parsed_url.path)
        if not filename:
            filename = f"{parsed_url.netloc.replace('.', '_')}.html"
        
        filepath = os.path.join(CRAWLED_HTML_DIR, filename)
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(refined_html)
        logging.info(f"정제된 HTML을 저장했습니다: {filepath}")
    except IOError as e:
        logging.error(f"HTML 파일 저장 중 오류 발생 ({filepath}): {e}")

    # 3. HTML을 마크다운으로 변환
    h = html2text.HTML2Text()
    h.ignore_links = False # 링크 유지
    markdown_content = h.handle(refined_html)
    
    return markdown_content


def main():
    """
    메인 실행 함수. 전체 크롤링 및 변환 프로세스를 조율합니다.
    """
    # 1. 로깅 및 프로젝트 구조 설정
    setup_logging()
    setup_project_structure()

    # 2. 커맨드 라인 인자 파싱
    parser = argparse.ArgumentParser(
        description="웹페이지와 그 하위 페이지들을 크롤링하여 하나의 마크다운 파일로 통합합니다."
    )
    parser.add_argument(
        "start_url",
        type=str,
        help="크롤링을 시작할 최상위 페이지의 URL"
    )
    args = parser.parse_args()
    start_url = args.start_url

    logging.info(f"크롤링 프로세스를 시작합니다. 대상 URL: {start_url}")

    # 3. 메인 페이지에서 링크 추출
    subpage_urls = extract_main_links(start_url)
    if not subpage_urls:
        logging.warning("크롤링할 하위 페이지가 없습니다. 프로세스를 종료합니다.")
        return

    # 4. 각 하위 페이지 처리 및 마크다운 통합
    all_markdowns = []
    for url in subpage_urls:
        markdown = process_and_save_subpage(url)
        if markdown:
            # 페이지 제목을 마크다운에 추가
            page_title = url.split('/')[-1]
            all_markdowns.append(f"# {page_title}\n\nSource: <{url}>\n\n{markdown}")

    # 5. 통합된 마크다운 파일 저장
    try:
        with open(MARKDOWN_FILE, 'w', encoding='utf-8') as f:
            # 각 문서 사이에 구분선 추가
            f.write("\n\n---\n\n".join(all_markdowns))
        logging.info(f"모든 콘텐츠를 성공적으로 통합하여 '{MARKDOWN_FILE}'에 저장했습니다.")
    except IOError as e:
        logging.error(f"최종 마크다운 파일 저장 중 오류 발생: {e}")

    logging.info("모든 프로세스가 완료되었습니다.")


if __name__ == "__main__":
    main()
