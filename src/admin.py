import streamlit as st
import yaml
import app_config as config
from pathlib import Path
from video import Video
from dataclasses import asdict

METAFILE_PATH = config.META_DIR + "/categories.yaml"
VIDEOS_PATH = str(Path(config.META_DIR) / "videos.yaml")


def load_categories():
    try:
        with open(METAFILE_PATH, 'r') as file:
            categories = yaml.safe_load(file)
            return categories if categories else []
    except FileNotFoundError:
        return []


def load_videos():
    try:
        with open(VIDEOS_PATH, 'r', encoding=config.FILE_ENCODING) as f:
            videos_data = yaml.safe_load(f)
            if videos_data:
                return [Video(video_id=v['video_id'], title=v['title'], category=v['category']) for v in videos_data]
    except FileNotFoundError:
        pass
    return []


def save_videos(videos):
    try:
        with open(VIDEOS_PATH, 'w', encoding=config.FILE_ENCODING) as f:
            yaml.dump(
                [asdict(video) for video in videos],
                f,
                default_flow_style=False,
                sort_keys=False,
                allow_unicode=True
            )
        return True, "Videos updated successfully!"
    except Exception as e:
        return False, f"Error saving videos: {str(e)}"


def delete_videos_by_category(category, video_ids=None):
    videos = load_videos()
    initial_count = len(videos)

    if video_ids:
        # Delete specific videos
        videos = [v for v in videos if not (v.category == category and v.video_id in video_ids)]
    else:
        # Delete all videos in category
        videos = [v for v in videos if v.category != category]

    if len(videos) == initial_count:
        return False, f"No videos found to delete in category '{category}'"

    success, message = save_videos(videos)
    if success:
        deleted_count = initial_count - len(videos)
        if video_ids:
            return True, f"Deleted {deleted_count} selected videos from category '{category}'"
        else:
            return True, f"Deleted {deleted_count} videos from category '{category}'"
    return False, message


def move_videos_between_categories(source_category, target_category, video_ids=None):
    if source_category == target_category:
        return False, "Source and target categories are the same"

    videos = load_videos()
    moved_count = 0

    for video in videos:
        # If video_ids is provided, only move those specific videos
        # Otherwise move all videos in the source category
        if video.category == source_category and (video_ids is None or video.video_id in video_ids):
            video.category = target_category
            moved_count += 1

    if moved_count == 0:
        return False, f"No videos found to move from '{source_category}'"

    success, message = save_videos(videos)
    if success:
        return True, f"Moved {moved_count} videos from '{source_category}' to '{target_category}'"
    return False, message


def save_category(new_category):
    categories = load_categories()

    # Check if category already exists
    if new_category in categories:
        return False, "Category already exists!"

    # Add new category
    categories.append(new_category)

    # Sort categories alphabetically
    categories.sort()

    # Save to file
    try:
        with open(METAFILE_PATH, 'w') as file:
            yaml.safe_dump(categories, file, allow_unicode=True)
        return True, "Category added successfully!"
    except Exception as e:
        return False, f"Error saving category: {str(e)}"


def main():
    st.header("Category & Video Management")

    # Load categories
    categories = load_categories()

    # Create tabs for different operations
    tab1, tab2, tab3 = st.tabs(["Add Category", "Remove Videos", "Move Videos"])

    with tab1:
        display_category_management(categories)

    with tab2:
        display_remove_videos(categories)

    with tab3:
        display_move_vidoes(categories)


def display_move_vidoes(categories):
    st.subheader("Move Videos Between Categories")
    if len(categories) >= 2:
        col1, col2 = st.columns(2)

        with col1:
            source_category = st.selectbox(
                "Source Category",
                options=categories,
                key="source_category"
            )

        with col2:
            # Filter out source category from target options
            target_options = [c for c in categories if c != source_category]
            target_category = st.selectbox(
                "Target Category",
                options=target_options,
                key="target_category"
            )

        # Get videos in source category
        videos = load_videos()
        source_videos = [v for v in videos if v.category == source_category]

        if source_videos:
            st.write("Select videos to move:")
            selected_videos = []

            # Create checkboxes for each video
            for video in source_videos:
                if st.checkbox(video.title, key=f"move_{video.video_id}"):
                    selected_videos.append(video.video_id)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Move Selected Videos"):
                    if selected_videos:
                        success, message = move_videos_between_categories(
                            source_category,
                            target_category,
                            video_ids=selected_videos
                        )
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.warning("Please select at least one video to move")

            with col2:
                if st.button("Move All Videos"):
                    success, message = move_videos_between_categories(source_category, target_category)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
        else:
            st.warning(f"No videos found in category '{source_category}'")
    else:
        st.warning("Need at least 2 categories to move videos between them")


def display_remove_videos(categories):
    if categories:
        category_to_delete = st.selectbox(
            "Select category to delete videos from",
            options=categories,
            key="delete_category"
        )

        # Get videos in selected category
        videos = load_videos()
        category_videos = [v for v in videos if v.category == category_to_delete]

        if category_videos:
            st.write("Select videos to delete:")
            selected_videos = []

            # Create a multiselect box for videos
            selected_video_titles = st.multiselect(
                "Select videos",
                options=[v.title for v in category_videos],
                key="delete_video_selection"
            )

            # Map selected titles back to video IDs
            selected_videos = [v.video_id for v in category_videos if v.title in selected_video_titles]

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Delete Selected Videos"):
                    if selected_videos:
                        try:
                            success, message = delete_videos_by_category(category_to_delete, selected_videos)
                            if success:
                                st.success(message)
                                # st.experimental_rerun()
                                st.rerun()
                            else:
                                st.error(message)
                        except Exception as e:
                            st.error(f"Error deleting videos: {str(e)}")
                    else:
                        st.warning("Please select at least one video to delete")

            with col2:
                if st.button("Delete All Videos"):
                    if st.session_state.get('confirm_delete_all', False):
                        success, message = delete_videos_by_category(category_to_delete)
                        if success:
                            st.success(message)
                            st.session_state['confirm_delete_all'] = False
                        else:
                            st.error(message)
                    else:
                        st.warning(f"Are you sure you want to delete all videos in category '{category_to_delete}'?")
                        if st.button("Yes, Delete All"):
                            st.session_state['confirm_delete_all'] = True
        else:
            st.warning(f"No videos found in category '{category_to_delete}'")
    else:
        st.warning("No categories available")


def display_category_management(categories):
    st.subheader("Add New Category")
    new_category = st.text_input("Enter new category:")
    if st.button("Add Category"):
        if new_category.strip():
            success, message = save_category(new_category.strip())
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning("Please enter a category name!")
    # Display current categories
    st.subheader("Current Categories:")
    if categories:
        st.text_area("Categories", "\n".join(categories), height=len(categories) * 20)


if __name__ == "__main__":
    main()
