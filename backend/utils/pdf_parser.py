import PyPDF2
import io

def extract_text(file_bytes: bytes) -> str:
    """
    Extracts raw text from a PDF file.
    Returns cleaned, concatenated text from all pages.
    Falls back gracefully if a page fails.
    """
    try:
        reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
        pages = []
        for page in reader.pages:
            try:
                text = page.extract_text()
                if text:
                    pages.append(text.strip())
            except Exception:
                continue
        full_text = "\n".join(pages)
        # Normalize whitespace
        return " ".join(full_text.split())
    except Exception as e:
        print(f"[PDF] Parse error: {e}")
        return ""
