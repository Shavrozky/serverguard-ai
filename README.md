# ServerGuard AI

ServerGuard AI adalah aplikasi monitoring server ringan dengan fitur deteksi anomali sederhana. Aplikasi ini dibuat untuk memantau penggunaan resource server seperti CPU, RAM, dan disk, lalu menampilkan hasilnya melalui dashboard web.

## Features

- Collect CPU usage
- Collect RAM usage
- Collect disk usage
- Store metrics into SQLite database
- Display live dashboard charts
- Health status: Healthy, Warning, Critical
- Threshold-based alert
- Z-score anomaly detection
- Anomaly history tracking

## Tech Stack

### Backend

- Python
- FastAPI
- SQLAlchemy
- SQLite
- Uvicorn

### Collector

- Python
- psutil
- requests

### Frontend

- React
- Vite
- Recharts

## Project Structure

```txt
serverguard-ai/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── anomaly.py
│   └── requirements.txt
│
├── collector/
│   ├── collect.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
│
├── README.md
└── .gitignore
```

git
