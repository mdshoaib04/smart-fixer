import pdfplumber

def extract_code_from_pdf(pdf_path):
    """Extract code from a PDF file"""
    try:
        # Extract text from PDF
        extracted_text = ""
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text += page_text + "\n"
        
        # Clean up the extracted text
        if extracted_text:
            # Remove extra whitespace and clean up lines
            lines = [line.strip() for line in extracted_text.split('\n') if line.strip()]
            cleaned_text = '\n'.join(lines)
            return cleaned_text, None
        else:
            return "", None
            
    except Exception as e:
        return None, f"Error processing PDF: {str(e)}"

# Test the function
if __name__ == "__main__":
    extracted_text, error = extract_code_from_pdf("test.pdf")
    if error:
        print(f"Error: {error}")
    else:
        print(f"Extracted text: {extracted_text}")