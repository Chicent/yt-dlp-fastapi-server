from fastapi import FastAPI, Request, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

# CORS settings — allow all origins (restrict in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model for POST
class URLRequest(BaseModel):
    url: str

# Health check endpoint
@app.get("/")
def read_root():
    return {"message": "FastAPI yt-dlp API is live."}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

# Main extraction logic (shared by both POST and GET)
def extract_video_data(url: str):
    ydl_opts = {
        'quiet': True,
        'format': 'best',
        'noplaylist': True,
        'cookiefile': 'cookies.txt',  # Load cookies if available
        'proxy': os.getenv("PROXY", None),  # Optional proxy support
        'nocheckcertificate': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        formats = info.get("formats", [])
        best_format = next(
            (fmt for fmt in reversed(formats) if fmt.get("ext") in ["mp4", "webm"] and fmt.get("url")),
            None
        )

        if not best_format:
            return {"status": "error", "message": "No downloadable format found."}

        return {
            "status": "success",
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "webpage_url": info.get("webpage_url"),
            "download_url": best_format.get("url"),
            "ext": best_format.get("ext"),
        }

# POST: /api/download — Accept JSON body
@app.post("/api/download")
async def download_video_post(data: URLRequest):
    try:
        return extract_video_data(data.url)
    except Exception as e:
        return {"status": "error", "message": str(e)}

# GET: /download?url=...
@app.get("/download")
async def download_video_get(url: str = Query(...)):
    try:
        return extract_video_data(url)
    except Exception as e:
        return {"status": "error", "message": str(e)}
