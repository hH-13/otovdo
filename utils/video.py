"""search and download videos, combine clips, add subs and audio"""

import os
from datetime import datetime

import niquests
from dotenv import load_dotenv
from moviepy import AudioFileClip, CompositeVideoClip, VideoFileClip, concatenate_videoclips
from moviepy.video.tools.subtitles import SubtitlesClip

load_dotenv()


# TODO: deduplicate api call housekeeping code -- may not be required??
# TODO: ability ro use videes from local storage
def download_clips(
    search_terms: list = ["restaurant", "menu", "design", "professional"], min_duration: int = 30
) -> list[tuple[str, str]]:
    """
    Search for video clips using pexels API.
    """
    pexels_url = os.getenv("PEXELS_URL")
    if not pexels_url:
        raise ValueError("PEXELS_URL environment variable is not set")
    pexels_key = os.getenv("PEXELS_KEY")
    if not pexels_key:
        raise ValueError("PEXELS_KEY environment variable is not set")

    total_duration = 0
    saved_videos = []

    while (total_duration < min_duration) and len(search_terms) >= 2:
        response = niquests.get(
            pexels_url,
            params={"query": " ".join(search_terms), "orientation": "portrait"},
            auth=f" {pexels_key}",
        )

        if response.status_code != 200:
            raise ValueError(f"Error: {response.status_code} - {response.text}")

        print(f"Rate Limit: {response.headers['X-RateLimit-Limit']}")
        print(f"Rate Limit Remaining: {response.headers['X-RateLimit-Remaining']}")
        print(
            f"Rate Limit Reset: {datetime.fromtimestamp(int(response.headers['X-RateLimit-Reset'])).strftime('%Y-%m-%d %H:%M:%S %Z')}"
        )

        search_terms = search_terms[:-1]
        data = response.json()

        if data.get("total_results") == 0:
            print("No results found, retrying with less specific search terms...")
            continue

        videos = [
            (
                sorted((i.get("video_files")), key=lambda x: x.get("width") * x.get("height"), reverse=True)[0].get(
                    "link"
                ),
                i.get("duration", 0),
            )
            for i in data.get("videos")
        ]

        for url, duration in videos:
            try:
                with open(path := f"./assets/video/{url.split('/')[-1]}", "wb") as f:
                    video_bytes = niquests.get(url).content
                    assert video_bytes, "Failed to download video"
                    f.write(video_bytes)
            except Exception as e:
                print(f"Failed to download video from {url}: {e}")
                continue
            total_duration += duration if duration <= 15 else duration / 2
            print(f"Downloaded {url} ({duration} seconds)")
            saved_videos.append((path, url, duration))
            if total_duration >= min_duration:
                break

    print(f"{len(saved_videos)} videos with a total duration of {total_duration} seconds downloaded.")

    return saved_videos


def combine_clips(clips: list[tuple], output_path: str = "./assets/video/combined.mp4", max_duration: int = 30) -> str:
    """
    Combine video clips into a single video file.
    """
    if not clips:
        raise ValueError("No clips to combine")

    video_clips = [VideoFileClip(clip[0], audio=False, target_resolution=(1080, 1920)) for clip in clips]

    final_clip = concatenate_videoclips(
        [clip[(clip.duration / 2 if clip.duration > 15 else clip.duration) :] for clip in video_clips], method="chain"
    )

    final_clip.write_videofile(output_path, audio=False)
    print(f"Combined video saved to {output_path}")
    final_clip.close()
    map(lambda x: x.close(), video_clips)  # Close all video clips
    print("Closed all video clips")

    return output_path


def add_dubsub(
    video_path: str,
    subtitles_path: str | None = None,
    audio_path: str | None = None,
    output_path: str = "./assets/video/final.mp4",
) -> None:
    """
    Add subtitles to a video file.
    """
    if not os.path.exists(video_path):
        raise ValueError(f"Video file {video_path} does not exist")
    video_clip = VideoFileClip(video_path)
    if audio_path:
        if not os.path.exists(audio_path):
            raise ValueError(f"Subtitles file {audio_path} does not exist")
        video_clip = video_clip.with_audio(
            AudioFileClip(audio_path)
        )  # .set_audio(audio_path) if audio_path else video_clip

    if subtitles_path:
        if not os.path.exists(subtitles_path):
            raise ValueError(f"Subtitles file {subtitles_path} does not exist")
        subs = SubtitlesClip(subtitles_path, font="./assets/fonts/bold_font.ttf")
        video_clip = CompositeVideoClip([video_clip, subs])

    video_clip.write_videofile(output_path, codec="libx264", audio_codec="aac")
    print(f"Video saved to {output_path}")
    video_clip.close()
    print("Closed video clip")
