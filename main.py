from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp

app = FastAPI()

# CORS to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

# Root endpoint for quick live check
@app.get("/")
def read_root():
    return {"message": "FastAPI yt-dlp API is live."}

# Health check route for Render or monitoring
@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Main download endpoint
@app.post("/api/download")
async def download_video(data: URLRequest):
    url = data.url
    ydl_opts = {
        'quiet': True,
        'skip_download': True,
        'force_generic_extractor': False,
        'extract_flat': 'in_playlist',
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info_dict = ydl.extract_info(url, download=False)
            formats = info_dict.get("formats", [])
            best_format = None

            for fmt in reversed(formats):
                if fmt.get("ext") in ["mp4", "webm"] and fmt.get("url"):
                    best_format = fmt
                    break

            if not best_format:
                return {"error": "No downloadable formats found."}

            return {
                "title": info_dict.get("title"),
                "thumbnail": info_dict.get("thumbnail"),
                "download_url": best_format.get("url")
            }
    except Exception as e:
        return {"error": str(e)}
