# 🚨 TruthSense: Full-Stack Fake News Detection System

TruthSense is a production-ready, AI-powered web application designed to identify misinformation in news articles with high precision.

## ✨ Core Features
- **Real-Time Detection**: Passive Aggressive Classifier provides instant reliability scores.
- **Premium UI**: Modern dark-mode dashboard with glassmorphism and fluid animations.
- **RESTful API**: Comprehensive v1 API for integration with other platforms.
- **Persistent History**: Every analysis is stored and searchable for future reference.
- **Live Statistics**: Dynamic dashboard showing system-wide analysis trends.
- **Model Training**: One-click retraining capability from the web interface.

## 🛠️ Technology Stack
- **Backend**: Python 3.9+, Flask, SQLAlchemy (SQLite/PostgreSQL)
- **ML Engine**: Scikit-Learn (Passive Aggressive Classifier), Pandas, TF-IDF
- **Frontend**: Vanilla HTML5, CSS3 (Modern Flex/Grid), JavaScript (ES6+)
- **DevOps**: Docker & Docker Compose

## 🚀 Quick Start (Local)

1. **Setup Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # venv\Scripts\activate on Windows
   pip install -r requirements.txt
   ```

2. **Run Application**:
   ```bash
   python run.py
   ```
   Access at: `http://localhost:5000`

3. **Train Model**:
   - Go to the **Statistics** page.
   - Click **Retrain Model** (requires `data/train.csv`).

## 🐳 Docker Setup
```bash
docker-compose up --build
```

## 📂 Project Structure
```
fake_news_detection/
├── app/                # Flask Backend
│   ├── ml_model.py     # classifier logic
│   ├── models.py       # DB schema
│   └── routes.py       # API & Web routes
├── templates/          # HTML Templates
├── static/             # Assets (CSS/JS)
├── data/               # Training data
├── models/             # Saved .pkl models
├── run.py              # Entry point
└── Dockerfile          # Container config
```
