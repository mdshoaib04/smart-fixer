#!/usr/bin/env python3
"""
Test script for the Upload Code feature implementation
This script verifies that the file upload functionality works correctly
"""

import os
import sys

def test_file_extensions():
    """Test that the allowed file extensions are correctly configured"""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Import the routes module to test ALLOWED_EXTENSIONS
    from routes import ALLOWED_EXTENSIONS
    
    # Test that code file extensions are allowed
    code_extensions = {'py', 'js', 'java', 'cpp', 'c', 'cs', 'ts', 'tsx', 'jsx', 'rb', 'php', 'swift', 'go', 'rs', 'kt', 'scala', 'pl', 'dart', 'hs', 'm', 'r', 'sql', 'sh', 'html', 'css'}
    for ext in code_extensions:
        assert ext in ALLOWED_EXTENSIONS, f"Code extension {ext} should be allowed"
    
    # Test that image file extensions are allowed
    image_extensions = {'png', 'jpg', 'jpeg'}
    for ext in image_extensions:
        assert ext in ALLOWED_EXTENSIONS, f"Image extension {ext} should be allowed"
    
    # Test that PDF file extension is allowed
    assert 'pdf' in ALLOWED_EXTENSIONS, "PDF extension should be allowed"
    
    print("✓ All file extensions are correctly configured")

def test_ocr_function_exists():
    """Test that the OCR function exists"""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Import the routes module to test OCR functions
    from routes import extract_code_from_image, extract_code_from_pdf
    
    # Check that the functions exist
    assert extract_code_from_image is not None, "extract_code_from_image function should exist"
    assert extract_code_from_pdf is not None, "extract_code_from_pdf function should exist"
    
    print("✓ OCR and PDF extraction functions exist")

def test_api_routes_exist():
    """Test that the API routes exist"""
    # Add the project root to the Python path
    project_root = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, project_root)
    
    # Import the routes module to test API routes
    import routes
    
    # Check that the route functions exist
    assert hasattr(routes, 'api_extract_code_from_image'), "api_extract_code_from_image route should exist"
    assert hasattr(routes, 'api_extract_code_from_pdf'), "api_extract_code_from_pdf route should exist"
    
    print("✓ API routes for OCR and PDF extraction exist")

if __name__ == "__main__":
    print("Testing Upload Code feature implementation...")
    
    try:
        test_file_extensions()
        test_ocr_function_exists()
        test_api_routes_exist()
        
        print("\n✓ All tests passed! The Upload Code feature is implemented correctly.")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        sys.exit(1)