# 旅行回憶紀錄系統

一個基於 Vue.js 和 FastAPI 的旅行記錄系統，支援地圖標記和照片上傳功能。

## 功能特點

- 互動式地圖界面（使用 Mapbox GL JS）
- 旅行地點標記和照片上傳
- 時間軸式的旅行記錄展示
- 響應式設計，支援多種設備

## 技術棧

### 前端
- Vue.js 3 (Composition API)
- TailwindCSS
- Mapbox GL JS

### 後端
- Python FastAPI
- MongoDB
- Docker

## 開始使用

### 開發環境設置

1. 克隆倉庫：
```bash
git clone [repository-url]
cd travel_record
```

2. 啟動開發環境：
```bash
docker-compose up --build
```

3. 訪問應用：
- 前端：http://localhost:3000
- 後端 API：http://localhost:8000
- API 文檔：http://localhost:8000/docs