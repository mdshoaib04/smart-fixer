# Upload Code Feature Implementation

## Overview
This document describes the implementation of the Upload Code feature with proper validation, detection, and error handling as requested.

## Features Implemented

### 1. Accepted File Types
The upload system now accepts the following file types:

#### Text Code Files
- Extensions: .py, .js, .c, .cpp, .java, .html, .css, .ts, .bash, .php, etc.
- Automatically verified for language by checking file extension and syntax
- Invalid code files show error: "⚠ invalid code file."

#### Images with Code
- Supported formats: .jpg, .jpeg, .png
- Uses OCR (Optical Character Recognition) to extract text from images
- Enhances text detection and contrast for small text
- **Validates extracted text for programming syntax** (rejects normal text, human faces, nature scenes)
- Valid code is inserted into the text editor
- Invalid images show error: "⚠ Can't take input of this image. Try again with an image that contains programming code."

#### PDF Files with Code
- Extracts text from PDFs and checks for programming syntax
- **Validates extracted text for programming syntax** (rejects normal text, human faces, nature scenes)
- Valid code is inserted into the text editor
- Invalid PDFs show error: "⚠ Can't take input of this file. Try again with a file that contains programming code."

### 2. Files to Reject
The following file types are completely rejected:
- Videos (.mp4, .mkv, .avi)
- Audio files (.mp3, .wav)
- Documents (.docx, .txt, .rtf, .pptx, .xls, etc.)
- Images without code or with non-programming text

Error message: "⚠ Can't take this file as input. Give a code file with an extension like .py, .js, .c, etc."

### 3. Processing Logic
- Automatically detects file type
- Extracts code text from valid files
- **Verifies syntax and confirms programming language** using enhanced validation
- Inserts code directly into the text editor
- Shows proper popup messages for invalid content

### 4. UI/UX Updates
- Changed text label below upload input to: "Upload any files, images or PDFs with code"
- Added dynamic hints:
  - "Only code files or images with code are supported."
  - "Avoid uploading random images or documents."

## Technical Implementation

### Frontend Changes
1. Modified `templates/upload_or_write.html`:
   - Updated file input to accept all file types
   - Enhanced `handleFileUpload` function with comprehensive file validation
   - Updated UI text and hints

### Backend Changes
1. Modified `routes.py`:
   - Updated `ALLOWED_EXTENSIONS` to include image and PDF files
   - Enhanced `extract_code_from_image` function with programming syntax validation:
     - Gaussian blur to reduce noise
     - Adaptive thresholding for better contrast
     - Morphological operations to clean up the image
     - Resizing small images to improve OCR accuracy
     - Custom pytesseract configuration with character whitelist
     - **Programming syntax validation to reject normal text**
   - Enhanced `extract_code_from_pdf` function with programming syntax validation
   - Added `/api/extract-code-from-image` route for OCR processing
   - Added `/api/extract-code-from-pdf` route for PDF processing

2. Created `requirements.txt` with necessary dependencies:
   - opencv-python for image processing
   - pytesseract for OCR functionality
   - pdfplumber for PDF text extraction

### Testing
Created `test_upload_feature.py` to verify:
- File extensions are correctly configured
- OCR and PDF extraction functions exist
- API routes are properly implemented

Created `test_code_validation.py` to verify:
- Programming syntax detection works correctly
- Normal text is properly rejected
- Code content is properly accepted

## Dependencies
The implementation requires the following system dependencies:
- Tesseract OCR engine (for image text extraction)
- Python packages listed in requirements.txt

## Error Handling
Comprehensive error handling with user-friendly messages for all scenarios:
- Invalid file types
- Empty or corrupted files
- OCR processing failures
- PDF extraction failures
- Network errors
- **Content validation failures (normal text vs code)**

## Future Improvements
- Add support for more image formats
- Improve OCR accuracy with advanced preprocessing
- Add support for compressed archives (.zip, .tar.gz)
- Implement file size limits
- Add progress indicators for large file processing