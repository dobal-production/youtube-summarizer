import argparse
from pathlib import Path
import boto3
from typing import List
import logging
import streamlit as st
import yaml
import app_config as config
from utils.youtube_utils import YouTubeHelper
from utils.bedrock_utils import BedrockHelper
from utils.i18n_manager import I18nManager
from video import Video
from language_detection import detect_browser_language

def setup_logging():
    """로깅 설정을 구성하고 로거 인스턴스를 반환합니다.
    
    Returns:
        logging.Logger: 구성된 로거 인스턴스
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()
i18n =  I18nManager()

def get_file_path(folder_name: str, file_name: str, extension: str, suffix: str = "") -> Path:
    """폴더, 파일명, 확장자 및 선택적 접미사를 기반으로 파일 경로를 생성합니다.
    
    Args:
        folder_name (str): 대상 폴더명
        file_name (str): 기본 파일명
        extension (str): 파일 확장자
        suffix (str, optional): 파일명의 선택적 접미사. 기본값은 "".
    
    Returns:
        Path: 생성된 파일 경로
    """
    return (Path(folder_name) / f"{file_name}.{extension}") if not suffix else (
            Path(config.DATA_DIR) / f"{file_name}_{suffix}.{extension}")


def translate_to_file(video_id: str, source_lang: str, target_lang: str, model_alias: str = "np") -> None:
    """Bedrock을 사용하여 자막 파일을 번역합니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
        source_lang (str): 원본 언어 코드
        target_lang (str): 대상 언어 코드
        model_alias (str, optional): 번역에 사용할 Bedrock 모델 별칭. 기본값은 "np".
    
    Raises:
        FileNotFoundError: 원본 자막 파일을 찾을 수 없을 때
        Exception: 번역이 실패할 때
    """
    try:
        with open(Path(config.DATA_DIR) / f"{video_id}.txt", 'r', encoding=config.FILE_ENCODING) as file:
            text = file.read()

        bedrock = BedrockHelper()
        translated_text = bedrock.get_translated_text(
            model_alias=model_alias,
            text=text,
            max_tokens=config.DEFAULT_MAX_TOKENS
        )

        with open(Path(config.DATA_DIR) / f"{video_id}_ko.txt", 'w', encoding=config.FILE_ENCODING) as file:
            file.write(translated_text)

    except FileNotFoundError:
        logger.error(f"Source file for video {video_id} not found")
        raise
    except Exception as e:
        logger.error(f"Error in translate_to_file: {str(e)}")
        raise


def apply_filter(transcripts: str):
    """설정에 따라 자막에 단어 필터링을 적용합니다.
    
    Args:
        transcripts (str): 원본 자막 텍스트
    
    Returns:
        str: 필터링된 자막 텍스트
    """
    if config.FILTER_WORDS:
        for word in config.FILTER_WORDS:
            transcripts = transcripts.replace(word, "")
    return transcripts


def download_transcripts(video_id, language):
    """YouTube 비디오 자막을 다운로드하고 파일로 저장합니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
        language (str): 자막 언어 코드
    
    Raises:
        Exception: 자막 다운로드 또는 파일 저장이 실패할 때
    """
    try:
        youtube_helper = YouTubeHelper()
        transcripts = youtube_helper.get_transcript(video_id, language)
        filtered_transcripts = apply_filter(transcripts)
        with open(get_file_path(config.DATA_DIR, video_id, "txt"), 'w', encoding=config.FILE_ENCODING) as f:
            f.write(filtered_transcripts)
    except Exception as e:
        logger.error(f"Error on download_transcripts: {str(e)}")
        raise


def translate_transcripts(video_id, source_lang, target_lang, model_alias="np"):
    """원본 언어와 대상 언어가 다른 경우 자막 파일을 번역합니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
        source_lang (str): 원본 언어 코드
        target_lang (str): 대상 언어 코드
        model_alias (str, optional): 번역에 사용할 Bedrock 모델 별칭. 기본값은 "np".
    """
    if source_lang == target_lang:
        logger.info("Source and target languages are the same. No translation needed.")
        return

    translate_to_file(video_id, source_lang, target_lang, model_alias)


def get_transcripts(video_id, target_lang="ko"):
    """번역된 버전이 있으면 우선적으로 자막을 가져옵니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
        target_lang (str, optional): 대상 언어 코드. 기본값은 "ko".
    
    Returns:
        str: 자막 내용
    """
    translated_file_path = get_file_path(config.DATA_DIR, video_id, "txt", target_lang)

    if (translated_file_path).exists():
        return get_translated_transcripts(video_id, target_lang)

    return get_original_transcripts(video_id)


def get_original_transcripts(video_id):
    """원본 자막 파일 내용을 읽습니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
    
    Returns:
        str: 원본 자막 내용
    """
    transcripts_file = get_file_path(config.DATA_DIR, video_id, "txt")

    if transcripts_file.exists():
        with open(transcripts_file, 'r', encoding=config.FILE_ENCODING) as f:
            transcripts = f.read()

    return transcripts


def get_translated_transcripts(video_id, target_lang="ko"):
    """번역된 자막 파일 내용을 읽습니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
        target_lang (str, optional): 대상 언어 코드. 기본값은 "ko".
    
    Returns:
        str: 파일이 존재하는 경우 번역된 자막 내용
    """
    translated_file_path = get_file_path(config.DATA_DIR, video_id, "txt", target_lang)

    if (translated_file_path).exists():
        with open(translated_file_path, 'r', encoding=config.FILE_ENCODING) as f:
            return f.read()


def initialize_markdown(video_id):
    """비디오 요약을 위한 빈 마크다운 파일을 초기화합니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
    """
    summary_file = get_file_path(config.DATA_DIR, video_id, "md")
    if summary_file.exists():
        with open(summary_file, 'w', encoding=config.FILE_ENCODING) as f:
            f.write("")


def save_as_md(text, video_id, model_name):
    """모델명 헤더와 함께 요약된 텍스트를 마크다운 파일에 추가합니다.
    
    Args:
        text (str): 요약된 텍스트 내용
        video_id (str): YouTube 비디오 ID
        model_name (str): 요약에 사용된 모델명
    """
    summary_file = get_file_path(config.DATA_DIR, video_id, "md")
    with open(summary_file, 'a', encoding=config.FILE_ENCODING) as f:
        f.write(f"\n## {model_name}\n")
        f.write(text)
        f.write("\n\n")


def process_model_summaries(
        model_aliases: List[str],
        transcripts: str,
        video_id: str,
        max_tokens: int = config.DEFAULT_MAX_TOKENS
) -> None:
    """여러 Bedrock 모델을 사용하여 자막 요약을 처리합니다.
    
    Args:
        model_aliases (List[str]): 사용할 모델 별칭 목록
        transcripts (str): 요약할 자막 텍스트
        video_id (str): YouTube 비디오 ID
        max_tokens (int, optional): 요약의 최대 토큰 수. 기본값은 config.DEFAULT_MAX_TOKENS.
    
    Raises:
        Exception: Bedrock 초기화가 실패할 때
    """
    try:
        bedrock = BedrockHelper()

        initialize_markdown(video_id)

        for model_alias in model_aliases:
            try:
                summary = bedrock.get_summarized_text(
                    model_alias=model_alias,
                    text=transcripts,
                    max_tokens=max_tokens
                )
                save_as_md(summary, video_id, bedrock.get_model_name(model_alias))
            except Exception as e:
                logger.error(f"Failed to process model {model_alias}: {str(e)}")
                continue

    except Exception as e:
        logger.error(f"Failed to initialize Bedrock: {str(e)}")
        raise


from dataclasses import asdict


def add_to_videos(new_video: Video):
    """비디오 목록에 새 비디오가 존재하지 않는 경우 추가합니다.
    
    Args:
        new_video (Video): 목록에 추가할 비디오 객체
    """
    videos = load_videos()

    try:
        for video in videos:
            if video.video_id == new_video.video_id:
                logger.info(f"Video ID {new_video.video_id} already exists in the list")
                return

        videos.append(new_video)
        videos.reverse()

        add_to_list_file(videos)
    except Exception as e:
        logger.error(f"Error on add_to_videos: {str(e)}")


def add_to_list_file(videos):
    """비디오 목록을 YAML 파일로 저장합니다.
    
    Args:
        videos (List[Video]): 저장할 비디오 객체 목록
    
    Raises:
        Exception: 파일 쓰기 작업이 실패할 때
    """
    list_file = get_file_path(config.META_DIR, "videos", "yaml")
    try:
        with open(list_file, 'w', encoding=config.FILE_ENCODING) as f:
            yaml.dump(
                [asdict(video) for video in videos],
                f,
                default_flow_style=False,
                sort_keys=False,
                default_style='"'
            )
    except Exception as e:
        logger.error(f"Error on add_to_list_file: {str(e)}")
        raise


def display_summary(video: Video):
    """Streamlit 인터페이스에서 비디오 요약을 표시합니다.
    
    Args:
        video (Video): 비디오 정보를 포함하는 비디오 객체
    """
    summary_file = get_file_path(config.DATA_DIR, video.video_id, "md")
    if summary_file.exists():
        with open(summary_file, 'r', encoding=config.FILE_ENCODING) as f:
            summary = f.read()
            st.subheader(video.title)
            st.markdown(
                f"""
                <div style="min-height: 100px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                    {summary}
                
                </div>
                """.strip(),
                unsafe_allow_html=True
            )
    else:
        st.warning(f"No summary found for video ID {video.video_id}")


def embed_youtube_player(video_id: str):
    """Streamlit 인터페이스에 YouTube 비디오 플레이어를 임베드합니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
    """
    youtube_embed = f"""
        <iframe
            width="100%"
            height="400"
            src="https://www.youtube.com/embed/{video_id}"
            frameborder="0"
            allowfullscreen
        ></iframe>
    """
    st.markdown(youtube_embed, unsafe_allow_html=True)


def display_video_selection(category, videos, key):
    """카테고리별로 필터링된 비디오 선택 드롭다운을 표시합니다.
    
    Args:
        category (str): 비디오를 필터링할 카테고리
        videos (List[Video]): 사용 가능한 비디오 목록
        key (str): Streamlit 위젯의 고유 키
    
    Returns:
        Video or None: 선택된 비디오 객체 또는 사용 가능한 비디오가 없는 경우 None
    """
    if videos:
        filtered_videos = list(filter(lambda x: x.category == category, videos))
        if filtered_videos:
            return st.selectbox("Select a video",
                                options=filtered_videos,
                                format_func=lambda x: x.title,
                                key=f"select_video_{key}",
                                help="Use arrow keys or type to search")
    return None


def display_explore_summaries(videos, categories):
    """카테고리 및 비디오 선택이 포함된 요약 탐색 인터페이스를 표시합니다.
    
    Args:
        videos (List[Video]): 사용 가능한 비디오 목록
        categories (List[str]): 사용 가능한 카테고리 목록
    """
    with st.container():
        row1_col1, row1_col2 = st.columns([0.3, 0.7])

        with row1_col1:
            selected_category = st.selectbox("Select a category",
                                             options=categories,
                                             index=0,
                                             key="select_category_tab2"
                                             )

        with row1_col2:
            selected_video = display_video_selection(selected_category, videos, "tab2")

    if selected_video:
        embed_youtube_player(selected_video.video_id)
        display_related_files(selected_video.video_id)
        display_insight_area(selected_video)
        display_summary(selected_video)


def get_insight_from_bedrock(question, video, model_alias):
    """Bedrock을 사용하여 비디오 자막에서 AI 생성 인사이트를 가져옵니다.
    
    Args:
        question (str): 비디오에 대한 사용자 질문
        video (Video): 비디오 정보를 포함하는 비디오 객체
        model_alias (str): 사용할 Bedrock 모델 별칭
    """
    try:
        transcripts = get_transcripts(video.video_id, "en")

        bedrock = BedrockHelper()

        full_answer = ""
        response_placeholder = st.empty()

        for response_chunk in bedrock.get_insight_stream(
                model_alias=model_alias,
                transcripts=transcripts,
                question=question,
                max_tokens=config.DEFAULT_MAX_TOKENS
        ):
            if response_chunk:
                full_answer += response_chunk
                response_placeholder.markdown(full_answer + " ▋")

        response_placeholder.markdown(full_answer)
    except Exception as e:
        st.error(f"An error occurred on getting insight: {str(e)}")


def get_summary_content(video_id):
    """요약 마크다운 파일 내용을 읽습니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
    
    Returns:
        str: 요약 내용
    """
    summary_file = get_file_path(config.DATA_DIR, video_id, "md")
    if summary_file.exists():
        with open(summary_file, 'r', encoding=config.FILE_ENCODING) as f:
            return f.read()
    return ""


def display_related_files(video_id):
    """자막 및 번역된 파일의 다운로드 버튼을 표시합니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
    """
    with st.container():
        row1_col1, row1_col2, row1_col3 = st.columns([0.33, 0.33, 0.34])

        with row1_col1:
            if get_file_path(config.DATA_DIR, video_id, "txt").exists():
                st.download_button(
                    label=f"Download Transcripts",
                    data=get_original_transcripts(video_id),
                    file_name=f"{video_id}.txt",
                    mime="text/plain"
                )
        with row1_col2:
            if get_file_path(config.DATA_DIR, video_id, "txt", "ko").exists():
                st.download_button(
                    label=f"Download Translated Transcripts",
                    data=get_translated_transcripts(video_id, "ko"),
                    file_name=f"{video_id}_ko.txt",
                    mime="text/plain"
                )
        with row1_col3:
            if get_file_path(config.DATA_DIR, video_id, "md").exists():
                st.download_button(
                    label=f"Download Summary",
                    data=get_summary_content(video_id),
                    file_name=f"{video_id}_summary.md",
                    mime="text/markdown"
                )


def display_insight_area(selected_video):
    """모델 선택 및 질문 입력이 포함된 인사이트 영역을 표시합니다.
    
    Args:
        selected_video (Video): 선택된 비디오 객체
    """
    model_options = BedrockHelper().get_model_names()

    selected_model_name = st.selectbox("Select a model",
                                       options=model_options,
                                       key="select_model_tab2"
                                       )
    selected_model_alias = BedrockHelper().get_model_alias_by_name(selected_model_name)

    question = st.text_area(
        "Ask a question about the video",
        placeholder="What is the video about?",
        key="question_input"
    )

    if st.button("Get Answer"):
        with st.spinner("Getting answer..."):
            if question:
                get_insight_from_bedrock(question, selected_video, selected_model_alias)
            else:
                st.warning("Please enter a question")


def save_transcript_to_s3(video_id):
    """자막 파일을 S3 버킷에 업로드합니다.
    
    Args:
        video_id (str): YouTube 비디오 ID
    """
    try:
        s3 = boto3.client('s3')
        s3.upload_file(
            get_file_path(config.DATA_DIR, video_id, "txt"),
            config.S3_BUCKET_NAME,
            f"{video_id}.txt"
        )
    except Exception as e:
        logger.error(f"Error on save_transcript_to_s3: {str(e)}")


def execute_summary_process(category, is_translate, origin_lang, selected_models, target_lang, video_id):
    """완전한 비디오 요약 프로세스를 실행합니다.
    
    Args:
        category (str): 비디오 카테고리
        is_translate (bool): 자막을 번역할지 여부
        origin_lang (str): 비디오의 원본 언어
        selected_models (List[str]): 선택된 Bedrock 모델 목록
        target_lang (str): 번역을 위한 대상 언어
        video_id (str): YouTube 비디오 ID
    """
    try:
        with st.spinner("Getting video title..."):
            youtube_helper = YouTubeHelper()
            video_title = youtube_helper.get_video_title(video_id)

        with st.spinner("Downloading transcripts..."):
            download_transcripts(video_id, origin_lang)

        if is_translate:
            with st.spinner("Translating transcripts..."):
                # 첫 번째 선택된 모델을 번역에 사용
                translate_model = selected_models[0] if selected_models else "np"
                translate_transcripts(video_id, origin_lang, target_lang, model_alias=translate_model)

        with st.spinner("Generating summaries..."):
            transcripts = get_transcripts(video_id, "en")
            process_model_summaries(
                model_aliases=",".join(selected_models).split(","),
                transcripts=transcripts,
                video_id=video_id
            )

        with st.spinner("Saving transcript to S3..."):
            save_transcript_to_s3(video_id)

        new_video = Video(video_id, video_title, category)

        with st.spinner("Update video list..."):
            add_to_videos(new_video)

        st.success("Processing completed successfully!")

        display_summary(new_video)

    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

def summarize_new_video(categories_options):
    """새 비디오 요약 인터페이스를 표시합니다.
    
    Args:
        categories_options (List[str]): 사용 가능한 카테고리 목록
    """
    with st.container():
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            video_url = st.text_input("YouTube Video URL", help="Enter the video URL")
            video_id = YouTubeHelper.extract_video_id(video_url)

        with row1_col2:
            category = st.selectbox("Select Category", options=categories_options, index=0)

    with st.container():
        bedrock_helper = BedrockHelper()
        model_options = bedrock_helper.get_model_aliases()
        selected_models = st.multiselect("Select Bedrock Models",
                                         options=model_options,
                                         default=list(model_options)[0])

    with st.container():
        row3_col1, row3_col2, row3_col3 = st.columns(3)

        with row3_col1:
            source_lang_options = ["en", "ko"]
            source_lang = st.selectbox("Select Source Language", options=source_lang_options, index=0)

        with row3_col2:
            target_lang_options = ["ko", "en"]
            target_lang = st.selectbox("Select Target Language", 
                                      options=target_lang_options, 
                                      index=0,
                                      disabled=(source_lang == "ko"))

        with row3_col3:
            is_translate = st.checkbox(i18n.get_label("tab.labels.translate"), value=(source_lang == "en"))

    if st.button(i18n.get_label("tab.buttons.summarize")):
        if video_id:
            execute_summary_process(category, is_translate, source_lang, selected_models, target_lang, video_id)
        else:
            st.warning("Please enter a YouTube Video ID")


def load_category_list():
    """meta/categories.yaml 파일에서 카테고리 목록을 로드합니다.
    
    Returns:
        List[str]: 사용 가능한 카테고리 목록
    """
    category_file = get_file_path(config.META_DIR, "categories", "yaml")
    if category_file.exists():
        with open(category_file, 'r', encoding=config.FILE_ENCODING) as f:
            categories = yaml.safe_load(f) or []

    return categories


def load_videos():
    """meta/videos.yaml 파일에서 비디오 목록을 로드합니다.
    
    Returns:
        List[Video]: 비디오 객체 목록
    """
    list_file = get_file_path(config.META_DIR, "videos", "yaml")

    if not list_file.exists():
        with open(list_file, 'w', encoding=config.FILE_ENCODING) as f:
            f.write("")

    with open(list_file, 'r', encoding=config.FILE_ENCODING) as f:
        videos = yaml.safe_load(f)

    return [Video(video_id=video['video_id'], title=video['title'], category=video['category']) for video in
            videos] if videos else []


def main_streamlit():
    """메인 Streamlit 애플리케이션 진입점입니다."""
    st.set_page_config(
        page_title="YouTube Video Summarizer",
        page_icon="🎥",
        layout="wide",
        initial_sidebar_state="auto"
    )
    
    st.session_state['language'] = detect_browser_language()
    i18n.set_language(st.session_state['language'])
    categories = load_category_list()

    st.title(i18n.get_label("app.title"))

    tab1, tab2, tab3 = st.tabs(["New Summary", "Explore Summaries", "Management"])

    with tab1:
        summarize_new_video(categories)

    videos = load_videos()

    if videos:
        with tab2:
            display_explore_summaries(videos, categories)

    with tab3:
        from admin import main as admin
        admin()


def main_terminal():
    """비디오 요약을 위한 명령줄 인터페이스입니다 (deprecated).
    
    Args:
        --video_id (str): YouTube 비디오 ID (필수)
        --models (str): Bedrock 모델 ID들, 쉼표로 구분 (기본값: "np")
        --lang (str): 언어 코드 (기본값: 'en')
    """
    parser = argparse.ArgumentParser(description='YouTube 자막 요약')
    parser.add_argument('--video_id', required=True, help='YouTube Video ID')
    parser.add_argument('--models', default="np", help='Bedrock Model IDs, allow comma for multiple ids')
    parser.add_argument('--lang', default='en', help='en, ko')

    args = parser.parse_args()

    try:
        download_transcripts(args.video_id, args.lang)
        model_alias = args.models.split(",")[0]
        translate_transcripts(args.video_id, args.lang, 'ko', model_alias=model_alias)
        transcripts = get_translated_transcripts(args.video_id)

        process_model_summaries(
            model_aliases=args.models.split(","),
            transcripts=transcripts,
            video_id=args.video_id
        )

        add_to_videos(args.video_id)

    except Exception as e:
        logger.error(f"Error : {str(e)}")


if __name__ == "__main__":
    # main_terminal()
    main_streamlit()