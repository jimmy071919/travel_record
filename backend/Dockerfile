# 使用 Python 3.9 作為基礎映像
FROM python:3.9-slim

# 設置工作目錄
WORKDIR /app

# 複製 requirements.txt
COPY requirements.txt .

# 安裝依賴
RUN pip install -r requirements.txt

# 複製源代碼
COPY . .

# 啟動後端服務
CMD ["python3", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
