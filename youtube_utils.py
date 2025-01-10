# import sys
# print("environments", sys.executable)
from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi
from dataclasses import dataclass
import app_config as ac
import logging
from contextlib import contextmanager
import re

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)
logger = setup_logging()


class YouTubeHelper:
    @staticmethod
    @contextmanager
    def get_youtube_client():
        try:
            youtube = build('youtube', 'v3', developerKey=ac.YOUTUBE_API_KEY)
            yield youtube
        finally:
            if youtube:
                youtube.close()

    @staticmethod
    def get_transcript(video_id, language='en'):
        try:
            youtube = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = youtube.find_transcript([language])
            full_transcript = ' '.join([entry['text'] for entry in transcript.fetch()])
            return full_transcript

        except Exception as e:
            logger.error(f"Transcript extraction error: {e}")
            raise

    @staticmethod
    def extract_video_id(url):
        video_id = re.search(r'(?<=v=)[^&#]+', url)
        if video_id:
            return video_id.group(0)

        video_id = re.search(r'(?<=be/)[^&#]+', url)
        if video_id:
            return video_id.group(0)

        video_id = re.search(r'(?<=youtu.be/)[^&#]+', url)
        if video_id:
            return video_id.group(0)

        return None

    # Getting video title from video ID using Youtube API
    @staticmethod
    def get_video_title(video_id: str) -> str:
        try:
            with YouTubeHelper.get_youtube_client() as youtube:
                request = youtube.videos().list(
                    part='snippet',
                    id=video_id
                )
                response = request.execute()

                return response['items'][0]['snippet']['title']
        except Exception as e:
            logger.error(f"Video title extraction error: {e}")
            raise

# dataclass for video information
@dataclass
class VideoInfo:
    video_id: str
    title: str