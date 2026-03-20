import pytest
from utils.dedup import make_hash
from utils.embedder import embed, cosine_similarity
from utils.pdf_parser import extract_text

def test_dedup_same_job():
    h1 = make_hash("stripe", "Software Engineer", "Remote")
    h2 = make_hash("stripe", "Software Engineer", "Remote")
    assert h1 == h2

def test_dedup_different_job():
    h1 = make_hash("stripe", "Software Engineer", "Remote")
    h2 = make_hash("stripe", "Product Manager", "Remote")
    assert h1 != h2

def test_dedup_case_insensitive():
    h1 = make_hash("Stripe", "Software Engineer", "Remote")
    h2 = make_hash("stripe", "software engineer", "remote")
    assert h1 == h2

def test_embed_returns_vector():
    vec = embed("Python backend engineer")
    assert isinstance(vec, list)
    assert len(vec) == 384
    assert all(isinstance(v, float) for v in vec)

def test_cosine_similar_texts():
    v1 = embed("Python backend FastAPI MongoDB")
    v2 = embed("Python developer REST API databases")
    v3 = embed("Graphic designer Photoshop Illustrator")
    assert cosine_similarity(v1, v2) > cosine_similarity(
        v1, v3
    )

def test_pdf_parser_empty_bytes():
    result = extract_text(b"")
    assert result == ""

def test_pdf_parser_invalid_bytes():
    result = extract_text(b"not a pdf")
    assert result == ""
