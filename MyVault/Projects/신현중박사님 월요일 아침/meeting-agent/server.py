"""
회의록 자동 작성 Agent - Flask 백엔드
Claude Sonnet을 사용하여 회의 녹취록을 구조화된 회의록으로 변환
"""

import os
import json
from datetime import datetime
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from dotenv import load_dotenv
import anthropic

load_dotenv()

app = Flask(__name__, static_folder=".")

# 회의록 저장 경로: meeting-agent 폴더의 부모 폴더 (프로젝트 폴더)
SAVE_DIR = Path(__file__).parent.parent

SYSTEM_PROMPT = """당신은 20년 이상의 경력을 가진 전문 서무원입니다.
연구실 회의의 녹취 내용을 바탕으로 공식적인 회의록을 작성합니다.

작성 원칙:
- 중립적이고 객관적인 문체를 사용합니다
- 기술 용어, 수치, 재료명 등은 발화된 그대로 정확히 기재합니다
- 결정된 사항과 아직 검토 중인 사항을 명확히 구분합니다
- 액션 아이템은 담당자와 기한이 명시된 경우 반드시 테이블에 기재합니다
- 마크다운 형식으로만 응답하며, 추가 설명 없이 회의록 본문만 작성합니다"""

USER_PROMPT_TEMPLATE = """아래의 회의 녹취 내용을 분석하여 공식 회의록을 작성해주세요.

회의 날짜: {date}

녹취 내용:
---
{transcript}
---

다음 마크다운 형식으로 작성해주세요:

# 회의록 - {date}

## 회의 정보
- **일시**: {date}
- **장소**: (언급된 경우 기재, 없으면 비워두기)
- **참석자**: (언급된 참석자 기재, 불분명하면 "미기재")
- **주제**: (핵심 주제 1~2줄 요약)

---

## 주요 논의 사항

(각 논의 항목을 ### 1. 제목 형식의 섹션으로 구분하여 상세히 기재)

---

## 결정 사항
- [ ] (결정된 사항 체크박스 형식으로 기재)

---

## 액션 아이템

| 담당자 | 업무 | 마감일 |
|--------|------|--------|
| (담당자) | (업무 내용) | (마감일 또는 "-") |

---

## 다음 회의
- **예정일**: (언급된 경우 기재)
- **안건**: (언급된 경우 기재)

---

#meeting #회의록"""


@app.route("/")
def index():
    return send_from_directory(".", "index.html")


@app.route("/process", methods=["POST"])
def process_transcript():
    data = request.json
    transcript = data.get("transcript", "").strip()
    meeting_date = data.get("date", datetime.now().strftime("%Y%m%d"))

    if not transcript:
        return jsonify({"error": "녹취 내용이 없습니다. 회의 내용을 입력해주세요."}), 400

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return jsonify({"error": "ANTHROPIC_API_KEY가 설정되지 않았습니다. .env 파일을 확인해주세요."}), 500

    client = anthropic.Anthropic(api_key=api_key)

    user_message = USER_PROMPT_TEMPLATE.format(
        date=meeting_date,
        transcript=transcript,
    )

    try:
        message = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )
    except anthropic.AuthenticationError:
        return jsonify({"error": "API 키가 유효하지 않습니다. .env 파일의 ANTHROPIC_API_KEY를 확인해주세요."}), 401
    except anthropic.BadRequestError as e:
        msg = str(e)
        if "credit balance is too low" in msg:
            return jsonify({"error": "API 크레딧이 부족합니다. console.anthropic.com → Plans & Billing에서 충전해주세요."}), 402
        return jsonify({"error": f"API 요청 오류: {msg}"}), 400
    except anthropic.APIError as e:
        return jsonify({"error": f"Anthropic API 오류: {str(e)}"}), 500

    meeting_notes = message.content[0].text

    # 파일 저장
    filename = f"{meeting_date}.md"
    filepath = SAVE_DIR / filename
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(meeting_notes)

    return jsonify({
        "content": meeting_notes,
        "filename": filename,
        "filepath": str(filepath),
    })


@app.route("/health")
def health():
    return jsonify({"status": "ok", "save_dir": str(SAVE_DIR)})


if __name__ == "__main__":
    print("=" * 50)
    print("회의록 자동 작성 Agent 시작")
    print(f"회의록 저장 경로: {SAVE_DIR}")
    print("브라우저에서 http://localhost:5000 접속")
    print("Chrome 또는 Edge 사용 권장")
    print("=" * 50)
    app.run(debug=False, port=5000)
