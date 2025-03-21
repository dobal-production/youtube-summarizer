
## Nova Pro
### 제너레이티브 AI의 새로운 위험과 도전
* 제너레이티브 AI는 기존의 기계 학습과 비교하여 새로운 위험과 도전을 제시한다.
* 환각(hallucinations)과 같은 문제는 여전히 존재하며, 품질 문제도 중요하다.
* 변호사가 사례법을 검색할 때 제너레이티브 도구를 사용하면 환각이 발생할 수 있다.
* 챗봇이 정책을 잘못 해석하면 사용자가 잘못된 가정을 하거나 실수를 할 수 있다.
* 의료 요약의 AI 전사에서 환각이 발생하면 위험할 수 있다.

### 책임 있는 AI
* 책임 있는 AI는 여러 상호 관련된 관심사로 정의할 수 있다.
* 8가지 기둥: 제어 가능성, 프라이버시 및 보안, 안전성, 독성, 편향 및 공정성, 진실성, 견고성, 설명 가능성, 투명성, 거버넌스.
* 지속 가능성은 별도의 AWS 차원의 관심사로 취급된다.

### AI 위험 평가
* 규제(예: EU AI Act)는 위험을 먼저 고려한다.
* 조직에서 위험 평가 능력을 구축하는 것이 중요하다.
* AWS는 위험 평가 프로세스를 고객에게 조언하고 지원한다.

### 편향 및 공정성
* 편향 평가는 기술적으로 해결된 문제이지만, 여러 가지 추가 고려 사항이 있다.
* Amazon SageMaker Clarify는 21가지 편향 측정 지표를 지원한다.
* 제너레이티브 AI의 경우, 언어의 공정성 외에도 결과 기반 평가를 고려해야 한다.

### 설명 가능성
* 설명 가능성은 기계 학습 모델이 결과에 도달한 방식을 이해하는 것이다.
* SageMaker Clarify는 전통적인 기계 학습과 제너레이티브 시스템 모두에 대한 설명 가능성을 지원한다.
* 제너레이티브 AI의 경우, 설명 가능성은 여전히 연구 중인 분야이다.

### 제어 가능성
* AI 시스템을 모니터링하고 관찰 가능성을 확보해야 한다.
* Bedrock agents를 통해 사용자가 특정 작업을 허용하거나 거부할 수 있다.

### 프라이버시 및 보안
* AWS Bedrock은 사용자 데이터를 사용하여 모델을 개선하지 않으며, 프롬프트와 완성을 저장하지 않는다.
* 사용자는 데이터를 자체적으로 저장하고 관리할 수 있다.
* 암호화, 액세스 관리, CloudWatch를 통한 사용 추적 등 다양한 보안 기능이 제공된다.

### 견고성
* 작은 입력 변화가 출력에 큰 변화를 일으키지 않도록 하는 것이 중요하다.
* 모델에는 이미 여러 가지 보호 기능이 내장되어 있다.
* Amazon Bedrock Guardrails를 통해 사용자 지정 가드레일을 구성할 수 있다.

### 투명성
* 생성된 콘텐츠가 AI에 의해 생성되었음을 알 수 있도록 하는 것이 중요하다.
* Amazon은 C2PA 운영 위원회에 참여하고, 이미지 생성 모델에 보이지 않는 워터마크를 포함시킨다.
* AWS 서비스 카드를 통해 모델의 훈련 방식, 벤치마크, 사용 목적 등에 대한 정보를 제공한다.

### Cisco의 책임 있는 AI 여정
* Cisco는 ChatGPT 출시 후 제너레이티브 AI 모델과 제품에 대한 접근을 제한하고 내부 프로세스와 워크플로를 개발했다.
* 책임 있는 AI 프로그램은 사용자와 직원을 AI에 안전하고 안전하게 연결하는 다리와 같다.
* 모델, 벤더 평가, 최종 사용 사례에 대한 세 가지 주요 평가를 진행한다.
* 투명성 노트를 통해 고객에게 데이터 흐름과 처리 방식에 대한 정보를 제공한다.

### 자동화된 추론 검사
* 명시적 추론을 사용하여 언어 모델의 완성을 검증하는 산업 최초의 제품이다.
* 자연어로 정책을 정의하고, 이를 명시적 규칙으로 변환하여 완성을 검증한다.
* 현재 이 기능은 게이트드 프리뷰로 제공되며, 액세스 요청이 필요할 수 있다.


## Cloaude 3.5 Sonnet v2
### AWS의 책임있는 AI 접근 방식
* AWS는 AI/ML 전문가들을 통해 고객들의 AI/ML 애플리케이션 구축을 지원하고 있다.
* 책임있는 AI를 위해 과학적, 공학적 관점에서 접근하며 ISO와 유럽 표준화 작업에도 참여하고 있다.
* 생성형 AI의 주요 위험 요소로는 환각(hallucination), 사실 정확성, 지적재산권, 데이터 프라이버시, 유해성 등이 있다.

### AWS의 책임있는 AI 8대 원칙
* 제어가능성, 프라이버시/보안, 안전성, 편향성/공정성, 정확성/견고성, 설명가능성, 투명성, 거버넌스의 8가지 원칙을 중심으로 접근한다.
* AI 리스크 평가를 통해 시스템의 위험도를 판단하고 적절한 대응 방안을 수립한다.
* SageMaker Clarify를 통해 21가지 편향성 지표를 측정하고 관리할 수 있다.

### Cisco의 책임있는 AI 여정
* ChatGPT 출시 이후 생성형 AI 접근을 제한하고 내부 프로세스와 워크플로우를 개발했다.
* AI 사용 사례를 3가지(제품/서비스, 내부 사용, 고객 제공)로 분류하여 관리한다.
* 모델 평가, 벤더 평가, 최종 사용 사례 평가의 3단계로 AI 시스템을 평가한다.
* 투명성 노트를 통해 고객들이 AI 기능의 데이터 흐름과 처리 방식을 이해할 수 있도록 한다.

### AWS의 자동화된 추론 검사
* 자연어로 작성된 정책을 명시적인 논리 규칙으로 변환하여 적용한다.
* 규칙 위반 시 위반 사유와 관련 규칙을 설명하는 형태의 설명가능성을 제공한다.
* 현재는 제한된 프리뷰로 제공되며 별도의 접근 권한이 필요하다.

