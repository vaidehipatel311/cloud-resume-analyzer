import textract

def extract_text(file_path):
    text = textract.process(file_path).decode('utf-8', errors='ignore')
    return text
