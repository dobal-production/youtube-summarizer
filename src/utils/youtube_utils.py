from typing import Optional, List, Dict, Any
from contextlib import contextmanager
import logging
import re

from googleapiclient.discovery import build
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound
import app_config as ac


class YouTubeError(Exception):
    """YouTube 관련 작업에서 발생하는 기본 예외"""
    pass


class TranscriptError(YouTubeError):
    """자막 관련 작업에서 발생하는 예외"""
    pass


class VideoNotFoundError(YouTubeError):
    """비디오를 찾을 수 없을 때 발생하는 예외"""
    pass


class YouTubeHelper:
    """YouTube API 및 자막 처리를 위한 헬퍼 클래스"""
    
    # YouTube URL 패턴 상수
    URL_PATTERNS = [
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/watch\?v=([^&]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtu\.be\/([^?]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/embed\/([^?]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/v\/([^?]+)',
        r'(?:https?:\/\/)?(?:www\.)?youtube\.com\/shorts\/([^?]+)'
    ]
    
    def __init__(self):
        self.logger = self._setup_logger()
    
    @staticmethod
    def _setup_logger() -> logging.Logger:
        """로거 설정"""
        logger = logging.getLogger(__name__)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            logger.setLevel(logging.INFO)
        return logger

    @contextmanager
    def get_youtube_client(self):
        """YouTube API 클라이언트 컨텍스트 매니저"""
        youtube = None
        try:
            youtube = build('youtube', 'v3', developerKey=ac.YOUTUBE_API_KEY)
            yield youtube
        except Exception as e:
            self.logger.error(f"YouTube API 클라이언트 생성 실패: {e}")
            raise YouTubeError(f"YouTube API 클라이언트 생성 실패: {e}")
        finally:
            if youtube:
                youtube.close()

    def get_transcript(self, video_id: str, language: str = 'en') -> str:
        """
        비디오 자막을 가져와서 텍스트로 반환
        
        Args:
            video_id: YouTube 비디오 ID
            language: 자막 언어 코드 (기본값: 'en')
            
        Returns:
            자막 텍스트
            
        Raises:
            TranscriptError: 자막을 가져올 수 없을 때
        """
        try:
            transcript_data = self._fetch_transcript_data(video_id, language)
            
            if not transcript_data:
                raise TranscriptError(f"자막 데이터가 비어있습니다: {video_id}")
            
            full_transcript = ' '.join([entry.text for entry in transcript_data])
            return full_transcript
            
        except (TranscriptsDisabled, NoTranscriptFound) as e:
            self.logger.error(f"자막을 사용할 수 없습니다 - 비디오 ID: {video_id}, 언어: {language}")
            raise TranscriptError(f"자막을 사용할 수 없습니다: {e}")
        except Exception as e:
            self.logger.error(f"자막 추출 오류 - 비디오 ID: {video_id}, 오류: {e}")
            raise TranscriptError(f"자막 추출 실패: {e}")

    def _fetch_transcript_data(self, video_id: str, language: str) -> List[Any]:
        """
        자막 데이터를 가져오는 내부 메서드
        
        Args:
            video_id: YouTube 비디오 ID
            language: 자막 언어 코드
            
        Returns:
            자막 데이터 리스트
        """
        ytt_api = YouTubeTranscriptApi()

        try:
            # 요청한 언어의 자막 시도
            fetched_transcript = ytt_api.fetch(video_id, languages=[language])
            return fetched_transcript
        except (TranscriptsDisabled, NoTranscriptFound):
            # 요청한 언어가 없으면 기본 자막 시도
            self.logger.warning(f"언어 '{language}' 자막을 찾을 수 없어 기본 자막을 시도합니다 - 비디오 ID: {video_id}")
            try:
                fetched_transcript = ytt_api.fetch(video_id)
                return fetched_transcript
            except Exception as e:
                raise TranscriptError(f"기본 자막도 가져올 수 없습니다: {e}")

    @classmethod
    def extract_video_id(cls, url: str) -> Optional[str]:
        """
        YouTube URL에서 비디오 ID 추출
        
        Args:
            url: YouTube URL
            
        Returns:
            비디오 ID 또는 None (찾을 수 없는 경우)
        """
        if not url or not isinstance(url, str):
            return None
            
        url = url.strip()
        
        for pattern in cls.URL_PATTERNS:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None

    def get_video_title(self, video_id: str) -> str:
        """
        비디오 ID로 비디오 제목 가져오기
        
        Args:
            video_id: YouTube 비디오 ID
            
        Returns:
            비디오 제목
            
        Raises:
            VideoNotFoundError: 비디오를 찾을 수 없을 때
            YouTubeError: API 호출 실패 시
        """
        try:
            with self.get_youtube_client() as youtube:
                request = youtube.videos().list(
                    part='snippet',
                    id=video_id
                )
                response = request.execute()
                
                if not response.get('items'):
                    raise VideoNotFoundError(f"비디오를 찾을 수 없습니다: {video_id}")
                
                return response['items'][0]['snippet']['title']
                
        except VideoNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"비디오 제목 추출 오류 - 비디오 ID: {video_id}, 오류: {e}")
            raise YouTubeError(f"비디오 제목 추출 실패: {e}")

    def get_video_info(self, video_id: str) -> Dict[str, Any]:
        """
        비디오의 상세 정보 가져오기
        
        Args:
            video_id: YouTube 비디오 ID
            
        Returns:
            비디오 정보 딕셔너리 (제목, 설명, 채널명 등)
            
        Raises:
            VideoNotFoundError: 비디오를 찾을 수 없을 때
            YouTubeError: API 호출 실패 시
        """
        try:
            with self.get_youtube_client() as youtube:
                request = youtube.videos().list(
                    part='snippet,statistics',
                    id=video_id
                )
                response = request.execute()
                
                if not response.get('items'):
                    raise VideoNotFoundError(f"비디오를 찾을 수 없습니다: {video_id}")
                
                item = response['items'][0]
                snippet = item['snippet']
                statistics = item.get('statistics', {})
                
                return {
                    'title': snippet['title'],
                    'description': snippet.get('description', ''),
                    'channel_title': snippet['channelTitle'],
                    'published_at': snippet['publishedAt'],
                    'view_count': statistics.get('viewCount', '0'),
                    'like_count': statistics.get('likeCount', '0'),
                    'duration': item.get('contentDetails', {}).get('duration', '')
                }
                
        except VideoNotFoundError:
            raise
        except Exception as e:
            self.logger.error(f"비디오 정보 추출 오류 - 비디오 ID: {video_id}, 오류: {e}")
            raise YouTubeError(f"비디오 정보 추출 실패: {e}")