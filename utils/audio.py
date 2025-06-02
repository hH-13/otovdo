"""search and download songs, generate tts, combine tts and bgm, generate subtitles"""
# https://www.youtube.com/playlist?list=PLabJQI0gItOjHOspcPvJJHBJRady1Cjm2  -- 20
# https://www.youtube.com/playlist?list=PL-4lk5FyOCGX1TJn8wAZCGln1l2m4HzaR  -- 40

import os
from datetime import UTC, datetime
from textwrap import wrap

from dotenv import load_dotenv
from moviepy import AudioClip, AudioFileClip, CompositeAudioClip
from niquests import Session, get
from srt_equalizer import equalize_srt_file

load_dotenv()

VOICES = [
    # DISNEY VOICES
    "en_us_ghostface",  # Ghost Face
    "en_us_chewbacca",  # Chewbacca
    "en_us_c3po",  # C3PO
    "en_us_stitch",  # Stitch
    "en_us_stormtrooper",  # Stormtrooper
    "en_us_rocket",  # Rocket
    # ENGLISH VOICES
    "en_au_001",  # English AU - Female
    "en_au_002",  # English AU - Male
    "en_uk_001",  # English UK - Male 1
    "en_uk_003",  # English UK - Male 2
    "en_us_001",  # English US - Female (Int. 1)
    "en_us_002",  # English US - Female (Int. 2)
    "en_us_006",  # English US - Male 1
    "en_us_007",  # English US - Male 2
    "en_us_009",  # English US - Male 3
    "en_us_010",  # English US - Male 4
    # EUROPE VOICES
    "fr_001",  # French - Male 1
    "fr_002",  # French - Male 2
    "de_001",  # German - Female
    "de_002",  # German - Male
    "es_002",  # Spanish - Male
    # AMERICA VOICES
    "es_mx_002",  # Spanish MX - Male
    "br_001",  # Portuguese BR - Female 1
    "br_003",  # Portuguese BR - Female 2
    "br_004",  # Portuguese BR - Female 3
    "br_005",  # Portuguese BR - Male
    # ASIA VOICES
    "id_001",  # Indonesian - Female
    "jp_001",  # Japanese - Female 1
    "jp_003",  # Japanese - Female 2
    "jp_005",  # Japanese - Female 3
    "jp_006",  # Japanese - Male
    "kr_002",  # Korean - Male 1
    "kr_003",  # Korean - Female
    "kr_004",  # Korean - Male 2
    # SINGING VOICES
    "en_female_f08_salut_damour",  # Alto
    "en_male_m03_lobby",  # Tenor
    "en_female_f08_warmy_breeze",  # Warmy Breeze
    "en_male_m03_sunshine_soon",  # Sunshine Soon
    # OTHER
    "en_male_narration",  # narrator
    "en_male_funny",  # wacky
    "en_female_emotional",  # peaceful
]


def download_songs(
    search_terms: list = ["restaurant", "menu", "design", "professional"], min_duration: int = 30
) -> list[tuple[str, str]]:
    """
    Search for songs using a music API.
    """
    # download bgm from some API, or maybe not from some API and directly from the tube
    #  stick around to find out
    raise NotImplementedError("This function needs to be implemented.")


def generate_tts(script: str, voice: str = "en_us_ghostface", max_dialogue_len: int = 300) -> str:
    """
    Generate text-to-speech audio from the provided script.
    based on https://github.com/oscie57/tiktok-voice
    """
    if not script:
        raise ValueError("No script provided.")
    if voice not in VOICES:
        raise ValueError(f"Voice '{voice}' not found. Available voices: {', '.join(VOICES)}")

    urls = {
        "https://tiktok-tts.weilnet.workers.dev/api/generation": (lambda x: str(x).split('"')[5]),
        "https://tiktoktts.com/api/tiktok-tts": (lambda x: str(x).split('"')[3].split(",")[1]),
    }

    active_url = None
    # check with url is available rn
    for url in urls:
        if get(url.split("api")[0]).status_code == 200:
            active_url = url
            break
    if not active_url:
        raise ConnectionRefusedError(
            "TTS Service not available and probably temporarily rate limited, try again later..."
        )

    lines = [script] if len(script) < max_dialogue_len else wrap(script, max_dialogue_len - 1)
    requests = []

    with Session(multiplexed=True) as s:
        for line in lines:
            requests.append(
                s.post(
                    active_url,
                    json={"text": line, "voice": voice},
                    headers={"Content-Type": "application/json"},
                )
            )
        return "".join([urls[active_url](r.content) for r in requests if r.active != "error"])


def _generate_subtitles_local(script_lines: list[str], tts_lines: list[AudioFileClip]) -> str:
    start_time = 0
    subtitles = []

    for i, (sentence, audio_clip) in enumerate(zip(script_lines, tts_lines), start=1):
        end_time = start_time + audio_clip.duration

        # Format: subtitle index, start time --> end time, sentence
        subtitle_entry = f"{i}\n{datetime.fromtimestamp(start_time, UTC).strftime('%H:%M:%S,%f')} --> {datetime.fromtimestamp(end_time, UTC).strftime('%H:%M:%S,%f')}\n{sentence}\n"
        subtitles.append(subtitle_entry)

        start_time = end_time  # Update start time for the next subtitle

    return "\n".join(subtitles)


# TODO: full refactor
def _generate_subtitles_api(audio_path: str, voice: str, api_key: str) -> str:
    """
    Generates subtitles from a given audio file and returns the path to the subtitles.

    Args:
        audio_path (str): The path to the audio file to generate subtitles from.

    Returns:
        str: The generated subtitles
    """

    # language_mapping = {
    #     "br": "pt",
    #     "id": "en",  # AssemblyAI doesn't have Indonesian
    #     "jp": "ja",
    #     "kr": "ko",
    # }

    # if voice in language_mapping:
    #     lang_code = language_mapping[voice]
    # else:
    #     lang_code = voice

    # aai.settings.api_key = ASSEMBLY_AI_API_KEY
    # config = aai.TranscriptionConfig(language_code=lang_code)
    # transcriber = aai.Transcriber(config=config)
    # transcript = transcriber.transcribe(audio_path)
    # subtitles = transcript.export_subtitles_srt()

    # return subtitles
    raise NotImplementedError


def generate_srt_file(
    audio_file: str,
    script_lines: list[str] | None = None,
    tts_lines: list[AudioFileClip] | None = None,
    prefer_local: bool = True,
) -> str:
    """
    Generate subtitles from the provided audio file.
    """
    srt = None
    # locally or using an API??
    if (not prefer_local) and (AAI_API_KEY := os.getenv("ASSEMBLYAI_API_KEY")):
        srt = _generate_subtitles_api(audio_file, "tets", AAI_API_KEY)

    if script_lines and tts_lines:
        srt = _generate_subtitles_local(script_lines, tts_lines)

    if srt:
        with open(subs_path := f"{audio_file}.srt", "w") as subs:
            subs.write(srt)
        equalize_srt_file(subs_path, subs_path, target_chars=10, method="halving")
        return subs_path

    raise ValueError("Either script_lines and tts_lines or prefer_local must be provided.")


def combine_audio_tracks(tts_audio: str, bgm_audio: str) -> AudioClip:
    """
    Combine TTS audio and background music into a single audio track.
    """
    # Pmix the TTS audio with the background music. balance the levels...
    return CompositeAudioClip(
        (
            AudioFileClip(tts_audio).with_fps(44100),
            AudioFileClip(bgm_audio).with_fps(44100).with_volume_scaled(0.2),
        )
    )
