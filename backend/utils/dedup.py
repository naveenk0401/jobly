import hashlib

def make_hash(company: str, title: str, location: str) -> str:
    """
    Creates a unique fingerprint for a job posting.
    Same job posted twice → same hash → MongoDB upsert
    skips the duplicate silently.
    """
    raw = f"{company.strip().lower()}::{title.strip().lower()}::{location.strip().lower()}"
    return hashlib.md5(raw.encode()).hexdigest()
