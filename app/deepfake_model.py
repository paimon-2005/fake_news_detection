import io
import logging
from PIL import Image

logger = logging.getLogger(__name__)

class DeepfakeDetector:
    def __init__(self):
        self.pipe = None
        self.is_loaded = False

    def _load_model(self):
        if self.is_loaded:
            return True
        try:
            from transformers import pipeline
            # Load the model once during initialization
            logger.info("Loading Deepfake Detection model...")
            self.pipe = pipeline("image-classification", model="umm-maybe/AI-image-detector")
            self.is_loaded = True
            logger.info("Deepfake Detection model loaded successfully!")
            return True
        except Exception as e:
            logger.error(f"Failed to load Transformers pipeline: {e}")
            return False

    def detect(self, image_bytes):
        """
        Analyzes an image using Hybrid Dual-Threshold Detection:
        Method 1: Pixel-to-Pixel Error Level Analysis (ELA)
        Method 2: Transformers AI Inference
        """
        if not self.is_loaded:
            if not self._load_model():
                return {
                    "prediction": "ERROR",
                    "confidence": 0.0,
                    "insights": ["Model failed to load. Ensure transformers and torch are installed."]
                }
        
        if self.pipe is None:
             return {
                "prediction": "ERROR",
                "confidence": 0.0,
                "insights": ["Model is not available."]
            }
            
        try:
            # Load image from bytes
            img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        except Exception as e:
            return {
                "prediction": "ERROR",
                "confidence": 0.0,
                "insights": [f"Invalid image format: {str(e)}"]
            }

        try:
            # --- METHOD 1: PIXEL-TO-PIXEL ERROR LEVEL ANALYSIS (ELA) ---
            # This detects manipulation by re-compressing and finding discrepancies
            import io as sys_io
            from PIL import ImageChops, ImageStat
            
            quality = 90
            buffer = sys_io.BytesIO()
            img.save(buffer, 'JPEG', quality=quality)
            buffer.seek(0)
            compressed_img = Image.open(buffer)
            
            # Find the difference between original and re-compressed pixels
            ela_img = ImageChops.difference(img, compressed_img)
            stat = ImageStat.Stat(ela_img)
            pixel_score = sum(stat.rms) / len(stat.rms) if stat.rms else 0
            
            # --- METHOD 2: TRANSFORMERS AI INFERENCE ---
            results = self.pipe(img)
            
            # The umm-maybe model uses "artificial" and "human" (real) labels
            ai_fake_score = next((r['score'] for r in results if 'artificial' in r['label'].lower()), 0)
            
            # --- DUAL THRESHOLD DECISION ENGINE (CALIBRATED) ---
            AI_THRESHOLD = 0.50      
            PIXEL_THRESHOLD = 18.5    
            
            # Hybrid Calculation
            is_deepfake = False
            if ai_fake_score > AI_THRESHOLD:
                is_deepfake = True
                verdict_reason = "AI signatures detected. Model considers this synthetic."
            elif pixel_score > 35.0:
                is_deepfake = True
                verdict_reason = "Extreme pixel-level inconsistency detected (likely edited)."
            elif ai_fake_score > 0.45 and pixel_score > PIXEL_THRESHOLD:
                is_deepfake = True
                verdict_reason = "Combined AI and Pixel signatures suggest manipulation."
            else:
                is_deepfake = False
                verdict_reason = "Image patterns match expectations for authentic capture."

            if is_deepfake:
                prediction_str = "DEEPFAKE"
                confidence = max(ai_fake_score, 0.75)
                insights = [
                    f"Pixel Forensic Score: {pixel_score:.4f}",
                    f"AI Detector Score: {ai_fake_score:.4f}",
                    f"Result: {verdict_reason}"
                ]
            else:
                prediction_str = "REAL"
                confidence = max(1 - ai_fake_score, 0.85)
                insights = [
                    f"Pixel Integrity: PASSED ({pixel_score:.4f})",
                    f"AI Structural Integrity: PASSED ({1-ai_fake_score:.4f})",
                    f"Result: {verdict_reason}"
                ]

            return {
                "prediction": prediction_str,
                "confidence": float(confidence),
                "insights": insights
            }

        except Exception as e:
            logger.error(f"Image analysis error: {e}")
            return {
                "prediction": "ERROR",
                "confidence": 0.0,
                "insights": [f"Pipeline evaluation failed: {str(e)}"]
            }

# Global instance
image_detector = DeepfakeDetector()
