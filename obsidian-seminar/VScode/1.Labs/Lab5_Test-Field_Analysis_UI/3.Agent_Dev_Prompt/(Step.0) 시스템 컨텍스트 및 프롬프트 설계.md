
# 요구사항
- [목적] 내구-필드 수명분석 python 코드를 활용하여 Gemini CLI 에서 frontend와 backend로 구성된 AI-agent를 구현하기 위한 시스템 컨텍스트(gemini.md)와 작업 프롬프트를 작성
- [내구-필드 수명분석 내용]
	- 내구시험과 필드시험 수명데이터를 분석하여 최적분포를 결정 → 분포의 정합성(공통형상모수 또는 공통척도모수)을 검정 → 공통형상모수(또는 공통척도모수)를 가정하여 추정한 수명분포에 대해서 두 데이터간 척도모수(또는 위치모수)의 비율을 계산하여 가속계수 산출
- [AI-agent 구현내용 및 범위]
	- 분석코드를 활용하여 backend를 개발하고, 사용자가 데이터 업로드, 분석 환경설정, 분석실행 및 결과리포트 조회를 할 수 있는 frontend (GUI)를 개발
	- frontend는 React와 streamlit을 사용하는 경우에 대해서 각각 구현
- [요구사항]
	- 아래 제시된 프롬프팅 핵심기법, Agent 개발 메타프롬프트 템플릿을 활용할 것
	- 첨부한 python 분석코드(lifedata_v6.py)를 활용할 것. 분석절차, 코드에 구현된 함수의 내용, 산출물 형식을 변경하지 말고 유지할 것
	- 생성형 AI(gemini cli)가 코드를 개발하기 위한 '시스템 컨텍스트'와 '개발 프롬프트'를 작성할 것
	- 개발 프롬프트는 개발 단계별로 사용자가 순차적으로 실행할 수 있도록 구분하여 제시할 것
	- 디버깅 및 실행과정 추적이 쉽도록 백엔드의 모든 실행과정을 로깅하도록 할 것
	- Gemini CLI 에서 AI-agent를 개발하는 과업에 최적화할 것
	- python 및 ai-agent 개발에 익숙하지 않은 초보자도 이해할 수 있게 가능한 단순하고 직관적인 구조로 개발할 수 있도록 지시 할 것.
	- 한글로 작성할 것


# (참고자료) 프롬프팅 핵심기법

## **1) 역할-과업-형식 (PTF: Persona, Task, Format)**

PTF는 AI에게 지시를 내리는 가장 기본적이면서도 강력한 프레임워크입니다. AI에게 명확한 역할을 부여하면, 해당 분야의 지식과 스타일에 맞는 코드를 생성할 확률이 높아집니다.

- **P (Persona, 역할 부여):** AI의 전문 분야와 정체성을 구체적으로 지정합니다. 단순히 전문가 역할을 부여하는 것을 넘어, 사용하는 기술 스택과 전문 분야를 명시하면 더 정제된 결과물을 얻을 수 있습니다.
    
    - **예시:** "너는 **신뢰성 공학(Reliability Engineering) 전문가**이며, Python의 `pandas`, `numpy`, `matplotlib` 라이브러리를 활용한 **수명 데이터 분석(Lifetime Data Analysis)에 능숙**해."
        
- **T (Task, 과업 지시):** 수행할 작업을 구체적이고 명확하게 지시합니다. 두루뭉술한 지시 대신, 분석할 데이터의 정보(파일명, 컬럼 구조), 사용할 분석 기법 등 상세 정보를 포함해야 AI가 작업을 정확히 이해할 수 있습니다.
    
    - **예시:** "첨부된 `alt_data.csv` 파일(컬럼: `stress_level`, `time_to_failure`)을 읽어, **스트레스 수준별 와이블 분포(Weibull distribution)를 분석**하고 각 파라미터를 추정해줘."
        
- **F (Format, 형식 지정):** 결과물을 어떤 형태로 받을지 명시합니다. 코드뿐만 아니라, 보고서 초안, 함수 설명 문서(docstring), 특정 폴더 구조에 맞는 파일 목록 등 원하는 모든 출력 형식을 지정할 수 있습니다.
    
    - **예시:** "결과는 **Jupyter Notebook 형식**으로 셀을 나누어줘. 첫 번째 셀은 데이터 로딩, 두 번째 셀은 분석 코드, 세 번째 셀은 시각화 코드를 포함해줘."
        

### **2) 제로샷, 퓨샷, CoT 기법의 활용**

상황에 따라 다른 프롬프팅 기법을 선택하여 AI의 응답을 유도할 수 있습니다.

- **제로샷 프롬프팅 (Zero-Shot Prompting):** 별도의 예시 없이 바로 작업을 지시하는 방식으로, 작업이 간단하고 명확할 때 빠르게 사용하기 좋습니다.
    
    - **예시:** "파이썬으로 현재 시간을 'YYYY-MM-DD HH:MM:SS' 형식으로 출력하는 코드를 만들어줘."
        
- **퓨샷 프롬프팅 (Few-Shot Prompting):** 1~3개의 간단한 예시(입력과 출력 쌍)를 먼저 보여주고 작업을 지시합니다. AI가 내 의도를 잘 이해하지 못하거나, 특정 출력 형식을 따라 하게 만들고 싶을 때 효과적입니다. 제공하는 예시의 품질이 결과에 큰 영향을 미칩니다.
    
    - **예시:** "아래 예시처럼, 주어진 고장 코드(Failure Code)에서 시스템명만 추출하는 파이썬 함수를 만들어줘.
        
        - `F-SYS1-001` -> `SYS1`
            
        - `F-SYS2-005` -> `SYS2`"
            
- **사고의 연쇄 (CoT: Chain-of-Thought) 프롬프팅:** 복잡한 문제의 경우, AI에게 "단계별로 생각해서(Step-by-step)" 해결 과정을 설명하며 코드를 작성하도록 유도하는 기법입니다. 여러 단계를 거쳐야 하는 복잡한 분석이나 알고리즘 구현에 필수적이며, AI가 스스로 논리를 점검하게 만들어 실수를 줄일 수 있습니다.
    
    - **예시:** "총 가동 시간과 고장 횟수 데이터가 주어졌을 때, **MTBF(평균고장간격)를 계산하는 과정**을 **'단계별로 생각해서(Let's think step by step)'** 논리적으로 설명하고, 이를 수행하는 Python 코드를 작성해줘."
        

### **3) 명확한 맥락 제공 및 제약 조건 설정**

코드의 정확성과 품질을 높이기 위해 명확한 맥락과 구체적인 제약 조건을 설정하는 것이 중요합니다.

- **맥락(Context) 제공:** 분석하려는 데이터의 일부(헤더, 몇 개 행)를 직접 보여주거나, 기존 코드의 특정 부분을 제공하며 "이 코드에서 발생하는 에러를 해결해줘" 또는 "이 함수에 기능을 추가해줘"라고 지시합니다.
    
- **제약 조건(Constraints) 설정:** 사용할 프로그래밍 언어, 라이브러리 버전, 피해야 할 함수, 코드 스타일 등을 명시하여 결과물이 특정 요구사항을 만족하도록 지시합니다.
    
    - **예시:** “파이썬 3.9 버전을 기준으로, **numpy 라이브러리만 사용**해서 두 행렬의 곱을 구하는 코드를 작성해줘.”
        
- **테스트 케이스 먼저 제시하기 (TDD 방식 활용):** AI가 코드를 작성하기 전에, 통과해야 할 테스트 케이스를 먼저 제공하는 전략입니다. 이는 AI가 만들어낼 코드의 정확성과 신뢰도를 크게 향상시킵니다.
    
    - **예시:** "아래 `pytest` 형식의 **단위 테스트를 모두 통과**하는 `calculate_reliability(t, mtbf)` 함수를 작성해줘."
        
- **소프트웨어 공학 원칙 적용하기:** 소프트웨어 개발 방법론(SOLID, SRP,  클린 아키텍처, 테스트 주도 개발)을 적용할 것을 명시적으로 요구하여 모듈화되고 유지보수하기 좋은 코드를 생성하도록 유도할 수 있습니다.
    
    - **예시:** "데이터 처리, 분석, 시각화 기능을 각각 별도의 함수로 만들어줘. 각 함수는 **단일 책임 원칙(Single Responsibility Principle)을 준수**하도록 설계해줘."

# (참고자료) Agent 개발 메타프롬프트 템플릿

ROLE
- You are a senior software + data engineer who practices Clean Architecture, SOLID, and TDD.
- Your job is to design, implement, test, and document a complete solution from analysis to frontend/backend integration ("Vibe coding").

CONTEXT
- Project: {ProjectName}
- Domain/Use-case: {DomainDescription}
- Data sources: {DataSourcesAndSchemas} (include field names, types, units, null policy)
- Target users: {UserTypes} and their workflows
- Tech stack (preferred): {Language}/{Runtime}, {Frameworks}, {DB/Storage}, {Packaging}, {CI/CD}
- Deployment target: {Local/Container/Cloud}, OS: {OS}, GPU: {Y/N}

OBJECTIVES (prioritized)
1) Analysis pipeline (ingest → preprocess → model/algorithm → evaluation → visualization).
2) Report/Artifact generation: {PDF/HTML/Markdown/Notebook} with figures/tables.
3) Backend service: {REST/GraphQL} API exposing core functions.
4) Frontend/GUI: {Web/Desktop} with {Framework}, connecting to the backend.
5) Reproducibility: deterministic runs, seed control, environment lockfile.

NON-FUNCTIONAL REQUIREMENTS
- Modularity & testability, clear boundaries, minimal coupling.
- Reliability & performance budgets: {SLA/SLO/latency/throughput/footprint}.
- Security & privacy: {PII policy, access control, secrets handling}, no hard-coded secrets.
- Observability: structured logs, metrics, error traces.

ARCHITECTURE (Clean Architecture)
- Domain: pure business logic (no I/O, no UI); types, rules, algorithms.
- Application: use-cases, orchestration, validation; depends only on Domain.
- Interface: CLI/GUI/API adapters, serializers, request/response DTOs.
- Infrastructure: DB/repo, filesystem, external services; injected via interfaces.
- Dependency direction: Interface/Infra → Application → Domain (Domain is inner, depends on nothing).

DESIGN PRINCIPLES (SOLID)
- SRP: each module/class/function has one reason to change.
- OCP: extend via new implementations, avoid modifying stable code.
- LSP: subclasses/implementations must be substitutable via interface.
- ISP: small, focused interfaces (no “fat” interfaces).
- DIP: depend on abstractions; inject concrete implementations.

WORKFLOW (Plan-and-Solve + CoT)
- First: Produce a PLAN with milestones and module boundaries (file layout, public APIs, data contracts).
- Then: Implement step-by-step following the plan. Before code, write tests (TDD).
- After each milestone: run self-critique (RCI) → improve → verify tests again.

PROMPTING TECHNIQUES TO APPLY
- Start Zero-shot; add Few-shot mini-examples (I/O pairs) if ambiguity arises.
- Use CoT: explain brief reasoning (bulleted) before emitting final code.
- Use Plan-and-Solve: present plan section, then solution section.
- For alternatives: propose 2–3 options (Tree-of-Thought lite), pick one with rationale.
- If external info/tools are needed: state explicit assumptions or request permission (ReAct-lite).

SPECIFICATIONS (must provide)
- Data contracts: schemas, dtypes, units, missing-value policy, validation rules.
- Public API of each module: function/class signatures, types, side effects.
- Error handling: typed errors, user-facing messages, retry/backoff policy where relevant.
- Configuration: {YAML/ENV} with defaults and overrides; no secrets in code.
- Performance: target complexity and budgets; profiling hooks if needed.

TESTS (TDD)
- Before implementation: write unit tests (pytest/{Language’s test framework}) for each public function.
- Include golden tests for report/plot hashes or structural checks.
- Provide test data fixtures and factories; ensure deterministic seeds.

IMPLEMENTATION RULES
- Code style: {StyleGuide} with linter/formatter config (e.g., ruff/black, eslint/prettier).
- Types: full type hints (e.g., Python typing / TS types). Fail builds on type errors.
- I/O isolation: domain code never reads/writes files or calls network; inject repositories/adapters.
- Visualization: single-purpose plotting utilities; return figure objects; no business logic in plotting.
- Report: template-driven (e.g., Jinja/Quarto) with reproducible assets and TOC.
- Backend: OpenAPI/JSON Schema for contracts; versioned endpoints; pagination/filtering; input validation.
- Frontend: state management, error boundaries, accessibility (ARIA), responsiveness.

DELIVERABLES (must output)
1) Plan: module map, file tree, and responsibilities.
2) Contracts: schemas, DTOs, interfaces, OpenAPI spec.
3) Tests: complete test suite and how to run.
4) Code: domain, application, interface, infrastructure modules.
5) CLI or notebook for local runs; sample commands.
6) Report generator with sample output.
7) Backend server runnable locally; example curl requests.
8) Frontend app with minimal UI flow; build/run instructions.
9) README with quickstart, architecture diagram (ASCII ok), decisions (ADR), and limitations.

QUALITY GATES
- All tests pass; coverage ≥ {Target}% on domain/application.
- Lint/type checks pass; no TODOs in core modules.
- Benchmark: {TargetLatency/Throughput} on {DatasetSize}.
- Security: secrets via env/secret manager; no PII leakage in logs.

INTERACTION RULES
- If any spec is ambiguous or missing, ask ≤3 concrete clarifying questions at once.
- If a requirement conflicts with Clean Architecture or SOLID, call it out and propose a fix.
- Prefer small PR-sized chunks: implement → test → critique → refine.

OUTPUT FORMAT (strict)
- Use this order per milestone: [PLAN] → [TESTS] → [CODE] → [RUN INSTRUCTIONS] → [CRITIQUE & IMPROVEMENTS].
- Use fenced code blocks with language tags.
- Do not truncate code; if long, split by file with headers like: 
  --- file: {path/to/file.ext} ---