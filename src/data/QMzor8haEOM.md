
## Nova Pro
### 하이브리드 및 엣지 환경에서의 Amazon EKS 활용
* 하이브리드 전략을 채택한 고객들이 직면하는 일반적인 문제점과 이를 해결하기 위한 Amazon Elastic Kubernetes Service (EKS)의 역할을 소개.
* 클라우드, 온프레미스, 엣지 환경에서 쿠버네티스를 표준 플랫폼으로 채택하는 이유와 남아있는 문제점에 대한 설명.
* Amazon EKS 팀이 제공하는 솔루션을 통해 쿠버네티스를 더 간단하고 효율적으로 배포할 수 있는 방법 소개.

### EKS 하이브리드 솔루션
* **EKS on Outposts**: AWS Outposts를 통해 온프레미스 인프라에 EKS를 배포하여 클라우드와 동일한 관리 경험을 제공.
  * 확장형 클러스터: 클라우드 기반 EKS 컨트롤 플레인을 생성하고, AWS Outposts 랙에 쿠버네티스 노드를 배포.
  * 로컬 클러스터: 네트워크 연결이 불안정한 환경에서도 쿠버네티스 운영을 지속할 수 있도록 로컬 컨트롤 플레인을 Outposts 랙에 배포.
* **EKS Anywhere**: 고객 관리 하드웨어 및 가상화 환경에서 EKS를 배포할 수 있는 솔루션.
  * 인프라 제공자: 베어메탈 서버, 가상화 환경(VMware, CloudStack), 파트너 환경(Nutanix), AWS Snow 등에서 배포 가능.
  * 쿠버네티스 배포: EKS Distro를 사용하여 클러스터 배포.
  * 클러스터 라이프사이클 관리: Cluster API 기반으로 클러스터 생성, 삭제, 업그레이드 등을 관리.
  * 네트워킹: Cilium을 사용한 컨테이너 네트워킹 인터페이스(CNI) 지원.
  * 큐레이티드 패키지: AWS가 관리하는 추가 기능(Harbor, Emissary, MetalLB 등) 제공.
* **EKS Hybrid Nodes**: 고객 관리 하드웨어에서 쿠버네티스 노드를 운영하고, EKS 컨트롤 플레인은 클라우드에서 관리.
  * 하이브리드 노드 CLI 유틸리티(nodeadm)를 사용하여 온프레미스 호스트를 쿠버네티스 노드로 설정하고 EKS 컨트롤 플레인에 연결.
  * AWS Systems Manager 및 AWS IAM Roles Anywhere를 통한 인증 지원.
  * 지원되는 운영 체제: Ubuntu, RHEL (베어메탈 및 가상화 환경), Amazon Linux 2023 (가상화 환경).

### EKS 하이브리드 솔루션 선택 기준
* **EKS on Outposts**: 이미 AWS Outposts를 운영 중이거나 인프라 리프레시를 고려 중인 경우 선택.
* **EKS Hybrid Nodes**: 에어갭 환경이 필요하지 않은 경우, 기존 하드웨어에서 계속 운영하면서 컨트롤 플레인 관리 책임을 AWS에 위임.
* **EKS Anywhere**: 에어갭 환경이 필요한 경우 선택.

### 추가 학습 자료
* re:Invent 세션 참석: KUB402, KUB320, KUB201 등의 세션 참고.
* EKS 워크샵 및 베스트 프랙티스 가이드 참조.
* EKS Hybrid Nodes 문서 및 세션 자료 검토.


## Cloaude 3.5 Sonnet v2
### EKS(Amazon Elastic Kubernetes Service) 하이브리드 솔루션 개요
* AWS는 고객들이 온프레미스와 클라우드 환경에서 워크로드를 실행할 때 직면하는 문제들을 해결하기 위해 EKS 하이브리드 솔루션을 제공한다.
* 표준화된 쿠버네티스 플랫폼을 통해 환경 간 일관성을 제공하고 운영 효율성을 높일 수 있다.
* EKS 팀은 고객이 어디서든 쿠버네티스 운영을 쉽게 할 수 있도록 지원하는 것을 목표로 한다.

### EKS 하이브리드 솔루션 종류
* EKS on Outposts
  - AWS가 관리하는 인프라를 데이터센터나 코로케이션 시설로 확장
  - EC2, S3, EBS 등 AWS 서비스와 가장 일관된 경험 제공
  - 2019년부터 제공되어 금융, 게임 등 다양한 산업에서 활용

* EKS Anywhere 
  - 고객이 관리하는 하드웨어에서 쿠버네티스를 실행할 수 있는 AWS 지원 소프트웨어
  - 네트워킹 요구사항이 엄격하거나 제한된 네트워크 환경에 적합
  - 통신, 금융, 여행/호텔 등의 산업에서 활용

* EKS Hybrid Nodes (신규)
  - 기존 하드웨어를 활용하면서 클라우드의 EKS 컨트롤 플레인에 연결
  - 컨트롤 플레인 관리 부담을 AWS에 위임하면서 온프레미스 워크로드 유지 가능
  - 미디어 스트리밍, 제조업 등 분산 엣지 사례에 적합

### 솔루션 선택 가이드
* AWS Outposts를 이미 사용중이거나 인프라 교체를 고려한다면 EKS on Outposts 권장
* 에어갭(Air-gap) 환경이 필요하다면 EKS Anywhere 권장
* 그 외의 경우 EKS Hybrid Nodes가 가장 적합한 선택지

