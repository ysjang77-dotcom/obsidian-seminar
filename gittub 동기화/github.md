나의 github 웹 주소는
github.com/yjang-git

## 트리거 문구
- "이제 시작할거야" → pull 동기화 자동 실행
- "이제 종료할거야" → push 동기화 자동 실행

- myvault, obsidian-seminar, honeypot, github 폴더로 구성되어 있어.
- D:\AI\ 폴더 하부에 동일한 폴더를 가지고 있어.

## 작업 시작 전 동기화 (pull)

1. `git fetch origin` 으로 원격 변경 사항 확인
2. `git status` 로 로컬 변경 사항 확인
3. 새 파일, 변경된 파일, 삭제된 파일만 확인 후 `git pull origin main` 으로 반영
4. 충돌이 있으면 로컬 변경 내용을 보존하면서 병합

## 작업 종료 전 동기화 (push)

1. `git status` 로 변경된 파일/폴더 확인
2. 새 파일, 수정된 파일, 삭제된 파일만 선택적으로 스테이징
3. 변경 내용을 간결하게 요약한 커밋 메시지 작성
4. `git push origin main` 으로 업로드