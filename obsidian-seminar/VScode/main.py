import os
import sys
import google.generativeai as genai
from dotenv import load_dotenv

# .env 파일에서 환경 변수 로드
load_dotenv()

# API 키 설정
api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

# 사용할 Gemini 모델 선택
model = genai.GenerativeModel('gemini-pro')

# 명령줄 인자에서 프롬프트 가져오기
if len(sys.argv) > 1:
    prompt = " ".join(sys.argv[1:])
else:
    print("사용법: python main.py <프롬프트>")
    sys.exit(1)

# 모델에 프롬프트 전송
response = model.generate_content(prompt)

# 응답 출력
print(response.text)