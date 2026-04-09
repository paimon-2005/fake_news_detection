# TruthSense API Reference

Base URL: `http://localhost:5000/api/v1`

## Endpoints

### 1. Predict Article
`POST /predict`
- **Body**: `{ "title": "...", "author": "...", "text": "..." }`
- **Response**: `{ "id": 1, "prediction": "RELIABLE", "confidence": 0.85, "status": "success" }`

### 2. Get History
`GET /history`
- **Response**: List of prediction objects.

### 3. Get Stats
`GET /stats`
- **Response**: `{ "total": 10, "reliable": 6, "unreliable": 4, "avg_confidence": 0.88 }`

### 4. Retrain Model
`POST /train`
- **Requirement**: `data/train.csv` must exist.
- **Response**: Training results and accuracy.

### 5. Health Check
`GET /health`
- **Response**: `{ "status": "healthy", "model_loaded": true }`
