import cv2
import pytesseract

def extract_code_from_image(image_path):
    """Extract code from an image using OCR"""
    try:
        # Read the image
        image = cv2.imread(image_path)
        if image is None:
            return None, "Could not read image file"
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply several preprocessing techniques to enhance text detection
        # 1. Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        # 2. Apply adaptive thresholding for better contrast
        adaptive_thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2)
        
        # 3. Apply morphological operations to clean up the image
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
        cleaned = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_CLOSE, kernel)
        
        # 4. Resize the image to improve OCR for small text
        height, width = cleaned.shape[:2]
        if height < 300 or width < 300:  # If image is small
            scale_factor = max(300/height, 300/width)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            resized = cv2.resize(cleaned, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
        else:
            resized = cleaned
        
        # Use pytesseract to extract text with enhanced configuration
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz!\"#$%&\'()*+,-./:;<=>?@[\\]^_`{|}~ '
        extracted_text = pytesseract.image_to_string(resized, config=custom_config)
        
        # Clean up the extracted text
        if extracted_text:
            # Remove extra whitespace and clean up lines
            lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            return cleaned_text, None
        else:
            return "", None
            
    except Exception as e:
        return None, f"Error processing image: {str(e)}"

# Test the function (you would need to have an image file to test this)
if __name__ == "__main__":
    print("OCR functionality is ready to use.")