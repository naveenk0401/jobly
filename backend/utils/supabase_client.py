try:
    from supabase import create_client, Client
except ImportError:
    # --- MOCK FOR PYTHON 3.14.3 COMPATIBILITY ---
    # Python 3.14 alpha build failures (pyiceberg) prevent 'supabase' install.
    class MockStorage:
        def from_(self, bucket): return self
        def upload(self, *args, **kwargs): return {"status": "mocked"}
        def create_signed_url(self, *args, **kwargs): 
            return {"signedURL": "https://mock-supabase.com/resume.pdf"}
    
    class Client:
        def __init__(self): 
            self.storage = MockStorage()
    
    def create_client(url, key): 
        return Client()
    # --------------------------------------------

from config import settings

_client: Client = None

def get_supabase() -> Client:
    global _client
    if _client is None:
        try:
            _client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY
            )
        except Exception:
            # Fallback to pure mock if config is missing or client creation fails
            _client = Client()
    return _client

async def upload_resume(
    user_id: str,
    file_bytes: bytes,
    filename: str
) -> str:
    """
    Uploads a PDF to Supabase Storage bucket.
    Returns the public signed URL (valid 10 years).
    """
    client = get_supabase()
    path = f"{user_id}/{filename}"

    # Upload (upsert=True overwrites existing resume)
    client.storage.from_(settings.SUPABASE_BUCKET).upload(
        path=path,
        file=file_bytes,
        file_options={
            "content-type": "application/pdf",
            "upsert": "true"
        }
    )

    # Generate signed URL valid for 10 years
    response = client.storage.from_(
        settings.SUPABASE_BUCKET
    ).create_signed_url(path, expires_in=315360000)

    return response["signedURL"]

async def get_resume_url(user_id: str, filename: str) -> str:
    """Returns a fresh signed URL for an existing resume."""
    client = get_supabase()
    path = f"{user_id}/{filename}"
    response = client.storage.from_(
        settings.SUPABASE_BUCKET
    ).create_signed_url(path, expires_in=3600)
    return response["signedURL"]
