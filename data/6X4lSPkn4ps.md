
## Nova Pro
### 이벤트 주도 아키텍처의 기본 개념
* 이벤트 주도 아키텍처는 이벤트를 통해 서비스 간 비동기적으로 통신하는 방식이다.
* 이벤트 주도 아키텍처의 주요 요소로는 프로듀서, 컨슈머, 브로커 또는 버스, 이벤트가 있다.
* 프로듀서는 이벤트를 발행할 때 필요한 최소한의 데이터만 공유해야 한다.
* 컨슈머는 이벤트가 순서 없이 도착할 수 있으므로 이에 대응할 수 있어야 하며, 중복 처리를 위한 아이디엄 포텐시를 지원해야 한다.

### Amazon EventBridge 소개
* Amazon EventBridge는 이벤트 버스로, 서비스 간 이벤트를 쉽게 연결할 수 있게 한다.
* EventBridge는 기본 이벤트 버스, 사용자 정의 이벤트 버스, 파트너 이벤트 버스를 지원한다.
* EventBridge의 핵심은 이벤트 버스에 대한 필터링 및 라우팅 규칙으로, 이를 통해 이벤트를 특정 대상으로 전달하고 변환 또는 로직을 적용할 수 있다.

### 이벤트 구조화
* 이벤트는 고유 ID를 가지고, 필요한 데이터만 포함해야 한다.
* 이벤트는 메타데이터와 데이터 섹션으로 구분할 수 있다. 메타데이터에는 이벤트 ID, 이벤트 스키마 버전, 도메인, 이벤트 유형, TTL 등이 포함될 수 있다.
* 이벤트는 도메인 이벤트, 운영 이벤트, 로컬 내부 이벤트, 변환된 이벤트, AWS 이벤트로 분류할 수 있다.

### 이벤트 주도 패턴
* 코레오그래피와 오케스트레이션은 이벤트 주도 아키텍처에서 중요한 패턴이다.
* 코레오그래피는 이벤트에 반응하여 서비스가 자율적으로 작동하는 방식이다.
* 오케스트레이션은 중앙 컨트롤러가 서비스의 순서와 작업을 지시하는 방식이다.
* 함수 없는 통합 패턴은 불필요한 사용자 정의 함수를 작성하지 않고 네이티브 통합을 활용하는 방식이다.

### API 대상지
* API 대상지는 EventBridge 규칙의 대상으로 HTTP 엔드포인트를 지정하는 기능이다.
* API 대상지를 사용하면 외부 대상에 함수 없는 방식으로 이벤트를 전송할 수 있다.
* API 대상지는 기본 인증, API 키, OAuth 등 다양한 인증 방식을 지원한다.
* EventBridge는 API 대상지를 통한 비밀번호 관리 비용을 자동으로 처리한다.

### 회로 차단기 패턴
* 회로 차단기 패턴은 외부 서비스에 대한 요청이 실패할 때 대응하는 방식이다.
* 회로 차단기는 외부 서비스의 상태를 모니터링하고, 문제가 발생하면 요청을 차단하여 실패 응답을 반환한다.
* 회로 차단기는 상태 저장소를 통해 외부 서비스의 상태를 추적하고, 이를 기반으로 요청을 처리할지 여부를 결정한다.
* 회로 차단기는 실패한 요청을 아카이브에 저장하고, 외부 서비스가 복구되면 아카이브에서 이벤트를 재생할 수 있다.

### 오케스트레이션 패턴
* 오케스트레이션 패턴은 서비스 간 작업 흐름을 조정하는 방식이다.
* 오케스트레이션은 인-서비스, 크로스-서비스, 분산으로 구분할 수 있다.
* 분산 오케스트레이션은 여러 도메인에 걸쳐 복잡한 작업 흐름을 조정하는 방식이다.
* 분산 오케스트레이션에서는 작업 토큰을 사용하여 서비스 간 작업을 조정할 수 있다.

### 게이트키퍼 패턴
* 게이트키퍼 패턴은 도메인 또는 바운디드 컨텍스트 경계를 보호하는 방식이다.
* 게이트키퍼 버스는 내부 이벤트 버스와 외부 이벤트 버스를 분리하여 외부 통신을 관리한다.
* 게이트키퍼 버스는 도메인 이벤트를 외부로 전송하거나 다른 도메인과 이벤트를 공유하는 규칙을 포함한다.

### 자주 묻는 질문
* 이벤트 버스의 수는 기업 전체 버스, 도메인 버스, 바운디드 컨텍스트 버스 등 다양한 조합으로 설정할 수 있다.
* EventBridge와 Kinesis는 각각 다른 목적을 가지고 있으며, 유효한 사용 사례가 있는 경우에만 대체할 수 있다.
* SQS, SNS, EventBridge는 각각 큐잉, 퍼블리쉬-서브스크라이브 모델, 이벤트 조정을 위한 브로커 역할을 한다.


## Cloaude 3.5 Sonnet v2
### 이벤트 기반 아키텍처(EDA)의 기본
* 이벤트 기반 아키텍처는 이벤트를 통해 비동기 통신과 구현을 하는 아키텍처 개념이다.
* EDA의 4가지 주요 요소는 프로듀서(발행자), 컨슈머(소비자), 브로커/버스, 그리고 이벤트이다.
* 프로듀서는 컨슈머에 대해 독립적이어야 하며, 필요한 데이터만 공유해야 한다.
* 컨슈머는 이벤트가 순서대로 도착하지 않을 수 있음을 고려해야 하며, 동일한 이벤트가 여러 번 전달될 수 있는 상황에 대비해야 한다.

### Amazon EventBridge 소개
* EventBridge는 이벤트 버스로서 애플리케이션에서 이벤트를 발행자로부터 타겟으로 쉽게 연결할 수 있게 해준다.
* EventBridge는 세 가지 주요 부분으로 구성된다: 기본 이벤트 버스, 커스텀 이벤트 버스, 파트너 이벤트 버스.
* EventBridge의 핵심 기능은 필터링과 라우팅 규칙으로, 이벤트를 식별하고 타겟으로 전송하는 로직을 처리한다.

### 이벤트 기반 패턴들
* 코레오그래피 패턴: 각 서비스가 독립적으로 이벤트에 반응하여 작업을 수행하는 방식
* 기능없는 통합 패턴(Functionless Integration): 불필요한 Lambda 함수 작성을 줄이고 네이티브 통합을 활용하는 방식
* API Destination 패턴: 외부 시스템과의 통합을 위한 HTTP 엔드포인트를 제공하는 방식
* 서킷 브레이커 패턴: 시스템 장애 시 빠른 실패 처리와 복구를 위한 패턴
* 오케스트레이션 패턴: Step Functions를 활용한 워크플로우 제어 방식

### 자주 묻는 질문들
* 이벤트 버스의 수는 기업 전체, 도메인, 경계 컨텍스트 수준에서 결정할 수 있다.
* EventBridge와 Kinesis는 각각 다른 목적을 가지며, Kinesis는 대규모 이벤트 수집에, EventBridge는 정제된 이벤트 처리에 적합하다.
* SQS, SNS, EventBridge는 각각 큐잉, pub/sub, 이벤트 브로커라는 서로 다른 목적을 가진다.

