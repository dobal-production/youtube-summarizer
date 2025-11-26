import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
import re


class I18nManager:
    """
    Manages internationalization for multi-language applications.

    This class loads language-specific label files and provides methods
    to retrieve localized text based on the current language setting.
    """

    def __init__(self, labels_dir: str = None, default_language: str = 'en-US'):
        """
        Initialize the I18n Manager.

        Args:
            labels_dir (str): Directory containing label files.
                            Defaults to '../labels' relative to this file.
            default_language (str): Default language code. Defaults to 'en'.
        """
        if labels_dir is None:
            # Default to labels directory relative to this file
            current_dir = Path(__file__).parent
            labels_dir = current_dir.parent / 'labels'

        # Security: Validate and sanitize the labels directory path
        self.labels_dir = self._validate_labels_dir(labels_dir)
        
        # Security: Validate language code format
        self.default_language = self._validate_language_code(default_language)
        self.current_language = self.default_language
        self.labels_cache: Dict[str, Dict[str, Any]] = {}

        # Load available languages
        self._discover_languages()

        # Load default language
        self._load_language(self.default_language)

    def _validate_labels_dir(self, labels_dir: str) -> Path:
        """
        Validate and sanitize the labels directory path to prevent path traversal attacks.
        
        Args:
            labels_dir (str): Directory path to validate
            
        Returns:
            Path: Validated and resolved path
            
        Raises:
            ValueError: If path is invalid or potentially dangerous
        """
        try:
            path = Path(labels_dir).resolve()
            
            # Security: Ensure the path doesn't contain dangerous patterns
            path_str = str(path)
            if '..' in path_str or path_str.startswith('/etc') or path_str.startswith('/proc'):
                raise ValueError(f"Potentially dangerous path detected: {labels_dir}")
            
            # Security: Ensure it's a directory and exists (or can be created)
            if path.exists() and not path.is_dir():
                raise ValueError(f"Path is not a directory: {labels_dir}")
                
            return path
            
        except Exception as e:
            raise ValueError(f"Invalid labels directory path: {labels_dir}. Error: {str(e)}")

    def _validate_language_code(self, language_code: str) -> str:
        """
        Validate language code format to prevent injection attacks.
        
        Args:
            language_code (str): Language code to validate
            
        Returns:
            str: Validated language code
            
        Raises:
            ValueError: If language code format is invalid
        """
        # Security: Only allow alphanumeric characters, hyphens, and underscores
        if not re.match(r'^[a-zA-Z0-9_-]+$', language_code):
            raise ValueError(f"Invalid language code format: {language_code}")
        
        # Security: Limit length to prevent buffer overflow-like issues
        if len(language_code) > 10:
            raise ValueError(f"Language code too long: {language_code}")
            
        return language_code

    def _discover_languages(self) -> None:
        """Discover available language files in the labels directory."""
        self.available_languages = []

        if not self.labels_dir.exists():
            raise FileNotFoundError(f"Labels directory not found: {self.labels_dir}")

        for file_path in self.labels_dir.glob("label-*.yaml"):
            # Extract language code from filename (e.g., "label-en-US.yaml" -> "en")
            lang_code = file_path.stem.replace("label-", "")
            self.available_languages.append(lang_code)

        if not self.available_languages:
            raise ValueError(f"No label files found in {self.labels_dir}")

        print(f"Available languages: {', '.join(self.available_languages)}")

    def _load_language(self, language_code: str) -> None:
        """
        Load labels for a specific language.

        Args:
            language_code (str): Language code to load (e.g., 'en-US', 'ko-KR')
        """
        # Security: Validate language code before processing
        language_code = self._validate_language_code(language_code)
        
        if language_code in self.labels_cache:
            return

        label_file = self.labels_dir / f"label-{language_code}.yaml"
        
        # Security: Ensure the file is within the labels directory
        try:
            label_file = label_file.resolve()
            if not str(label_file).startswith(str(self.labels_dir.resolve())):
                raise ValueError(f"File path outside labels directory: {label_file}")
        except Exception as e:
            raise ValueError(f"Invalid file path: {e}")

        if not label_file.exists():
            if language_code != self.default_language:
                print(f"Warning: Label file not found for '{language_code}', using default language '{self.default_language}'")
                return
            else:
                raise FileNotFoundError(f"Default language file not found")

        try:
            # Security: Limit file size to prevent DoS attacks (5MB limit)
            file_size = label_file.stat().st_size
            if file_size > 5 * 1024 * 1024:  # 5MB
                raise ValueError(f"Label file too large: {file_size} bytes")
                
            with open(label_file, 'r', encoding='utf-8') as file:
                # Security: Use safe_load to prevent code execution
                content = yaml.safe_load(file)
                self.labels_cache[language_code] = content or {}
                print(f"Loaded labels for language: {language_code}")
        except yaml.YAMLError as e:
            raise Exception(f"Invalid YAML format in label file: {str(e)}")
        except Exception as e:
            raise Exception(f"Error loading label file: {str(e)}")

    def set_language(self, language_code: str) -> None:
        """
        Set the current language.

        Args:
            language_code (str): Language code to set as current
        """
        # Security: Validate language code
        try:
            language_code = self._validate_language_code(language_code)
        except ValueError as e:
            print(f"Warning: Invalid language code: {e}")
            return
            
        if language_code not in self.available_languages:
            print(f"Warning: Language '{language_code}' not available. Available: {', '.join(self.available_languages)}")
            return

        self.current_language = language_code
        self._load_language(language_code)
        print(f"Language set to: {language_code}")

    def get_label(self, key: str, language: str = None, default: str = None) -> str:
        """
        Get a localized label by key with full YAML depth support.

        Args:
            key (str): Dot-separated key path (e.g., 'app.title', 'buttons.primary.submit', 'forms.user.validation.email.required')
            language (str): Specific language code. Uses current language if None.
            default (str): Default value if key not found. Uses key if None.

        Returns:
            str: Localized label text
        """
        target_language = language or self.current_language

        # Ensure language is loaded
        self._load_language(target_language)

        # Get labels for target language, fallback to default language
        labels = self.labels_cache.get(target_language) or self.labels_cache.get(self.default_language, {})

        # Navigate through nested dictionary using dot notation with unlimited depth
        keys = key.split('.')
        value = labels

        try:
            for k in keys:
                if not isinstance(value, dict):
                    raise TypeError(f"Cannot navigate further: '{k}' in path '{key}' - parent is not a dictionary")
                value = value[k]
            
            # Ensure we return a string value, not a nested dictionary
            if isinstance(value, dict):
                raise TypeError(f"Key '{key}' points to a dictionary, not a string value")
            
            return str(value)
        except (KeyError, TypeError) as e:
            # Fallback to default language if not found in target language
            if target_language != self.default_language:
                return self.get_label(key, self.default_language, default)

            # Return default value or key if not found
            return default or key

    def get_labels_section(self, section: str, language: str = None) -> Dict[str, Any]:
        """
        Get all labels from a specific section with full depth support.

        Args:
            section (str): Dot-separated section path (e.g., 'buttons', 'forms.user', 'app.settings.theme')
            language (str): Specific language code. Uses current language if None.

        Returns:
            Dict[str, Any]: Dictionary containing all labels in the section
        """
        target_language = language or self.current_language
        self._load_language(target_language)

        labels = self.labels_cache.get(target_language) or self.labels_cache.get(self.default_language, {})
        
        # Navigate through nested dictionary using dot notation
        keys = section.split('.')
        value = labels

        try:
            for k in keys:
                if not isinstance(value, dict):
                    return {}
                value = value[k]
            
            # Return the nested dictionary or empty dict if not found
            return value if isinstance(value, dict) else {}
        except (KeyError, TypeError):
            # Fallback to default language if not found in target language
            if target_language != self.default_language:
                return self.get_labels_section(section, self.default_language)
            return {}

    def get_nested_value(self, key: str, language: str = None) -> Any:
        """
        Get a nested value (can be string, dict, list, etc.) by key path.

        Args:
            key (str): Dot-separated key path
            language (str): Specific language code. Uses current language if None.

        Returns:
            Any: The value at the specified path (string, dict, list, etc.)
        """
        target_language = language or self.current_language
        self._load_language(target_language)

        labels = self.labels_cache.get(target_language) or self.labels_cache.get(self.default_language, {})
        
        # Navigate through nested dictionary using dot notation
        keys = key.split('.')
        value = labels

        try:
            for k in keys:
                if not isinstance(value, dict):
                    raise TypeError(f"Cannot navigate further: '{k}' in path '{key}'")
                value = value[k]
            return value
        except (KeyError, TypeError):
            # Fallback to default language if not found in target language
            if target_language != self.default_language:
                return self.get_nested_value(key, self.default_language)
            return None

    def get_current_language(self) -> str:
        """Get the current language code."""
        return self.current_language

    def get_available_languages(self) -> list:
        """Get list of available language codes."""
        return self.available_languages.copy()

    def has_key(self, key: str, language: str = None) -> bool:
        """
        Check if a key exists in the labels.

        Args:
            key (str): Dot-separated key path
            language (str): Specific language code. Uses current language if None.

        Returns:
            bool: True if key exists, False otherwise
        """
        target_language = language or self.current_language
        self._load_language(target_language)

        labels = self.labels_cache.get(target_language) or self.labels_cache.get(self.default_language, {})
        
        keys = key.split('.')
        value = labels

        try:
            for k in keys:
                if not isinstance(value, dict):
                    return False
                value = value[k]
            return True
        except (KeyError, TypeError):
            # Check in default language if not found in target language
            if target_language != self.default_language:
                return self.has_key(key, self.default_language)
            return False

    def get_all_keys(self, prefix: str = "", language: str = None) -> list:
        """
        Get all available keys with optional prefix filter.

        Args:
            prefix (str): Key prefix to filter by (e.g., 'app', 'buttons.primary')
            language (str): Specific language code. Uses current language if None.

        Returns:
            list: List of all matching keys
        """
        target_language = language or self.current_language
        self._load_language(target_language)

        labels = self.labels_cache.get(target_language) or self.labels_cache.get(self.default_language, {})
        
        def _get_keys(obj, current_prefix=""):
            keys = []
            if isinstance(obj, dict):
                for key, value in obj.items():
                    new_prefix = f"{current_prefix}.{key}" if current_prefix else key
                    if isinstance(value, dict):
                        keys.extend(_get_keys(value, new_prefix))
                    else:
                        keys.append(new_prefix)
            return keys

        all_keys = _get_keys(labels)
        
        if prefix:
            return [key for key in all_keys if key.startswith(prefix)]
        return all_keys

    def format_label(self, key: str, **kwargs) -> str:
        """
        Get a label and format it with provided arguments.

        Args:
            key (str): Label key
            **kwargs: Arguments for string formatting

        Returns:
            str: Formatted label text
        """
        label = self.get_label(key)
        try:
            return label.format(**kwargs)
        except (KeyError, ValueError) as e:
            # Security: Don't expose detailed error information
            print(f"Warning: Error formatting label")
            return label


# Convenience function to create a global instance
_global_i18n = None

def get_i18n_manager(labels_dir: str = None, default_language: str = 'en-US') -> I18nManager:
    """
    Get or create a global I18nManager instance.

    Args:
        labels_dir (str): Directory containing label files
        default_language (str): Default language code

    Returns:
        I18nManager: Global I18nManager instance
    """
    global _global_i18n
    if _global_i18n is None:
        _global_i18n = I18nManager(labels_dir, default_language)
    return _global_i18n


# Convenience functions for easy access
def t(key: str, **kwargs) -> str:
    """
    Translate function - shorthand for getting labels.

    Args:
        key (str): Label key
        **kwargs: Arguments for string formatting

    Returns:
        str: Translated and formatted text
    """
    i18n = get_i18n_manager()
    if kwargs:
        return i18n.format_label(key, **kwargs)
    return i18n.get_label(key)


def set_language(language_code: str) -> None:
    """
    Set the current language - convenience function.

    Args:
        language_code (str): Language code to set
    """
    i18n = get_i18n_manager()
    i18n.set_language(language_code)
