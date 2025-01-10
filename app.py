import argparse
from pathlib import Path
import boto3
from typing import List
import logging
import streamlit as st
import yaml
import app_config as config
from youtube_utils import YouTubeHelper, VideoInfo
from bedrock_utils import BedrockHelper

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

logger = setup_logging()

def get_file_path(file_name: str, extension: str, suffix: str= "") -> Path:
    return (Path(config.DATA_DIR) / f"{file_name}.{extension}") if not suffix else (Path(config.DATA_DIR) / f"{file_name}_{suffix}.{extension}")

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
        with open(get_file_path(video_id, "txt"), 'w', encoding=config.FILE_ENCODING) as f:
            f.write(transcripts)
    except Exception as e:
        logger.error(f"Error on download_transcripts: {str(e)}")
        raise

def translate_transcripts(video_id, source_lang, target_lang, region):
    if source_lang == target_lang:
        logger.info("Source and target languages are the same. No translation needed.")
        return

    translate_to_file(video_id, source_lang, target_lang, region)

def get_translated_transcripts(video_id, target_lang='en'):
    if target_lang == 'en':
        translated_file_path = get_file_path(video_id, "txt")
    else:
        translated_file_path = get_file_path(video_id, "txt", "ko")

    if (translated_file_path).exists():
        with open(translated_file_path, 'r', encoding=config.FILE_ENCODING) as f:
            transcripts = f.read()

    return transcripts

#initialize markdown file
def initialize_markdown(video_id):
    summary_file = get_file_path(video_id, "md")
    if summary_file.exists():
        with open(summary_file, 'w', encoding=config.FILE_ENCODING) as f:
            f.write("")
            
# save summarized text to markdown file
def save_as_md(text, video_id, model_name):
    summary_file = get_file_path(video_id, "md")
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

def get_videos():
    list_file = get_file_path("video_list", "yaml")

    if not list_file.exists():
        with open(list_file, 'w', encoding=config.FILE_ENCODING) as f:
            f.write("")

    with open(list_file, 'r', encoding=config.FILE_ENCODING) as f:
        videos = yaml.safe_load(f)

    return [VideoInfo(video_id=video['video_id'], title=video['title']) for video in videos] if videos else []

# add to list as yaml file named video_list.yaml
from dataclasses import asdict
def add_to_videos(video_id, video_title):
    new_video = VideoInfo(video_id=video_id, title=video_title)

    videos = get_videos()

    try:
        # if video id exists in the DB, return
        for video in videos:
            if video.video_id == video_id:
                logger.info(f"Video ID {video_id} already exists in the list")
                return

        # add new video to the list
        videos.append(new_video)

        # add list to the list file
        add_to_list_file(videos)
    except Exception as e:
        logger.error(f"Error on add_to_list: {str(e)}")

def add_to_list_file(videos):
    list_file = get_file_path("video_list", "yaml")
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


def display_summary(video_id, video_title):
    summary_file = get_file_path(video_id, "md")
    if summary_file.exists():
        with open(summary_file, 'r', encoding=config.FILE_ENCODING) as f:
            summary = f.read()
            st.subheader(video_title)
            st.markdown(
                f"""
                <div style="min-height: 100px; padding: 10px; border: 1px solid #ccc; border-radius: 5px;">
                    {summary}
                </div>
                """.strip(),
                unsafe_allow_html=True
            )
    else:
        st.warning(f"No summary found for video ID {video_id}")

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

def get_selected_video(videos, key):
    if videos:
        video_options = convert_to_list(videos)
        return st.selectbox("Select a video",
                            options=video_options,
                            format_func=lambda x: x[1],
                            key=f"select_video_{key}"
                            )
    return None

def streamlit_app():
    st.title("YouTube Transcript Summarizer")

    tab1, tab2, tab3 = st.tabs(["New Summary", "Explore Summaries", "Get Insight"])

    with tab1:
        summarize_new_video()

    # Load video list
    videos = load_video_list()

    if videos:
        with tab2:
            explore_summaries(videos)

        with tab3:
            get_insight_from_video(videos)


def load_video_list():
    list_file = get_file_path("video_list", "yaml")
    if list_file.exists():
        with open(list_file, 'r', encoding=config.FILE_ENCODING) as f:
            videos = yaml.safe_load(f) or []
    return videos


def get_insight_from_video(videos):
    selected_item = get_selected_video(videos, "tab3")
    question = st.text_area(
        "Ask a question about the video",
        placeholder="What is the video about?",
        key="question_input"
    )
    if st.button("Get Answer"):
        if question:
            try:
                # Get the selected video's transcript
                transcripts = get_translated_transcripts(selected_item[0])

                # Get the answer from the transcript
                bedrock = BedrockHelper()

                full_answer = ""
                response_placeholder = st.empty()

                # Stream the response
                for response_chunk in bedrock.get_insight_stream(
                        model_alias="np",
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
        else:
            st.warning("Please enter a question")


def explore_summaries(videos):
    selected_item = get_selected_video(videos, "tab2")
    # Display summaries
    if selected_item:
        embed_youtube_player(selected_item[0])
        display_summary(selected_item[0], selected_item[1])


def summarize_new_video():
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
                                             default=["np"])
    with st.container():
        row2_col1, row2_col2 = st.columns(2)

        with row2_col1:
            # Language selection
            lang_options = ["en", "ko"]
            selected_lang = st.selectbox("Select Source Language", options=lang_options, index=0)

        with row2_col2:
            # AWS Region selection
            region_options = ["us-east-1"]
            region = st.selectbox("AWS Region", options=region_options, index=0)
    # Process button
    if st.button("Process Video"):
        if video_id:
            try:
                with st.spinner("Getting video title..."):
                    video_title = YouTubeHelper.get_video_title(video_id)

                with st.spinner("Downloading transcripts..."):
                    download_transcripts(video_id, selected_lang)

                with st.spinner("Translating transcripts..."):
                    translate_transcripts(video_id, selected_lang, 'ko', region=region)
                    transcripts = get_translated_transcripts(video_id)

                with st.spinner("Generating summaries..."):
                    process_model_summaries(
                        model_aliases=",".join(selected_models).split(","),
                        transcripts=transcripts,
                        video_id=video_id
                    )

                add_to_videos(video_id, video_title)

                # Display results
                st.success("Processing completed successfully!")

                # Display summaries
                display_summary(video_id, video_title)

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
        else:
            st.warning("Please enter a YouTube Video ID")


def convert_to_list(videos):
    items = {video['video_id']: video['title'] for video in videos}
    video_options = list(items.items())
    return video_options


# for command line
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