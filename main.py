from utils.audio import VOICES, combine_audio_tracks, download_songs, generate_srt_file, generate_tts
from utils.video import add_dubsub, combine_clips, download_clips


def main():
    print("Hello from otovdo!")

    # Order of operations
    # - Choose a subject
    # - Write the script
    # - Generate the tts/voice-over from the script
    generate_tts()
    # - Add bgm music or sound track
    download_songs()
    combine_audio_tracks()
    # - Obtain relevant video clips acc to the audio track's length
    download_clips()
    # - Stitch the video clips together
    combine_clips()
    # - Generate subtitles
    generate_srt_file()
    # - Combine the audio and video tracks
    add_dubsub()


if __name__ == "__main__":
    main()
