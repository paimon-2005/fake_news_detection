import os
from flask import Blueprint, request, jsonify, render_template
from app.models import db, Prediction
from app.ml_model import classifier
from app.deepfake_model import image_detector
from config import Config

api = Blueprint('api', __name__)
main = Blueprint('main', __name__)

# --- WEB ROUTES ---

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/predict')
def predict_page():
    return render_template('predict.html')

@main.route('/history')
def history_page():
    return render_template('history.html')

@main.route('/stats')
def stats_page():
    return render_template('stats.html')

@main.route('/about')
def about_page():
    return render_template('about.html')

@main.route('/deepfake')
def deepfake_page():
    return render_template('deepfake.html')

# --- API ENDPOINTS ---

@api.route('/v1/predict', methods=['POST'])
def predict():
    data = request.get_json()
    if not data or 'text' not in data:
        return jsonify({'error': 'No text provided'}), 400
    
    title = data.get('title', '')
    author = data.get('author', '')
    text = data.get('text', '')
    
    result = classifier.predict(text)
    
    if 'error' in result:
        return jsonify(result), 500
    
    # Save to database
    prediction = Prediction(
        title=title,
        author=author,
        text=text,
        prediction=result['prediction'],
        confidence=result['confidence']
    )
    db.session.add(prediction)
    db.session.commit()
    
    return jsonify({
        'id': prediction.id,
        'prediction': result['prediction'],
        'confidence': result['confidence'],
        'insights': result.get('insights', []),
        'status': 'success'
    })

@api.route('/v1/history', methods=['GET'])
def get_history():
    predictions = Prediction.query.order_by(Prediction.timestamp.desc()).limit(100).all()
    return jsonify([p.to_dict() for p in predictions])

@api.route('/v1/stats', methods=['GET'])
def get_stats():
    total = Prediction.query.count()
    reliable = Prediction.query.filter_by(prediction='RELIABLE').count()
    unreliable = Prediction.query.filter_by(prediction='UNRELIABLE').count()
    
    avg_confidence = db.session.query(db.func.avg(Prediction.confidence)).scalar() or 0
    
    return jsonify({
        'total': total,
        'reliable': reliable,
        'unreliable': unreliable,
        'avg_confidence': round(float(avg_confidence), 4)
    })

@api.route('/v1/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy', 'model_loaded': classifier.model is not None})

@api.route('/v1/train', methods=['POST'])
def train_model():
    # In a real app, you'd upload a file or point to a dataset
    # For now, let's assume there's a file in Config.DATA_PATH
    data_file = os.path.join(Config.DATA_PATH, 'train.csv')
    if not os.path.exists(data_file):
        return jsonify({'error': 'Training data file (train.csv) not found in data/ directory'}), 404
    
    result = classifier.train(data_file)
    return jsonify(result)

@api.route('/v1/clear-history', methods=['DELETE'])
def clear_history():
    try:
        Prediction.query.delete()
        db.session.commit()
        return jsonify({'status': 'success', 'message': 'History cleared'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/v1/detect-image', methods=['POST'])
def detect_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file uploaded'}), 400
        
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
        
    try:
        image_bytes = file.read()
        result = image_detector.detect(image_bytes)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
