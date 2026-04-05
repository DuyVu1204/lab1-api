from __future__ import annotations

import traceback
from typing import Any

import torch
from pydantic import BaseModel
from omegaconf import OmegaConf
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

CONFIG_FILE = "./config.yaml"
MODEL_NAME = "facebook/bart-large-cnn"
MODEL_URL = f"https://huggingface.co/{MODEL_NAME}"
MAX_INPUT_TOKENS = 1024
MAX_SUMMARY_TOKENS = 130
MIN_SUMMARY_TOKENS = 30
MIN_WORDS = 30


class TextSummarizer:
    def __init__(self, config_path: str) -> None:
        self.config = OmegaConf.load(config_path)
        model_id = str(self.config.model_path)
        self.tokenizer = AutoTokenizer.from_pretrained(model_id)
        self.model = AutoModelForSeq2SeqLM.from_pretrained(model_id)
        self.model.to("cpu")
        self.model.eval()

    @torch.inference_mode()
    def __call__(self, text: str) -> str:
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=MAX_INPUT_TOKENS,
        )

        summary_ids = self.model.generate(
            inputs["input_ids"],
            attention_mask=inputs.get("attention_mask"),
            max_length=MAX_SUMMARY_TOKENS,
            min_length=MIN_SUMMARY_TOKENS,
            num_beams=4,
            early_stopping=True,
            no_repeat_ngram_size=3,
            forced_bos_token_id=0,
        )
        return self.tokenizer.decode(summary_ids[0], skip_special_tokens=True).strip()


try:
    summarizer = TextSummarizer(CONFIG_FILE)
except Exception as exc:
    summarizer = None
    _load_error = str(exc)
else:
    _load_error = None

app = FastAPI(
    title="Text Summary API",
    description="REST API tạo tóm tắt tiếng Anh cho văn bản đầu vào bằng BART.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SummaryRequest(BaseModel):
    text: str

def _api_payload() -> dict[str, Any]:
    return {
        "name": "API Tóm tắt văn bản",
        "model": MODEL_NAME,
        "huggingface": MODEL_URL,
        "endpoints": {
            "GET /": "Thông tin giới thiệu ngắn gọn về hệ thống và mô tả chức năng của API.",
            "GET /health": " Kiểm tra trạng thái hoạt động của hệ thống.",
            "POST /predict": "Gửi JSON {text} để nhận bản tóm tắt. Trả về JSON {summary, model}.",
        },
    }


def _health_payload() -> dict[str, Any]:
    ok = summarizer is not None
    return {
        "status": "healthy" if ok else "unhealthy",
        "model_loaded": ok,
    }


def _validate_text(text: str) -> None:
    if not text:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "empty_text",
                "message": "Văn bản không được trống. Vui lòng cung cấp văn bản để tóm tắt.",
            },
        )

    if len(text.split()) < MIN_WORDS:
        raise HTTPException(
            status_code=400,
            detail={
                "error": "text_too_short",
                "message": f"Văn bản quá ngắn, hãy nhập ít nhất khoảng {MIN_WORDS} từ để có kết quả tóm tắt tốt hơn.",
            },
        )


def _summarize(text: str) -> str:
    assert summarizer is not None
    return summarizer(text)


def _require_model() -> None:
    if summarizer is None:
        raise HTTPException(
            status_code=503,
            detail={
                "error": "model_unavailable",
                "message": "Không tải được mô hình. Kiểm tra kết nối mạng và cấu hình.",
                "detail": _load_error,
            },
        )


@app.get("/")
def root_info() -> dict[str, Any]:
    return _api_payload()


@app.get("/health")
def health_check() -> dict[str, Any]:
    return _health_payload()


@app.post("/predict")
def generate_summary(request: SummaryRequest) -> JSONResponse:
    _require_model()

    text = request.text.strip()
    _validate_text(text)

    try:
        summary = _summarize(text)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "inference_failed",
                "message": "Lỗi trong lúc suy luận mô hình. Kiểm tra log server để biết chi tiết.",
                "trace": traceback.format_exc(),
            },
        )

    return JSONResponse(status_code=200, content={"summary": summary, "model": MODEL_NAME})


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)