# **생성형 AI를 위한 프롬프팅**

너는 **Python과 Langchain 프레임워크를 활용한 RAG(Retrieval-Augmented Generation) 시스템 구축 전문가**야. 특히 **Google의 Gemini 모델(Embedding 및 LLM)**을 사용하여 Markdown 형식의 로컬 문서를 처리하고, **FAISS VectorDB**를 효율적으로 저장하고 재사용하여 Streamlit과 같은 웹 애플리케이션과의 통합을 고려한 확장 가능한 코드를 작성하는 데 능숙해.

### **과업 지시 (Task)**

아래 요구사항에 따라 RAG 분석 파이프라인을 구축하는 Python 스크립트를 작성해 줘. **단계별로 생각해서(Let's think step by step)** 각 과정을 논리적으로 구성하고, 최종 코드는 하나의 완성된 파일로 제출해 줘.

#### **RAG 파이프라인 단계별 요구사항:**

1. **Document Loading (문서 로딩):**
    
    - `docs` 라는 이름의 하위 폴더에 있는 모든 Markdown(`.md`) 파일을 재귀적으로 탐색하고 로드해야 해.
        
    - `langchain.document_loaders`를 활용하여 구현해 줘.
        
2. **Text Splitting (텍스트 분할):**
    
    - 로드된 Markdown 문서는 헤더(`\n#`, `\n##`, `\n###`, `\n####`)를 기준으로 의미 있는 단위로 분할해야 해. 이는 각 섹션의 컨텍스트를 유지하기 위함이야.
        
    - `langchain.text_splitter.MarkdownHeaderTextSplitter`를 사용하는 것이 가장 적합해.
        
3. **Embedding (임베딩):**
    
    - 분할된 텍스트 청크(Chunk)를 벡터로 변환해야 해.
        
    - **Google의 Gemini 임베딩 모델**(`langchain_google_genai.GoogleGenerativeAIEmbeddings`)을 사용해 줘.
        
    - API 키 관리를 위해 `.env` 파일과 `python-dotenv` 라이브러리를 사용하는 코드를 포함해 줘. (예: `GOOGLE_API_KEY="YOUR_API_KEY"`)
        
4. **VectorDB Store (벡터 DB 저장):**
    
    - 임베딩된 벡터를 FAISS VectorDB에 저장해야 해.
        
    - **효율성 및 재사용성 극대화:**
        
        - VectorDB를 로컬 파일(예: `faiss_index`)로 저장하는 기능을 반드시 포함해야 해.
            
        - 스크립트 실행 시, 이미 저장된 `faiss_index` 파일이 존재하면 새로 DB를 구축하는 대신 기존 파일을 로드하여 사용하도록 구현해 줘. 이 로직은 웹 애플리케이션에서 반복적인 임베딩 비용과 시간을 줄이는 데 매우 중요해.
            
5. **Retrieval (검색):**
    
    - 사용자 질문(Query)이 들어오면, VectorDB에서 가장 관련성 높은 문서를 검색(Similarity Search)하는 Retriever를 생성해야 해.
        
    - 상위 3개의 가장 유사한 문서를 검색하도록 설정해 줘.
        
6. **Prompt & LLM (프롬프트 및 LLM):**
    
    - 검색된 문서(Context)와 사용자 질문(Query)을 조합하여 LLM에 전달할 프롬프트를 생성해야 해.
        
    - 프롬프트 템플릿을 사용하여 컨텍스트와 질문을 명확하게 구분해 줘.
        
    - **Google의 Gemini LLM**(`langchain_google_genai.ChatGoogleGenerativeAI`)을 사용하여 답변을 생성해 줘.
        
7. **Output (출력):**
    
    - 최종적으로 생성된 답변을 콘솔에 출력해 줘.
        

### **출력 형식 (Format)**

- **하나의 완성된 Python 스크립트 (`.py`) 파일**로 코드를 제공해 줘.
    
- 코드의 각 RAG 단계(로딩, 분할, 임베딩, 저장, 검색, 생성)마다 **상세한 주석**을 달아서 코드의 목적과 흐름을 쉽게 이해할 수 있도록 설명해 줘.
    
- 필요한 라이브러리를 `requirements.txt` 형식으로 파일 상단 주석에 명시해 줘.
    
- `.env` 파일 설정 방법에 대한 간단한 안내를 주석에 포함해 줘.
    

### **추가 고려사항 (Constraints & Considerations)**

- **오류 처리:** 파일 로딩 실패, API 키 부재 등 발생할 수 있는 예외 상황에 대한 기본적인 오류 처리 로직(예: `try-except`)을 추가하여 코드의 안정성을 높여줘.
    
- **모듈성:** 각 RAG 단계를 별도의 함수로 구성하여 코드의 가독성과 재사용성을 높이는 것을 고려해 줘. (예: `load_documents()`, `create_vector_db()`, `execute_query()`)
    
- **사용자 피드백:** 스크립트 실행 과정에서 "문서 로딩 중...", "VectorDB 생성 중...", "질문에 대한 답변 생성 중..." 과 같은 사용자 친화적인 진행 상태 메시지를 `print` 문으로 출력해 줘.


-----

#  # 생성형 AI를 위한 프롬프트 (Prompt for Generative AI)

**[Persona]**
너는 **Python을 사용한 AI 애플리케이션 구축 전문가**야. 특히 **LangChain 프레임워크와 Google의 Gemini 모델을 활용한 RAG(Retrieval-Augmented Generation) 시스템 설계 및 구현에 매우 능숙**해. 너의 코드는 항상 모듈화되어 있고, 효율적이며, 실제 서비스에 통합될 것을 고려하여 작성되어야 해.

**[Task]**
지정된 로컬 폴더에 있는 여러 Markdown(`.md`) 파일들을 소스로 사용하여, 사용자의 질문에 대한 답변을 생성하고 그 출처를 함께 제시하는 RAG 분석 Python 스크립트를 작성해 줘. 이 스크립트는 최종적으로 Streamlit과 같은 웹 애플리케이션에 통합될 것을 목표로 하므로, **VectorDB를 파일로 저장하고 재사용하여 효율성을 극대화**해야 해.

**[Constraints & Detailed Requirements]**

**1. RAG 파이프라인:** 아래의 7단계 구조를 반드시 따라서 코드를 작성해 줘. 각 단계별로 주석을 달아 어떤 역할을 하는지 명확히 설명해야 해.
\- **Step 1: Document Load:** `'docs'`라는 하위 폴더에 있는 모든 Markdown(`.md`) 파일을 로드해야 해. `langchain_community.document_loaders.DirectoryLoader`와 `UnstructuredMarkdownLoader`를 사용해 줘.
\- **Step 2: Text Split:** 로드된 문서는 단순히 글자 수로 자르는 것이 아니라, **Markdown의 헤더(`#`, `##`, `###`, `####`)를 기준**으로 의미 있는 단위로 분할해야 해. `langchain.text_splitter.MarkdownHeaderTextSplitter`를 사용하고, 분할 시 각 청크(chunk)가 어떤 파일, 어떤 헤더에 속해 있었는지 **메타데이터(metadata)에 자동으로 저장**되도록 해줘.
\- **Step 3: Embedding:** 텍스트 임베딩을 위해 Google의 Gemini 모델을 사용해야 해. `langchain_google_genai.GoogleGenerativeAIEmbeddings`를 사용하고, API 키는 `.env` 파일에서 `GOOGLE_API_KEY`라는 이름으로 불러오도록 설정해 줘.
\- **Step 4: VectorDB Store:**
\- 임베딩된 벡터는 `FAISS`를 사용하여 VectorDB에 저장해야 해.
\- **핵심 요구사항:** 생성된 VectorDB(FAISS index)는 `faiss_index`라는 이름의 로컬 폴더에 파일로 저장되어야 해. 스크립트 실행 시, 해당 폴더가 이미 존재하면 새로 생성하는 대신 **기존 파일을 불러와서 사용**하도록 로직을 구현해 줘. 이는 웹 애플리케이션 재시작 시 매번 문서를 다시 임베딩하는 비효율을 방지하기 위함이야.
\- **Step 5: Retrieval:** 저장된 VectorDB로부터 사용자의 질문과 가장 유사한 문서를 검색하는 `retriever`를 생성해 줘. 검색 결과에는 반드시 문서의 내용(page\_content)과 함께 출처를 명시할 수 있는 \*\*메타데이터(metadata)\*\*가 포함되어야 해.
\- **Step 6: Prompt & LLM:**
\- LLM(Large Language Model)은 `langchain_google_genai.ChatGoogleGenerativeAI`의 `gemini-pro` 모델을 사용해 줘.
\- 검색된 문서를 컨텍스트(context)로 활용하여 질문에 답변을 생성하도록 프롬프트 템플릿을 구성해 줘. 이 템플릿은 AI에게 **반드시 주어진 컨텍스트 내에서만 답변**하고, 답변의 근거가 된 **문서의 출처(source)를 명확히 밝히도록** 지시해야 해.
\- 프롬프트 템플릿 예시:
\`\`\`
당신은 주어진 문서를 바탕으로 질문에 답변하는 AI 어시스턴트입니다. 컨텍스트를 벗어난 내용은 답변하지 마세요. 답변을 할 때는 어떤 문서를 참고했는지 출처를 반드시 명시해주세요.

````
      [Context]
      {context}

      [Question]
      {question}

      [Answer]
      ```
- **Step 7: Output:** 최종 답변과 그 출처를 함께 출력해 줘. LangChain Expression Language (LCEL)를 사용하여 전체 파이프라인을 간결하고 직관적으로 연결해 줘.
````

**2. 코드 구조 및 품질:**
\- **모듈화:** 데이터 로딩 및 VectorDB 초기화, RAG 체인 생성, 질문/답변 실행 부분을 각각 논리적인 함수로 분리하여 \*\*단일 책임 원칙(Single Responsibility Principle)\*\*을 따르도록 설계해 줘. 이는 향후 Streamlit 앱에 각 기능을 통합하기 용이하게 만들어 줄 거야.
\- **예외 처리:** 파일 I/O나 API 호출 시 발생할 수 있는 오류에 대비하여 기본적인 `try-except` 구문을 추가해 줘.
\- **실행 가능성:** 코드가 바로 실행될 수 있도록, 예시로 사용할 수 있는 간단한 Markdown 파일(`docs/sample1.md`, `docs/sample2.md`)을 생성하는 코드와 함께, 전체 RAG 과정을 테스트하는 샘플 질문을 포함한 `if __name__ == "__main__":` 블록을 작성해 줘.

**[Format]**
결과는 아래 두 가지를 모두 포함하여 Markdown 형식으로 출력해 줘.

1.  **`requirements.txt`:** 스크립트 실행에 필요한 모든 Python 라이브러리와 버전 정보를 명시한 목록.
2.  **`rag_with_markdown.py`:** 위의 모든 요구사항을 반영한 완전한 Python 스크립트 파일. 코드의 각 부분에는 이해를 돕기 위한 상세한 주석을 포함해 줘.

**[Let's think step by step]**
자, 이제 단계별로 생각하며 위 요구사항을 만족하는 완벽한 RAG 파이썬 코드를 만들어 보자. 먼저 필요한 라이브러리를 정의하고, 전체적인 파일 구조를 구상한 뒤, RAG의 7단계 파이프라인을 순서대로 함수로 구현해 나가는 거야. 특히 VectorDB를 파일로 저장하고 재사용하는 부분이 핵심이니, 이 로직을 신중하게 설계해야 해.
