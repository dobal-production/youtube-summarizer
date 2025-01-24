import argparse
from pathlib import Path
import boto3
from typing import List
import logging
import streamlit as st
import yaml
import app_config as config
from youtube_utils import YouTubeHelper
from bedrock_utils import BedrockHelper
from video import Video

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def get_file_path(folder_name: str, file_name: str, extension: str, suffix: str= "") -> Path:
    return (Path(folder_name) / f"{file_name}.{extension}") if not suffix else (Path(config.DATA_DIR) / f"{file_name}_{suffix}.{extension}")

def translate_to_file(video_id: str, source_lang: str, target_lang: str, region: str) -> None:
    translate = boto3.client('translate', region_name=region)

    try:
        with open(Path(config.DATA_DIR) / f"{video_id}.txt", 'rb') as file:
            text = file.read()

        response = translate.translate_document(
            Document={
                'Content': text, 'ContentType': 'text/plain'
            },
            SourceLanguageCode=source_lang,
            TargetLanguageCode=target_lang
        )

        translated_text = (response["TranslatedDocument"]["Content"]).decode(config.FILE_ENCODING)

        with open(Path(config.DATA_DIR) / f"{video_id}_ko.txt", 'w', encoding=config.FILE_ENCODING) as file:
            file.write(translated_text)

    except FileNotFoundError:
        logger.error(f"Source file for video {video_id} not found")
        raise
    except boto3.exceptions.Boto3Error as e:
        logger.error(f"AWS Translation error: {str(e)}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error in translate_to_file: {str(e)}")
        raise

def download_transcripts(video_id, language):
    try:
        transcripts = YouTubeHelper.get_transcript(video_id, language)
        with open(get_file_path(config.DATA_DIR, video_id, "txt"), 'w', encoding=config.FILE_ENCODING) as f:
            f.write(transcripts)
    except Exception as e:
        logger.error(f"Error on download_transcripts: {str(e)}")
        raise

def translate_transcripts(video_id, source_lang, target_lang, region):
    if source_lang == target_lang:
        logger.info("Source and target languages are the same. No translation needed.")
        return

    translate_to_file(video_id, source_lang, target_lang, region)

def get_transcripts(video_id, target_lang="ko"):
    translated_file_path = get_file_path(config.DATA_DIR, video_id, "txt", target_lang)

    if (translated_file_path).exists():
        return get_translated_transcripts(video_id, target_lang)

    return get_original_transcripts(video_id)

def get_original_transcripts(video_id):
    transcripts_file = get_file_path(config.DATA_DIR, video_id, "txt")

    if transcripts_file.exists():
        with open(transcripts_file, 'r', encoding=config.FILE_ENCODING) as f:
            transcripts = f.read()

    return transcripts

def get_translated_transcripts(video_id, target_lang="ko"):
    translated_file_path = get_file_path(config.DATA_DIR, video_id, "txt", target_lang)

    if (translated_file_path).exists():
        with open(translated_file_path, 'r', encoding=config.FILE_ENCODING) as f:
            return f.read()

#initialize markdown file
def initialize_markdown(video_id):
    summary_file = get_file_path(config.DATA_DIR, video_id, "md")
    if summary_file.exists():
        with open(summary_file, 'w', encoding=config.FILE_ENCODING) as f:
            f.write("")
            
# save summarized text to markdown file
def save_as_md(text, video_id, model_name):
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

# add to list as yaml file named videos.yaml
from dataclasses import asdict
def add_to_videos(video_id, video_title, category):
    new_video = Video(video_id, video_title, category)

    videos = load_videos()

    try:
        # if video id exists in the DB, return
        for video in videos:
            if video.video_id == video_id:
                logger.info(f"Video ID {video_id} already exists in the list")
                return

        # add new video to the list
        videos.append(new_video)
        videos.reverse()

        # add list to the list file
        add_to_list_file(videos)
    except Exception as e:
        logger.error(f"Error on add_to_list: {str(e)}")

def add_to_list_file(videos):
    list_file = get_file_path(config.DATA_DIR, "video_list", "yaml")
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
    if videos:
        return st.selectbox("Select a video",
                            options=list(filter(lambda x: x.category == category, videos)),
                            format_func=lambda x: x.title,
                            key=f"select_video_{key}"
                            )
    return None

def display_insight_from_video(videos, categories):
    with st.container():
        row1_col1, row1_col2 = st.columns([0.3, 0.7])

        with row1_col1:
            selected_category = st.selectbox("Select a category",
                                             options=categories,
                                             index=0,
                                             key="select_category_tab3"
                                             )

        with row1_col2:
            selected_video = display_video_selection(selected_category, videos, "tab3")

    question = st.text_area(
        "Ask a question about the video",
        placeholder="What is the video about?",
        key="question_input"
    )

    if st.button("Get Answer"):
        if question:
            get_insight_from_bedrock(question, selected_video)
        else:
            st.warning("Please enter a question")

def get_insight_from_bedrock(question, video):
    try:
        transcripts = get_transcripts(video.video_id, "en")

        # Get the answer from the transcript
        bedrock = BedrockHelper()

        full_answer = ""
        response_placeholder = st.empty()

        # Stream the response
        for response_chunk in bedrock.get_insight_stream(
                model_alias="nm",
                transcripts=transcripts,
                question=question,
                max_tokens=config.DEFAULT_MAX_TOKENS
        ):
            if response_chunk:
                full_answer += response_chunk
                response_placeholder.markdown(full_answer + " ▋")

        # Final update
        response_placeholder.markdown(full_answer)
    except Exception as e:
        st.error(f"An error occurred on getting insight: {str(e)}")


# Display selected video's link for transcripts and translated files with file icon
def display_related_files(video_id):
    with st.container():
        row1_col1, row1_col2 = st.columns([0.3, 0.7])

        with row1_col1:
            if get_file_path(config.DATA_DIR, video_id, "txt").exists():
                st.download_button(
                    label=f"Download Transcripts",
                    data=get_original_transcripts(video_id),
                    file_name=f"{video_id}.txt",
                    mime="text/plain"
                )
        with row1_col2:
            #if translated file exists, display it
            if get_file_path(config.DATA_DIR, video_id, "txt", "ko").exists():
                st.download_button(
                    label=f"Download Translated Transcripts",
                    data=get_translated_transcripts(video_id, "ko"),
                    file_name=f"{video_id}_ko.txt",
                    mime="text/plain"
                )

def display_explore_summaries(videos, categories):
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

    # Display summaries
    if selected_video:
        embed_youtube_player(selected_video.video_id)
        display_related_files(selected_video.video_id)
        display_summary(selected_video)

def summarize_new_video(categories_options):
    with st.container():
        row1_col1, row1_col2 = st.columns(2)

        with row1_col1:
            # Input fields
            video_url = st.text_input("YouTube Video URL", help="Enter the video URL")
            video_id = YouTubeHelper.extract_video_id(video_url)

        with row1_col2:
            # Model selection
            # model_options = ["np", "claude", "titan"]  # Add your available model options
            model_options = BedrockHelper.MODEL_ALIASES.keys()
            selected_models = st.multiselect("Select Bedrock Models",
                                             options=model_options,
                                             default=["s35v2"])
    with st.container():
        row2_col1, row2_col2, row2_col3 = st.columns(3)

        with row2_col1:
            # Language selection
            source_lang_options = ["en", "ko"]
            origin_lang = st.selectbox("Select Source Language", options=source_lang_options, index=0)

            target_lang_options = ["ko", "en"]
            target_lang = st.selectbox("Select Target Language", options=target_lang_options, index=0)
            isTranslate = st.checkbox("Translate", value=True)

        with row2_col2:
            category = st.selectbox("Select Category", options=categories_options, index=0)

        with row2_col3:
            region_options = ["us-east-1", "us-west-2"]
            region = st.selectbox("AWS Region", options=region_options, index=0)

    if st.button("Summarize"):
        if video_id:
            try:
                with st.spinner("Getting video title..."):
                    video_title = YouTubeHelper.get_video_title(video_id)

                with st.spinner("Downloading transcripts..."):
                    download_transcripts(video_id, origin_lang)

                if isTranslate:
                    with st.spinner("Translating transcripts..."):
                        translate_transcripts(video_id, origin_lang, target_lang, region=region)

                with st.spinner("Generating summaries..."):
                    transcripts = get_transcripts(video_id, "en")
                    process_model_summaries(
                        model_aliases=",".join(selected_models).split(","),
                        transcripts=transcripts,
                        video_id=video_id
                    )

                add_to_videos(video_id, video_title, category)

                # Display results
                st.success("Processing completed successfully!")

                # Display summaries
                display_summary(video_id, video_title)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a YouTube Video ID")

# load category list from meta/categories.yaml
def load_category_list():
    category_file = get_file_path(config.META_DIR, "categories", "yaml")
    if category_file.exists():
        with open(category_file, 'r', encoding=config.FILE_ENCODING) as f:
            categories = yaml.safe_load(f) or []

    return categories

def load_videos():
    list_file = get_file_path(config.META_DIR, "videos", "yaml")

    if not list_file.exists():
        with open(list_file, 'w', encoding=config.FILE_ENCODING) as f:
            f.write("")

    with open(list_file, 'r', encoding=config.FILE_ENCODING) as f:
        videos = yaml.safe_load(f)

    return [Video(video_id=video['video_id'], title=video['title'], category=video['category']) for video in videos] if videos else []

def streamlit_app():
    categories = load_category_list()

    st.title("YouTube Summarizer")

    tab1, tab2, tab3 = st.tabs(["New Summary", "Explore Summaries", "Get Insight"])

    with tab1:
        summarize_new_video(categories)

    videos = load_videos()

    if videos:
        with tab2:
            display_explore_summaries(videos, categories)

        with tab3:
            display_insight_from_video(videos, categories)

# (Will be Deprecated) for command line
def main():
    parser = argparse.ArgumentParser(description='YouTube 자막 요약')
    parser.add_argument('--video_id', required=True, help='YouTube Video ID')
    parser.add_argument('--models', default="np", help='Bedrock Model IDs, allow comma for multiple ids')
    parser.add_argument('--lang', default='en', help='en, ko')
    parser.add_argument('--region', default=config.DEFAULT_REGION, help='AWS Region')

    args = parser.parse_args()

    try:
        download_transcripts(args.video_id, args.lang)
        translate_transcripts(args.video_id, args.lang, 'ko', region=args.region)
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
    # main()
    streamlit_app()