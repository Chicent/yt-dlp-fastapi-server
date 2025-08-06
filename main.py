from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yt_dlp
import os

app = FastAPI()

# Allow all origins (adjust this in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class URLRequest(BaseModel):
    url: str

@app.get("/")
def read_root():
    return {"message": "FastAPI yt-dlp API is live."}

@app.get("/healthz")
def health_check():
    return {"status": "ok"}

@app.post("/api/download")
async def download_video(data: URLRequest):
    url = data.url

    # yt-dlp options with cookie + proxy support
    ydl_opts = {
        'quiet': True,
        'format': 'best',
        'noplaylist': True,
        'cookiefile': 'cookies.txt',  # Support for cookies
        'proxy': os.getenv("PROXY", None),  # Optional proxy from environment
        'nocheckcertificate': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            formats = info.get("formats", [])
            best_format = None

            for fmt in reversed(formats):
                if fmt.get("ext") in ["mp4", "webm"] and fmt.get("url"):
                    best_format = fmt
                    break

            if not best_format:
                return {"status": "error", "message": "No downloadable formats found."}

            return {
                "status": "success",
                "title": info.get("title"),
                "thumbnail": info.get("thumbnail"),
                "webpage_url": info.get("webpage_url"),
                "download_url": best_format.get("url"),
                "ext": best_format.get("ext"),
            }

    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
