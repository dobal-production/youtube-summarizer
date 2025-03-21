
## Nova Pro
### 세션 개요
* 세션은 아마존의 다양한 제품과 서비스에서 활용된 탄력적 아키텍처 사례를 공유하며, 이를 통해 참석자들에게 영감을 주고 실제 적용 가능한 방법을 제시한다.

### 복원력의 정의
* 복원력은 애플리케이션이나 워크로드가 다양한 문제(과부하, 충돌, 사용자로부터 오는 잘못된 입력 등)를 흡수하고 복구할 수 있는 능력을 의미한다.
* 애플리케이션은 기능을 유지하며 고객에게 비즈니스 가치를 제공해야 한다.

### 확장성과 복원력
* 확장성은 예상 이상의 부하에도 애플리케이션이 가용성을 유지할 수 있도록 설계하는 것을 의미한다.
* 아마존의 프라임 데이와 같은 대규모 이벤트에서 AWS 서비스를 통해 높은 처리량을 달성한 사례를 통해 설명한다.

### 마이크로서비스 기반 아키텍처
* 아마존닷컴은 수만 개의 마이크로서비스로 구성되어 있으며, 이를 통해 복원력을 유지한다.
* 각 마이크로서비스는 독립적으로 확장되며, 일부 서비스에 문제가 발생해도 전체 시스템의 기능성을 유지할 수 있다.

### 셀 기반 아키텍처
* 셀 기반 아키텍처는 서비스를 작은 그룹(셀)으로 나누어 문제 발생 시 영향을 최소화하는 방식이다.
* 프라임 비디오와 아마존 뮤직은 셀 기반 아키텍처를 통해 복원력을 높이고 특정 비즈니스 문제를 해결했다.

### 링(Ring)의 이벤트 기반 확장 가능 아키텍처
* 링은 초당 130,000회 이상의 요청을 처리하면서 높은 가용성을 유지하는 이벤트 기반 아키텍처를 구축했다.
* 링은 할로윈과 같은 대규모 이벤트 동안 비디오 트랜스코딩을 처리하고 실시간으로 알림을 전송해야 한다.

### 링의 복원력 원칙
* 셀 기반 아키텍처: 셀 중 하나가 문제 발생 시 나머지 셀이 부하를 분산하여 처리한다.
* 폴백 셀: 상관 실패 문제를 해결하기 위해 추가 셀을 구축하여 대체 서비스를 제공한다.
* 회로 차단기: 문제가 발생한 셀의 트래픽을 다른 셀로 리디렉션하여 서비스 가용성을 유지한다.

### 결론
* 아마존의 다양한 제품과 서비스에서 활용된 복원력 원칙과 아키텍처는 모든 규모의 기업에 적용 가능하다.
* AWS 리질리언시 허브, 폴트 인젝션 서비스 등의 도구를 활용하여 탄력적인 아키텍처를 구축할 수 있다.


## Cloaude 3.5 Sonnet v2
### 회복탄력성(Resilience)의 정의와 중요성
* 회복탄력성은 애플리케이션이나 워크로드가 비정상적인 부하, 충돌, 악성 요청 등을 흡수하고 복구하는 능력을 의미한다.
* Amazon.com은 1994년 2대의 서버로 시작했으나, 현재는 수만 개의 마이크로서비스로 구성된 복잡한 시스템으로 발전했다.
* Prime Day와 같은 대규모 이벤트에서 수백만 건의 요청을 처리할 수 있는 규모의 회복탄력성이 필요하다.

### 마이크로서비스 아키텍처
* Amazon.com의 상세 페이지는 여러 개의 독립적인 마이크로서비스(위젯)로 구성되어 있다.
* 각 마이크로서비스는 제목, 별점, 이미지 등 특정 기능을 담당하며 독립적으로 확장 가능하다.
* 일부 서비스에 문제가 발생해도 핵심 기능(가격, 제목 등)이 작동하면 거래가 가능한 우아한 성능 저하(graceful degradation) 방식을 채택했다.

### 셀 기반 아키텍처
* Prime Video와 Amazon Music은 셀 기반 아키텍처를 통해 회복탄력성을 확보했다.
* 셀은 독립적인 작업 그룹으로, 한 셀의 문제가 다른 셀에 영향을 미치지 않도록 설계되었다.
* 셀 라우터를 통해 요청을 적절한 셀로 분배하며, 셀 간에는 상태를 공유하지 않는 것이 중요하다.

### Ring의 회복탄력성 전략
* Ring은 초당 130,000개 이상의 요청을 처리하며 99.9999%의 가용성을 유지한다.
* 할로윈과 같은 대규모 이벤트 시에도 안정적인 서비스를 제공하기 위해 확장 가능한 아키텍처를 구축했다.
* 셀 기반 아키텍처, 폴백 셀, 서킷 브레이커 등 다양한 회복탄력성 패턴을 구현했다.
* 전 세계 8개 지역에 배포되어 초당 300,000개 이상의 요청을 처리하며, 일부 지역에서는 100% 가용성을 달성했다.

