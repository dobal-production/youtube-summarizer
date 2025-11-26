# YouTube 비디오 요약 및 분석 with AWS Bedrock

AWS Bedrock 언어 모델과 YouTube API를 활용하여 비디오 자막을 요약하고 분석하는 Streamlit 기반 애플리케이션입니다. 자막 번역, 비디오 요약, 질의응답 기능을 제공합니다.

이 애플리케이션은 사용자가 YouTube 비디오의 내용을 빠르게 이해할 수 있도록 설계되었으며, 특히 AWS 이벤트 및 컨퍼런스 관련 비디오에 최적화되어 있습니다. AWS Bedrock, Translate, ECR 등 다양한 AWS 서비스를 활용하여 비디오 자막을 효율적으로 처리하고 분석합니다.

## 주요 기능

- **자막 다운로드**: YouTube API를 통한 자동 자막 추출
- **다국어 번역**: AWS Translate를 활용한 자막 번역 (영어 ↔ 한국어)
- **AI 요약**: 여러 AWS Bedrock 모델을 사용한 비디오 내용 요약
- **질의응답**: 비디오 내용 기반 AI 질의응답
- **비디오 관리**: 카테고리별 비디오 분류 및 관리
- **스트리밍 응답**: 실시간 AI 응답 스트리밍

## 프로젝트 구조

```
.
├── src/
│   ├── app.py                      # Streamlit 애플리케이션 메인 진입점
│   ├── app_config.py               # 애플리케이션 설정 상수
│   ├── config.py                   # 환경 변수 기반 설정
│   ├── video.py                    # Video 데이터 클래스
│   ├── admin.py                    # 관리자 기능
│   ├── language_detection.py      # 브라우저 언어 감지
│   ├── utils/
│   │   ├── youtube_utils.py       # YouTube API 유틸리티
│   │   ├── bedrock_utils.py       # AWS Bedrock 유틸리티
│   │   └── i18n_manager.py        # 다국어 지원 매니저
│   ├── labels/
│   │   ├── label-ko.yaml          # 한국어 레이블
│   │   └── label-en-US.yaml       # 영어 레이블
│   ├── data/                       # 자막 및 요약 데이터 저장
│   ├── meta/
│   │   ├── videos.yaml            # 비디오 목록
│   │   └── categories.yaml        # 카테고리 목록
│   ├── logs/                       # 로그 파일
│   ├── Dockerfile                  # Docker 컨테이너 설정
│   ├── docker-build.sh            # Docker 빌드 스크립트
│   ├── run.sh                     # 로컬 실행 스크립트
│   └── requirements.txt           # Python 의존성
└── README.md
```

### 주요 파일 설명

- **app.py**: Streamlit 기반 웹 애플리케이션의 메인 로직
- **youtube_utils.py**: YouTube 비디오 정보 및 자막 추출 기능
- **bedrock_utils.py**: AWS Bedrock 모델을 통한 요약 및 질의응답 처리
- **video.py**: 비디오 정보를 담는 데이터 클래스
- **Dockerfile**: 애플리케이션 컨테이너화 설정

### 통합 서비스

- **YouTube API**: 비디오 자막 및 메타데이터 추출
- **AWS Bedrock**: 다양한 LLM 모델을 통한 요약 및 분석
  - Claude 4 Sonnet
  - Claude 3.7 Sonnet
  - Claude 3.5 Sonnet v2
  - Amazon Nova (Pro, Lite, Micro)
  - Claude 3.5 Haiku
  - Titan Text G1 Express
- **AWS Translate**: 자막 번역 서비스
- **Amazon ECR**: Docker 이미지 저장소
- **Amazon S3**: 자막 파일 저장

## 설치 및 실행

### 사전 요구사항

- Python 3.9 이상
- Docker (컨테이너 배포 시)
- AWS CLI (적절한 권한으로 구성)
- YouTube API 키
- AWS Bedrock 접근 권한

### 로컬 설치

1. 저장소 클론
```bash
git clone <repository-url>
cd <project-directory>
```

2. 가상 환경 생성 및 활성화
```bash
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

3. 의존성 설치
```bash
pip install -r src/requirements.txt
```

4. 환경 변수 설정
```bash
cd src
cp .env.dev .env
# .env 파일을 편집하여 필요한 설정 입력
```

5. 애플리케이션 실행
```bash
./run.sh
# 또는
streamlit run app.py --server.port 8051
```

6. 브라우저에서 접속
```
http://localhost:8051
```

### 환경 변수 설정

`.env` 파일에 다음 항목을 설정하세요:

```env
STORAGE_TYPE=local
META_DIR=meta
DATA_DIR=data
LOG_DIR=logs
S3_BUCKET_NAME=your-bucket-name
AWS_REGION=us-east-1
YOUTUBE_API_KEY=your-youtube-api-key
```

## 사용 방법

### 1. 새 비디오 요약 생성

1. **New Summary** 탭 선택
2. YouTube 비디오 URL 입력
3. 카테고리 선택
4. 사용할 Bedrock 모델 선택 (다중 선택 가능)
5. AWS 리전 선택
6. 원본 언어 및 번역 옵션 설정
7. **Summarize** 버튼 클릭

애플리케이션이 자동으로:
- 비디오 자막 다운로드
- 필요시 번역 수행
- 선택한 모델들로 요약 생성
- S3에 자막 저장
- 비디오 목록에 추가

### 2. 요약 탐색

1. **Explore Summaries** 탭 선택
2. 카테고리 선택
3. 비디오 선택
4. 비디오 플레이어 및 요약 내용 확인
5. 자막 파일 다운로드 (원본/번역본)

### 3. 질의응답

1. **Explore Summaries** 탭에서 비디오 선택
2. 사용할 모델 선택
3. 질문 입력
4. **Get Answer** 버튼 클릭
5. 실시간 스트리밍 응답 확인

### 4. 비디오 관리

**Management** 탭에서:
- 비디오 목록 관리
- 카테고리 관리
- 메타데이터 편집

## Docker 배포

### Docker 이미지 빌드 및 푸시

```bash
cd src
chmod +x docker-build.sh
./docker-build.sh
```

스크립트는 자동으로:
1. AWS 계정 정보 확인
2. ECR 로그인
3. Docker 이미지 빌드
4. 타임스탬프 태그 생성
5. ECR에 이미지 푸시

### 수동 Docker 실행

```bash
docker build -t youtube-summarizer .
docker run -p 80:80 \
  -e AWS_REGION=us-east-1 \
  -e YOUTUBE_API_KEY=your-key \
  youtube-summarizer
```

### ECS/EKS 배포

1. ECR에서 이미지 URI 확인
2. 태스크 정의 또는 Deployment 생성
3. 환경 변수 설정
4. 서비스 배포

## 데이터 흐름

```
[사용자] 
   ↓
[Streamlit UI]
   ↓
[YouTube API] → 자막 추출
   ↓
[AWS Translate] → 번역 (선택사항)
   ↓
[AWS Bedrock] → 요약/질의응답
   ↓
[로컬 저장소/S3] → 캐싱
   ↓
[Streamlit UI] → 결과 표시
```

### 파일 저장 구조

```
data/
├── {video_id}.txt          # 원본 자막
├── {video_id}_ko.txt       # 번역된 자막
└── {video_id}.md           # 요약 내용

meta/
├── videos.yaml             # 비디오 목록
└── categories.yaml         # 카테고리 목록

logs/
└── response_usage_*.json   # API 사용량 로그
```

## 지원 모델

AWS Bedrock을 통해 다음 모델들을 사용할 수 있습니다:

| 모델 별칭 | 모델명 | Model ID |
|---------|--------|----------|
| s4 | Claude 4 Sonnet | us.anthropic.claude-sonnet-4-20250514-v1:0 |
| s37 | Claude 3.7 Sonnet | us.anthropic.claude-3-7-sonnet-20250219-v1:0 |
| s35v2 | Claude 3.5 Sonnet v2 | us.anthropic.claude-3-5-sonnet-20241022-v2:0 |
| np | Nova Pro | us.amazon.nova-pro-v1:0 |
| nl | Nova Lite | us.amazon.nova-lite-v1:0 |
| nm | Nova Micro | us.amazon.nova-micro-v1:0 |
| s35 | Claude 3.5 Sonnet | us.anthropic.claude-3-5-sonnet-20240620-v1:0 |
| h35 | Claude 3.5 Haiku | us.anthropic.claude-3-5-haiku-20241022-v1:0 |
| h3 | Claude 3 Haiku | anthropic.claude-3-haiku-20240307-v1:0 |
| c21 | Claude 2.1 | anthropic.claude-v2:1 |
| tg1e | Titan Text G1 Express | amazon.titan-text-express-v1 |

## 문제 해결

### AWS Bedrock 접근 오류

**증상**: `AccessDeniedException: User is not authorized to perform bedrock:InvokeModel`

**해결 방법**:
1. IAM 사용자/역할에 Bedrock 권한 확인
2. `app_config.py`에서 올바른 AWS 리전 설정 확인
3. AWS 계정에서 Bedrock 서비스 활성화 확인
4. 사용하려는 모델에 대한 접근 권한 확인

### YouTube 자막 추출 실패

**증상**: `TranscriptsDisabled: Subtitles are disabled for this video`

**해결 방법**:
1. 비디오에 자막이 있는지 확인
2. YouTube API 할당량 제한 확인
3. `app_config.py`의 YouTube API 키 확인
4. 비디오가 공개 상태인지 확인

### Streamlit 앱 시작 실패

**증상**: `ModuleNotFoundError: No module named 'streamlit'`

**해결 방법**:
1. 가상 환경이 활성화되어 있는지 확인
2. 의존성 재설치: `pip install -r requirements.txt`
3. Python 버전 확인 (3.9 이상 필요)
4. `PYTHONPATH` 환경 변수 확인

### 번역 오류

**증상**: AWS Translate 호출 실패

**해결 방법**:
1. AWS 자격 증명 확인
2. Translate 서비스 권한 확인
3. 지원되는 언어 코드 사용 확인 (en, ko 등)
4. 파일 인코딩 확인 (UTF-8)

### Docker 빌드 오류

**증상**: Docker 이미지 빌드 또는 푸시 실패

**해결 방법**:
1. Docker 데몬이 실행 중인지 확인
2. AWS CLI 자격 증명 확인
3. ECR 저장소 존재 확인
4. 네트워크 연결 확인

## 디버깅

### 로깅 레벨 변경

`app.py`의 `setup_logging()` 함수 수정:

```python
def setup_logging():
    logging.basicConfig(
        level=logging.DEBUG,  # INFO에서 DEBUG로 변경
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)
```

### Bedrock 호출 추적

`bedrock_utils.py`에서 상세 로그 확인:
- 입력/출력 토큰 수
- 응답 시간
- 모델 ID

로그 파일 위치: `logs/response_usage_*.json`

### API 사용량 모니터링

```bash
# 로그 파일 확인
cat logs/response_usage_*.json | jq .

# 총 토큰 사용량 계산
cat logs/response_usage_*.json | jq '.totalTokens' | awk '{sum+=$1} END {print sum}'
```

## 개발 가이드

### 새 모델 추가

`src/utils/bedrock_utils.py`의 `MODEL_ALIASES`에 추가:

```python
MODEL_ALIASES = {
    "new_model": {
        "name": "New Model Name",
        "model_id": "model-id-from-bedrock"
    },
    # ... 기존 모델들
}
```

### 새 언어 지원 추가

1. `src/labels/` 디렉토리에 새 레이블 파일 생성 (예: `label-ja.yaml`)
2. `src/utils/i18n_manager.py`에서 언어 코드 추가
3. AWS Translate에서 지원하는 언어 코드 확인

### 커스텀 프롬프트 작성

`src/utils/bedrock_utils.py`의 프롬프트 메서드 수정:
- `__generate_summary_prompt()`: 요약 프롬프트
- `__generate_insights_prompt()`: 질의응답 프롬프트
- `__generate_translate_prompt()`: 번역 프롬프트

## 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 기여

기여를 환영합니다! Pull Request를 제출하거나 Issue를 등록해 주세요.

## 문의

프로젝트 관련 문의사항이 있으시면 Issue를 통해 연락해 주세요.
