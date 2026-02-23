# Claude 자동 실행 규칙

## GitHub 동기화 트리거

다음 문구를 말하면 자동으로 해당 작업을 수행한다.

### "이제 시작할거야" → 작업 시작 전 동기화 (pull)

1. GitHub 전체 레포 목록 확인 (`gh repo list yjang-git`)
2. `git fetch origin` 으로 원격 변경 사항 확인
3. `git status` 로 로컬 변경 사항 확인
4. 로컬에 없는 GitHub 파일/폴더가 있으면 누락 여부 확인 후 `git pull origin main` 으로 반영
5. 충돌이 있으면 **GitHub를 기준**으로 병합 (GitHub가 항상 원본)
6. 동기화 결과를 간략히 보고

### "이제 종료할거야" → 작업 종료 전 동기화 (push)

1. GitHub 전체 레포 목록 확인 (`gh repo list yjang-git`)
2. `git status` 로 변경된 파일/폴더 확인
3. GitHub와 로컬의 폴더/파일명이 다르면 **GitHub 이름 기준**으로 로컬을 수정
4. 변경된 파일/폴더를 스테이징 (`git add -A`)
5. 변경 내용을 간결하게 요약한 커밋 메시지 작성 후 커밋
6. `git push origin main` 으로 업로드
7. 동기화 결과를 간략히 보고

## 기본 정보

- GitHub: github.com/yjang-git
- 로컬 경로: D:\AI\
- 브랜치: main
