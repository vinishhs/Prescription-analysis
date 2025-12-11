import pytesseract
from PIL import Image
import cv2
import numpy as np
import logging
import io
import re

logger = logging.getLogger(__name__)

class OCRProcessor:
    def __init__(self):
        logger.info("OCR Processor initialized")
        # Medical terms dictionary for correction
        self.medical_words = [
            "amoxicillin", "atorvastatin", "ibuprofen", "metformin",
            "lisinopril", "omeprazole", "warfarin", "aspirin", "acetaminophen",
            "prednisone", "tramadol", "gabapentin", "cephalexin", "azithromycin",
            "clarithromycin", "doxycycline", "metoprolol", "simvastatin",
            "amlodipine", "hydrochlorothiazide", "clopidogrel", "pantoprazole",
            "sertraline", "fluoxetine", "citalopram", "venlafaxine", "duloxetine",
            "albuterol", "montelukast", "fluticasone", "loratadine", "diphenhydramine",
            "mg", "mL", "mcg", "PO", "IV", "IM", "SC", "QID", "TID", "BID", "QD", "PRN"
        ]

    def preprocess_image(self, image):
        """Enhanced preprocessing for prescription images"""
        # Convert to OpenCV format
        img_cv = np.array(image)
        
        # Convert to grayscale
        if len(img_cv.shape) == 3:
            img_cv = cv2.cvtColor(img_cv, cv2.COLOR_RGB2GRAY)
        
        # Noise reduction
        img_cv = cv2.medianBlur(img_cv, 3)
        img_cv = cv2.GaussianBlur(img_cv, (5, 5), 0)
        
        # Contrast enhancement
        img_cv = cv2.convertScaleAbs(img_cv, alpha=1.5, beta=40)
        
        # Multiple thresholding techniques
        _, thresh1 = cv2.threshold(img_cv, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh2 = cv2.adaptiveThreshold(img_cv, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
        
        # Combine results
        processed = cv2.bitwise_or(thresh1, thresh2)
        
        # Morphological operations to clean up text
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
        processed = cv2.dilate(processed, kernel, iterations=1)
        
        return processed

    def get_medical_config(self, psm=6):
        """Get Tesseract config optimized for medical text"""
        return f'''
        --oem 3 --psm {psm}
        -c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789.,()/-:mgML
        -c preserve_interword_spaces=1
        -c textord_min_linesize=2.0
        '''.strip()

    def clean_medical_text(self, text: str) -> str:
        """Clean and correct common medical OCR errors"""
        if not text:
            return ""
            
        # Common medical term corrections
        corrections = {
            'qid': 'QID', 'tid': 'TID', 'bid': 'BID', 'qd': 'QD',
            'po': 'PO', 'iv': 'IV', 'im': 'IM', 'sc': 'SC', 'prn': 'PRN',
            'mg': 'mg', 'ml': 'mL', 'mcg': 'mcg', 'tab': 'tablet',
            'caps': 'capsule', 'disp': 'dispense', 'sig': 'instructions'
        }
        
        # Fix spacing around units and dosages
        text = re.sub(r'(\d)([a-zA-Z])', r'\1 \2', text)  # 500mg → 500 mg
        text = re.sub(r'([a-zA-Z])(\d)', r'\1 \2', text)  # mg500 → mg 500
        
        # Apply corrections
        for wrong, correct in corrections.items():
            text = re.sub(r'\b' + wrong + r'\b', correct, text, flags=re.IGNORECASE)
        
        return text

    def enhance_with_medical_dictionary(self, text: str) -> str:
        """Use medical dictionary to correct OCR errors"""
        words = text.split()
        corrected_words = []
        
        for word in words:
            original_word = word
            word_lower = word.lower()
            
            # Check if word is close to any medical term
            found_correction = False
            for medical_word in self.medical_words:
                if medical_word.startswith(word_lower[:3]) and len(word_lower) >= 3:
                    corrected_words.append(medical_word)
                    found_correction = True
                    break
            
            if not found_correction:
                corrected_words.append(original_word)
        
        return ' '.join(corrected_words)

    def extract_text_from_image(self, image_data: bytes) -> str:
        """
        Extract text from prescription image using enhanced OCR
        """
        try:
            # Convert bytes to image
            image = Image.open(io.BytesIO(image_data))
            
            # Preprocess image
            img_cv = self.preprocess_image(image)
            
            # Try multiple PSM modes for better accuracy
            texts = []
            for psm in [6, 8, 11, 12]:  # Different page segmentation modes
                config = self.get_medical_config(psm)
                text = pytesseract.image_to_string(img_cv, config=config)
                if text.strip():
                    texts.append(text.strip())
            
            # Return the best result (longest text)
            if texts:
                best_text = max(texts, key=len)
                
                # Clean and enhance the text
                cleaned_text = self.clean_medical_text(best_text)
                enhanced_text = self.enhance_with_medical_dictionary(cleaned_text)
                
                logger.info(f"OCR extracted text: {enhanced_text}")
                return enhanced_text
            else:
                return ""
                
        except Exception as e:
            logger.error(f"OCR processing error: {e}")
            return ""

# Global instance
ocr_processor = OCRProcessor()