
## Nova Pro
### 클러스터 운영 단순화
* Amazon EKS를 사용하여 컨테이너 기반 애플리케이션을 실행하는 선택 이유 설명.
* VPC CNI를 사용한 포드 간 네트워킹과 Auto Mode의 통합.
* Auto Mode에서 관리되는 구성 요소: VPC CNI, CoreDNS, kube-proxy, 애플리케이션 로드 밸런서 컨트롤러.

### 외부 애플리케이션 노출
* AWS Load Balancer Controller를 사용한 애플리케이션 로드 밸런서(ALB) 생성.
* 네트워크 로드 밸런서(NLB) 생성을 위한 서비스 유형 로드 밸런서 생성.
* 인그레스 리소스와 서비스 리소스를 사용한 외부 트래픽 처리.

### 네트워크 복원력 향상
* Amazon EKS와 Amazon Recovery Controller(ARC)의 통합을 통한 재해 복구 시나리오 테스트 및 복구 용이.
* ARC를 통해 AZ 장애 시 자동으로 서비스에서 엔드포인트 해제.

### 서비스 메시 도입
* 서비스 메시의 장점: 네트워크 보안, 관찰 기능, 신뢰성 향상.
* Istio Ambient Mesh를 통한 서비스 메시 구현: 뮤추얼 TLS, 레이어 4 권한 부여 정책, 레이어 7 고급 라우팅.
* 서비스 메시의 한계: 특정 워크로드에 대한 사이드카 프록시 필요.

### 쿠버네티스 게이트웨이 API
* 쿠버네티스 게이트웨이 API의 장점: 인그레스의 한계 극복, 서비스 메시의 교훈 반영.
* 게이트웨이 API를 통한 멀티클러스터 설정 용이.
* Amazon VPC Lattice를 통한 게이트웨이 API 구현: 레이어 7에서 동작, 여러 클러스터 간 트래픽 연결 가능.

### 학습 자료
* EKS Workshop: 셀프 페이스로 EKS에 대한 다양한 내용 학습 가능.
* EKS Best Practices Guide: 네트워킹 최적화 설정 및 모범 사례 안내.


## Cloaude 3.5 Sonnet v2
### EKS와 Kubernetes 네트워킹 기본 구성
* Amazon EKS Auto Mode는 컨트롤 플레인과 데이터 플레인의 주요 네트워킹 컴포넌트(VPC CNI, CoreDNS, kube-proxy, Load Balancer Controller)를 자동으로 관리해준다.
* Amazon VPC CNI는 AWS VPC와 깊이 통합되어 있어 VPC의 IP를 파드에 할당하고 보안 및 관찰 기능을 활용할 수 있다.
* AWS Load Balancer Controller는 인그레스와 서비스 리소스를 통해 ALB와 NLB를 자동으로 프로비저닝하고 관리한다.

### 네트워크 복원력과 서비스 메시
* Amazon Recovery Controller(ARC)와의 통합으로 AZ 장애 시 자동으로 영향받는 엔드포인트를 서비스에서 제거하여 복구 시간을 단축할 수 있다.
* Istio Ambient Mesh는 사이드카 없이도 서비스 간 mTLS, Layer 4/7 인증 정책, 고급 트래픽 라우팅 등을 제공한다.
* Kiali 대시보드를 통해 서비스 간 통신과 트래픽 흐름을 시각화하고 모니터링할 수 있다.

### Kubernetes Gateway API와 멀티클러스터
* Kubernetes Gateway API는 인그레스의 한계를 극복하고 서비스 메시의 교훈을 반영한 새로운 표준이다.
* Amazon VPC Lattice는 Gateway API를 구현하여 VPC와 계정 간 Layer 7 연결을 제공한다.
* VPC Lattice를 통해 Kubernetes, EC2, ECS, Lambda 등 다양한 컴퓨팅 서비스 간의 통합된 네트워킹이 가능하다.

