import os
from dotenv import load_dotenv

env_file = ".env.dev" if os.getenv("ENV", "dev").lower() == "dev" else ".env.prod"
load_dotenv(dotenv_path=env_file)

print(env_file)

class Config:
    STORAGE_TYPE = os.getenv("STORAGE_TYPE")
    META_DIR = os.getenv("META_DIR")
    DATA_DIR = os.getenv("DATA_DIR")
    LOG_DIR = os.getenv("LOG_DIR")
    S3_BUCKET_NAME = os.getenv("S3_BUCKET_NAME")
    AWS_REGION = os.getenv("AWS_REGION")
    FILE_ENCODING = "utf-8"
    DEFAULT_MAX_TOKENS = 4096
    DEFAULT_REGION = "us-east-1"
    FILTER_WORDS = ["[Music]", "[Applause]", "[Laughter]", "[음악]", "[박수]", "[웃음]"]
