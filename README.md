# Lab 1: FastAPI Text Summarization

## Thông tin sinh viên

- Họ và tên: Nguyễn Duy Vũ
- Môn học: Tư Duy Tính Toán
- Trường: Trường Đại học Khoa học Tự nhiên TP.HCM
- Khoa: Khoa Công nghệ Thông tin

## Tên mô hình và liên kết Hugging Face

- Tên mô hình: `facebook/bart-large-cnn` (tóm tắt văn bản)
- Liên kết Hugging Face: https://huggingface.co/facebook/bart-large-cnn

## Mô tả ngắn về hệ thống

Đồ án xây dựng một REST API để tóm tắt văn bản tiếng Anh. Server dùng FastAPI, còn phần suy luận dùng mô hình `facebook/bart-large-cnn` từ Hugging Face. Khi nhận text đầu vào, hệ thống sẽ tokenize, sinh câu tóm tắt và trả về JSON gồm `summary` và `model`.

## Cài đặt môi trường và thư viện

Khuyến nghị dùng Python `3.11.x` để đồng nhất với môi trường phát triển.

### Vì sao nên dùng môi trường ảo (`venv`)

Môi trường ảo giúp tách riêng thư viện của từng project, tránh xung đột phiên bản giữa các bài khác nhau trên cùng máy. Khi dùng `venv`, bạn có thể:

- Cài đúng dependency cho riêng project này mà không ảnh hưởng Python toàn cục.
- Dễ tái hiện môi trường trên máy khác chỉ với `requirements.txt`.
- Hạn chế lỗi kiểu `Import could not be resolved` do cài package nhầm interpreter.
- Dọn dẹp nhanh: chỉ cần xóa thư mục `.venv` khi muốn tạo lại môi trường sạch.

### Cài trực tiếp (không dùng venv)

Trong thư mục gốc của dự án, chạy một trong hai lệnh sau:

```bash
pip install -r requirements.txt
```

Hoặc:

```bash
python -m pip install -r requirements.txt
```

### Dùng môi trường ảo (`.venv`)

1. Tạo môi trường ảo:

```bash
python -m venv .venv
```

2. Kích hoạt theo hệ điều hành:

| Hệ điều hành | Lệnh |
| --- | --- |
| Windows (PowerShell) | `.\.venv\Scripts\Activate.ps1` |
| Windows (CMD) | `.\.venv\Scripts\activate.bat` |
| Linux / macOS | `source .venv/bin/activate` |

*PowerShell: nếu bị chặn script, chạy một lần `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`.*

3. Cài dependencies:

```bash
pip install -r requirements.txt
```

4. Thoát venv:

```bash
deactivate
```

File `requirements.txt` hiện gồm các thư viện chính: FastAPI, Uvicorn, Transformers (`<5`), PyTorch, Requests, Pydantic, OmegaConf.

### Kiểm tra sau khi cài

```bash
python -c "import fastapi, torch, transformers, pydantic, omegaconf, requests; print('Dependencies OK')"
```

### Lỗi thường gặp

- `Import could not be resolved`: VS Code đang chọn sai interpreter, hãy chọn đúng Python của `.venv`.
- `pip` cài sai môi trường: dùng `python -m pip install -r requirements.txt` thay cho `pip install ...`.
- PowerShell không cho chạy script activate: chạy `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` rồi kích hoạt lại.

---

## Hướng dẫn chạy chương trình

Chạy server FastAPI:

```bash
python -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

Các cách chạy server khác:

1. Dùng `uvicorn` trực tiếp (khi đã có trong PATH):

```bash
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

2. Dùng Python Launcher trên Windows:

```bash
py -3.11 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

3. Chạy thẳng file `main.py` (vì đã có `uvicorn.run(...)` trong `if __name__ == "__main__"`):

```bash
python main.py
```

Mở các đường dẫn kiểm tra:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/health`
- `http://127.0.0.1:8000/docs`

Chạy file test:

```bash
python test_api.py
```

## Hướng dẫn gọi API và ví dụ request/response

### 1. `GET /`

Request:

```bash
curl http://127.0.0.1:8000/
```

Response mẫu:

```json
{
  "name": "API Tóm tắt văn bản",
  "model": "facebook/bart-large-cnn",
  "huggingface": "https://huggingface.co/facebook/bart-large-cnn",
  "endpoints": {
    "GET /": "Thông tin giới thiệu ngắn gọn về hệ thống và mô tả chức năng của API.",
    "GET /health": "Kiểm tra trạng thái hoạt động của hệ thống.",
    "POST /predict": "Gửi JSON {text} để nhận bản tóm tắt. Trả về JSON {summary, model}."
  }
}
```

### 2. `GET /health`

Request:

```bash
curl http://127.0.0.1:8000/health
```

Response mẫu:

```json
{
  "status": "healthy",
  "model_loaded": true
}
```

### 3. `POST /predict`

Lưu ý: API yêu cầu văn bản đầu vào đủ dài (khoảng từ 30 từ trở lên), nếu quá ngắn sẽ trả lỗi `text_too_short`.

Request:

```bash
curl -X POST http://127.0.0.1:8000/predict \
  -H "Content-Type: application/json" \
  -d "{\"text\": \"Artificial intelligence is being used in healthcare to support diagnosis and treatment planning. Hospitals can analyze medical images faster, detect diseases earlier, and reduce human error. At the same time, doctors still play a critical role in interpreting results and communicating with patients in a safe and ethical way.\"}"
```

Response mẫu:

```json
{
  "summary": "...",
  "model": "facebook/bart-large-cnn"
}
```


## Liên kết video demo

- Xem video: [Google Drive - Demo sản phẩm](https://drive.google.com/file/d/1KZavJ_0sfSAw3SeonUAnoASgT9hHWxXh/view?usp=sharing)
- Ghi chú: Vui lòng bật quyền `Anyone with the link` để giảng viên có thể xem trực tiếp.
