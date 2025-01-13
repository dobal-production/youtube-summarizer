
## Nova Pro
### EKS Hybrid Nodes 소개
* EKS Hybrid Nodes는 온프레미스 및 엣지 인프라를 EKS 클러스터의 노드로 사용할 수 있게 하는 새로운 기능이다.
* 이 기능을 통해 온프레미스 환경에서 쿠버네티스를 관리하는 것을 줄일 수 있으며, 클라우드와 온프레미스 환경에서 쿠버네티스를 통합하여 관리할 수 있다.

### 온프레미스 Kubernetes 운영의 과제
* 온프레미스 Kubernetes 클러스터 관리의 운영 오버헤드
* 쿠버네티스 관리 경험의 제한
* 기술 스프롤과 관련된 문제

### EKS 온프레미스 및 엣지 사용 사례 포트폴리오
* EKS on Outpost: AWS 관리 인프라를 데이터 센터나 콜로 시설에서 실행
* EKS Anywhere (EKSA): 온프레미스 인프라에서 실행되는 AWS 관리 또는 지원 Kubernetes 관리 소프트웨어

### EKS Hybrid Nodes의 필요성
* 온프레미스 환경을 클라우드에 연결하여 클라우드 관리 서비스를 활용하고 싶은 고객 충족
* 온프레미스 하드웨어를 교체할 수 없는 고객을 위한 솔루션 제공

### EKS Hybrid Nodes의 주요 기능
* 온프레미스 및 엣지 인프라를 EKS 클러스터의 노드로 사용
* 동일한 AWS 관리 EKS 클러스터, 기능 및 도구 사용
* EKS 애드온, EKS Pod Identity, 클러스터 액세스 항목 등과 함께 사용 가능
* SSM, IAM Roles Anywhere, Amazon Managed Prometheus, CloudWatch 등과 통합

### EKS Hybrid Nodes의 아키텍처
* EKS 컨트롤 플레인은 AWS 리전에서 실행
* 워커 노드만 온프레미스에서 실행
* 네트워크 연결은 VPC를 통해 이루어짐
* 인증은 임시 IAM 자격 증명을 사용

### EKS Hybrid Nodes의 공유 책임 모델
* AWS는 클라우드에서 관리, 사용자는 온프레미스 인프라 관리
* AWS는 Hybrid Node CLI (nodeadm)로 설치된 구성 요소 지원

### EKS Hybrid Nodes 사용을 위한 핵심 전제 조건
* 네트워크 연결성: VPC와 온프레미스 환경 간의 프라이빗 연결
* 인프라 계층: 사용자 고유의 인프라 (베어메탈 서버, VMware 가상 머신, Nutanix 인프라 등)
* 운영 체제: Ubuntu, Red Hat Enterprise Linux, Amazon Linux 2023 등
* 자격 증명: Systems Manager Hybrid Activations 또는 IAM Roles Anywhere를 통한 임시 IAM 자격 증명

### EKS Hybrid Nodes의 네트워킹
* 클러스터 생성 시 원격 노드 네트워크 및 원격 포드 네트워크 구성
* VPC 라우팅 테이블 및 온프레미스 라우팅 테이블 구성
* CNI 구성 (Cilium 또는 Calico 사용 가능)
* 네트워크 액세스: 방화벽 및 보안 그룹 설정

### Hybrid Nodes CLI (nodeadm)
* 온프레미스 환경에서 Hybrid Nodes를 관리하는 도구
* 운영 체제 빌드 파이프라인에서 nodeadm 설치 프로세스 실행 권장
* SSM Hybrid Activations 또는 IAM Roles Anywhere를 통한 인증 지원

### EKS Hybrid Nodes의 출시 기능
* 모든 AWS 리전(GovCloud 및 중국 리전 제외)에서 사용 가능
* 새로운 EKS 클러스터에서만 사용 가능 (기존 클러스터 지원 예정)
* 동일한 EKS Kubernetes 버전 사용 가능
* 혼합 모드 EKS 클러스터 지원
* IPv4만 지원
* Cilium 및 Calico를 포드 네트워킹으로 지원
* 코어 네트워킹 애드온 (coreDNS, kube-proxy) 지원
* Pod Identities 및 IAM 역할 사용 가능
* 관찰성 애드온 (Amazon Managed Prometheus, CloudWatch 에이전트 등) 지원
* GuardDuty EKS Protection 지원

### 모범 사례
* 노드 부트스트랩 자동화
* 낮은 대기 시간을 위해 가장 가까운 AWS 리전 사용
* 네트워킹 및 보안 팀과 협력
* VPC 보안 그룹 구성
* 워크로드 배치를 위한 레이블 사용
* AWS 통합 활용
* 공용 및 프라이빗 엔드포인트 액세스 중 하나만 사용
* 혼합 모드 클러스터에서 coreDNS 복제본 보유
* 영역 레이블 사용
* 롤링 업그레이드 수행
* 사용하지 않는 노드 삭제

### Northwestern Mutual의 EKS Hybrid Nodes 경험
* Northwestern Mutual은 금융 서비스 회사로, 미국인의 재정적 불안을 해소하는 데 중점을 둠
* 쿠버네티스를 사용하여 마이크로서비스 허브를 구축하고 클라우드 플랫폼을 출시함
* EKS로 마이그레이션하여 컨테이너 플랫폼 팀을 통합함
* 온프레미스 Kubernetes 솔루션의 필요성을 인식하고 EKS Hybrid Nodes를 도입함
* EKS Hybrid Nodes를 통해 안정성, 보안, 표준화, 단순화, 비용 절감, 직원 경험 향상 등의 이점을 얻음


## Cloaude 3.5 Sonnet v2
### EKS Hybrid Nodes 소개
* AWS는 온프레미스와 엣지 인프라를 EKS 클러스터의 용량으로 활용할 수 있는 새로운 기능인 EKS Hybrid Nodes를 출시했다.
* 고객들이 온프레미스에서 Kubernetes를 운영할 때 겪는 운영 오버헤드, 제한된 경험, 기술 분산 등의 문제를 해결하기 위해 개발되었다.
* 클라우드와 온프레미스 환경에서 일관된 Kubernetes 관리 경험을 제공한다.

### EKS Hybrid Nodes의 주요 특징
* AWS 리전에서 실행되는 EKS 컨트롤 플레인을 사용하며, 워커 노드만 온프레미스에서 실행된다.
* 기존 온프레미스 인프라(VM, 베어메탈)를 그대로 활용할 수 있다.
* VPC를 통한 프라이빗 네트워크 연결이 필요하다.
* SSM hybrid activations 또는 IAM Roles Anywhere를 통한 인증을 지원한다.
* EKS 애드온, Pod Identity, 클러스터 액세스 등 EKS의 주요 기능들을 사용할 수 있다.

### 구현 시 고려사항
* 네트워크 연결은 최소 100Mbps 대역폭과 200ms 이하의 지연시간이 권장된다.
* nodeadm CLI를 통해 노드 부트스트랩을 자동화할 수 있다.
* 워크로드 배치를 위해 compute-type=hybrid 레이블을 활용해야 한다.
* 보안그룹과 라우팅 테이블 설정에 주의가 필요하다.
* 가용성을 위해 coreDNS 복제본을 클라우드와 온프레미스 양쪽에 배치해야 한다.

### Northwestern Mutual 적용 사례
* 기존 온프레미스 Kubernetes 환경의 안정성과 운영 효율성 문제를 해결하기 위해 EKS Hybrid Nodes를 도입했다.
* Direct Connect, VMware, RHEL, SSM을 활용해 구현했다.
* 데이터센터 장애 시에도 20분 이내 복구가 가능했으며, 컨트롤 플레인 분리로 워크로드 안정성이 향상되었다.
* 일관된 개발자 경험과 도구 사용, 비용 효율성 등의 이점을 얻을 수 있었다.

