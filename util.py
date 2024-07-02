import re
import os


def remove_not_allowed_chars(text):
    # chinese and english characters are allowed
    return re.sub(r"[^\u4e00-\u9fffA-Za-z]", "", text)


def add_poppler_to_path():
    poppler_relative_path = "poppler-24.02.0/Library/bin"
    poppler_path = os.path.abspath(poppler_relative_path)

    print(poppler_path)

    # Get the current PATH variable
    current_path = os.environ.get("PATH", "")

    # Append the Poppler path to the current PATH variable
    updated_path = f"{current_path};{poppler_path}"

    # Update the PATH variable
    os.environ["PATH"] = updated_path


def create_docs_folder():
    if not os.path.exists("docs"):
        os.makedirs("docs")
