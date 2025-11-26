
## Nova Pro
### 클러스터 레벨 보안 제어
* AWS-AUTH 설정 대신 Cluster Access Management을 사용하여 클러스터 접근 권한을 설정할 수 있다.
* IAM Roles For Service Account (IRSA)와 Pod Identity를 사용하여 클러스터 내 애플리케이션에 AWS 리소스 접근 권한을 할당할 수 있다.
* Pod Identity는 EKS 관리형 서비스에 최적화되어 있으며, EKS Anywhere나 셀프 매니지드 쿠버네티스 클러스터에서는 지원되지 않는다.
* 클러스터 엔드포인트와 EKS API를 프라이빗 모드로 구성할 수 있다.
* EKS 애드온, EKS 최적화된 AMI 등 관리형 구성 요소를 활용할 것을 권장한다.
* Security Hub를 사용하여 클러스터의 보안 상태를 스캔할 수 있다.

### 인프라 레벨 보안 제어
* EKS Auto Mode를 사용하여 쿠버네티스 클러스터 인프라를 자동화할 수 있다.
* 쿠버네티스 네트워킹 정책과 보안 그룹을 활용하여 클러스터 네트워크 보안을 강화할 수 있다.
* Amazon GuardDuty를 사용하여 감사 로그 보호와 런타임 보호를 구현할 수 있다.
* AWS Systems Manager를 사용하여 SSH 대신 SSM을 통해 인스턴스에 접근할 수 있다.
* 컨테이너 최적화된 OS (예: Bottle Rocket)를 사용할 것을 권장한다.
* CIS 벤치마크를 사용하여 클러스터 구성을 검증할 수 있다.

### 애플리케이션 레벨 보안 제어
* 쿠버네티스 Pod Security Standards나 외부 정책 코드 솔루션 (예: Kyverno, Open Policy Agent Gatekeeper)을 사용하여 포드 보안을 강화할 수 있다.
* 권한 있는 컨테이너를 제한하고, 서비스 계정 토큰 마운트를 비활성화하며, 호스트 경로 사용을 제한할 것을 권장한다.
* 컨테이너 이미지를 정기적으로 취약점 스캔하고, 가능하면 읽기 전용 파일 시스템과 비루트 사용자를 구성할 것을 권장한다.
* Cedar를 사용하여 쿠버네티스 권한 부여를 재구상할 수 있다. Cedar는 조건부 권한 부여와 거부 기능을 지원한다.

### 추가 리소스
* EKS 모범 사례 가이드: AWS 문서에 제공되며, EKS 및 쿠버네티스 관련 모범 사례를 포함한다.
* EKS 워크샵: EKS 클러스터 생성, 구성, 애플리케이션 설치 등을 안내하는 가이드 투어.
* EKS 블루프린트: Terraform 및 AWS CDK를 위한 샘플 구성을 제공하여 EKS 시작을 돕는다.
* 공개 로드맵: GitHub의 AWS 조직 컨테이너 로드맵에서 사용자 의견을 반영하고 피드백을 받을 수 있다.


## Cloaude 3.5 Sonnet v2
### EKS 클러스터 접근 관리
* EKS는 AWS-AUTH config map을 통해 IAM 주체와 Kubernetes 권한을 매핑하는 방식을 사용했으나, 여러 API를 오가야 하는 등의 한계가 있었다.
* 이를 해결하기 위해 Cluster Access Management가 도입되어 EKS API로 통합된 권한 관리가 가능해졌다.
* Cluster Access Management는 EKS의 미래 방향성이며, 기존 AWS-AUTH config map 사용자들의 마이그레이션을 권장한다.

### Pod Identity와 IRSA
* Pod Identity는 EKS 서비스 전체에서 사용할 수 있는 역할을 생성하여 신뢰 관계를 단순화했다.
* IRSA(IAM Roles for Service Account)와 Pod Identity는 공존하며, IRSA는 EKS Anywhere나 자체 관리형 Kubernetes 클러스터에서도 사용 가능하다.
* Pod Identity는 EKS 관리형 서비스에 최적화되어 있으며, IAM 역할 세션 태그를 지원한다.

### 인프라스트럭처 보안
* EKS Auto Mode가 새롭게 출시되어 Kubernetes 클러스터 인프라를 자동화하고 최적화할 수 있게 되었다.
* AWS Systems Manager를 통해 SSH 접근을 제한하고 보안을 강화할 수 있다.
* GuardDuty를 통한 감사 로그 보호와 런타임 보호 기능을 제공한다.

### 애플리케이션 보안
* 특권 컨테이너 사용을 제한하고, 필요하지 않은 서비스 계정 토큰 마운트를 비활성화해야 한다.
* Amazon ECR과 Inspector를 통해 이미지 취약점 스캔을 정기적으로 수행할 것을 권장한다.
* Cedar를 통해 Kubernetes 인증 시스템을 개선하여 세밀한 접근 제어가 가능해졌다.

