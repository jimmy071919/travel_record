#!/bin/bash
# 啟動 MongoDB
mongod --fork --logpath /var/log/mongodb.log

# 啟動後端
cd /app/backend && python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &

# 啟動前端
cd /app/frontend && npm run dev -- --host 0.0.0.0
