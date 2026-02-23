import logging
import shutil
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, Form, HTTPException, status
from fastapi.responses import JSONResponse, FileResponse
from starlette.requests import Request
from fastapi.middleware.cors import CORSMiddleware  # CORS 미들웨어 임포트

from .core.config import Config
from .core.analysis import run_analysis
from .models.schemas import AnalysisResult

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Life Data Analysis Agent",
    description="브레이크 패드 내구-필드 수명 분석 및 가속계수 산출 AI 에이전트",
    version="1.2.0"
)

# --- CORS 미들웨어 설정 ---
# React 개발 서버(localhost:3000)에서의 요청을 허용합니다.
origins = [
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 모든 HTTP 메소드 허용
    allow_headers=["*"],  # 모든 HTTP 헤더 허용
)
# -------------------------


UPLOADS_DIR = Path("uploads")
UPLOADS_DIR.mkdir(exist_ok=True)
RESULTS_DIR = Path("results")
RESULTS_DIR.mkdir(exist_ok=True)

@app.get("/results/{filename}", tags=["Results"])
async def get_result_file(filename: str):
    """결과 디렉토리에서 분석 결과 파일(이미지, 마크다운)을 제공합니다."""
    file_path = RESULTS_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(file_path)

@app.post("/analyze/", response_model=AnalysisResult, tags=["Analysis"])
async def create_analysis(
    request: Request,
    file: UploadFile = File(..., description="분석할 Excel 또는 CSV 파일"),
    lifetime_column: str = Form('distance(km)', description="수명 데이터 컬럼명"),
    type_column: str = Form('type', description="데이터 구분 컬럼명 ('test', 'field')"),
    test_type_value: str = Form('test', description="내구시험 데이터 구분 값"),
    field_type_value: str = Form('field', description="필드 데이터 구분 값"),
    confidence_level: float = Form(0.95, description="신뢰수준 (0.0 ~ 1.0)")
):
    logger.info(f"파일 수신: {file.filename}")
    
    file_location = UPLOADS_DIR / file.filename
    try:
        with file_location.open("wb+") as file_object:
            shutil.copyfileobj(file.file, file_object)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"파일 저장 실패: {e}")
    finally:
        file.file.close()

    try:
        config = Config(
            data_path=str(file_location),
            lifetime_column=lifetime_column,
            type_column=type_column,
            test_type_value=test_type_value,
            field_type_value=field_type_value,
            confidence_level=confidence_level,
            results_dir=str(RESULTS_DIR)
        )

        analysis_results = run_analysis(config)

        base_url = str(request.base_url)
        report_path = analysis_results.get("report_path")
        report_url = f"{base_url}results/{Path(report_path).name}" if report_path else None
        
        plot_urls = []
        for p_path in analysis_results.get("plot_paths", []):
            plot_urls.append(f"{base_url}results/{Path(p_path).name}")

        return AnalysisResult(
            message="분석이 성공적으로 완료되었습니다.",
            report_url=report_url,
            plot_urls=plot_urls,
            analysis_summary=analysis_results.get("analysis_summary")
        )
    except Exception as e:
        logger.error(f"분석 파이프라인 실행 중 오류 발생: {e}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=AnalysisResult(message="분석 중 오류가 발생했습니다.", error=str(e)).dict()
        )