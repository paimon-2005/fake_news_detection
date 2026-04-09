import os
import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import PassiveAggressiveClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import logging

logger = logging.getLogger(__name__)

class NewsClassifier:
    def __init__(self, model_dir='models'):
        self.model_dir = model_dir
        self.model_path = os.path.join(model_dir, 'model.pkl')
        self.vector_path = os.path.join(model_dir, 'tfidf.pkl')
        self.model = None
        self.vectorizer = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(self.model_path) and os.path.exists(self.vector_path):
                self.model = joblib.load(self.model_path)
                self.vectorizer = joblib.load(self.vector_path)
                logger.info("Model and vectorizer loaded successfully.")
            else:
                logger.warning("Model files not found. Need to train first.")
        except Exception as e:
            logger.error(f"Error loading model: {e}")

    def train(self, data_path=None):
        """
        Trains the model. 
        If data_path is provided, uses that CSV.
        Otherwise, looks for Fake.csv and True.csv in the data directory.
        """
        try:
            df = None
            data_dir = os.path.dirname(data_path) if data_path else 'data'
            fake_path = os.path.join(data_dir, 'Fake.csv')
            true_path = os.path.join(data_dir, 'True.csv')

            if os.path.exists(fake_path) and os.path.exists(true_path):
                logger.info("Found Fake.csv and True.csv. Merging for training...")
                fake_df = pd.read_csv(fake_path)
                true_df = pd.read_csv(true_path)
                
                fake_df['label'] = 'UNRELIABLE'
                true_df['label'] = 'RELIABLE'
                
                df = pd.concat([fake_df, true_df]).reset_index(drop=True)
                # Shuffle the data
                df = df.sample(frac=1, random_state=42).reset_index(drop=True)
            elif data_path and os.path.exists(data_path):
                logger.info(f"Using provided data path: {data_path}")
                df = pd.read_csv(data_path)
            else:
                return {"status": "error", "message": "No training data found (need Fake.csv/True.csv or train.csv)"}

            # Preprocessing
            df = df.dropna(subset=['text', 'label'])
            
            # Combine title and text for better features if title exists
            if 'title' in df.columns:
                X = df['title'] + " " + df['text']
            else:
                X = df['text']
                
            y = df['label']
            
            # Use a subset if data is massive to avoid memory issues in limited environments
            # These datasets are ~45k rows, which is fine.
            
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
            
            self.vectorizer = TfidfVectorizer(stop_words='english', max_df=0.7, min_df=2)
            tfidf_train = self.vectorizer.fit_transform(X_train)
            tfidf_test = self.vectorizer.transform(X_test)
            
            self.model = PassiveAggressiveClassifier(max_iter=100, random_state=42)
            self.model.fit(tfidf_train, y_train)
            
            y_pred = self.model.predict(tfidf_test)
            score = accuracy_score(y_test, y_pred)
            
            # Save models
            os.makedirs(self.model_dir, exist_ok=True)
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.vectorizer, self.vector_path)
            
            return {
                "status": "success",
                "accuracy": round(score, 4),
                "samples": len(df),
                "model_files": [self.model_path, self.vector_path]
            }
        except Exception as e:
            logger.error(f"Training error: {e}")
            return {"status": "error", "message": str(e)}

    def predict(self, text):
        if not self.model or not self.vectorizer:
            return {"error": "Model not trained or loaded."}
        
        try:
            tfidf_input = self.vectorizer.transform([text])
            prediction = self.model.predict(tfidf_input)[0]
            
            # Decision function gives the distance from the hyperplane
            decision = self.model.decision_function(tfidf_input)[0]
            
            # Convert decision distance to confidence
            import numpy as np
            confidence = 1 / (1 + np.exp(-abs(decision)))
            
            # --- LINGUISTIC INSIGHTS ---
            # Get the top words influencing this specific prediction
            feature_names = self.vectorizer.get_feature_names_out()
            feature_index = tfidf_input.nonzero()[1]
            weights = self.model.coef_[0]
            
            insights = []
            for i in feature_index:
                word = feature_names[i]
                weight = weights[i]
                # If we predicted 'UNRELIABLE', find things that pushed it that way (typically positive/negative weights depending on label index)
                # For PassiveAggressive with binary labels, we'll just track magnitude and direction
                insights.append({'word': word, 'weight': round(float(weight), 4)})
            
            # Sort by absolute weight to find most influential words
            insights = sorted(insights, key=lambda x: abs(x['weight']), reverse=True)[:5]
            
            return {
                "prediction": prediction,
                "confidence": round(float(confidence), 4),
                "insights": insights
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return {"error": str(e)}

# Singleton instance
classifier = NewsClassifier()
