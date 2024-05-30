API_KEY_ASSEMBLYAI: str = "2396e3cdd1b345549d7a9fdb0f27c9e8";
HEADERS: dict           = {"authorization": API_KEY_ASSEMBLYAI};

# URL's -----------------------------------------------------------------

UPLOAD_URL: str         = "https://api.assemblyai.com/v2/upload";
TRANSCRIPT_URL: str     = "https://api.assemblyai.com/v2/transcript";
POLL_URL: str           = TRANSCRIPT_URL+"/";