# SVsim: Shadowverse Game Engine


## 1. About The Project
SVsim은 Cygames의 디지털 카드 게임 '섀도우버스: 월즈 비욘드'의 핵심 게임플레이 로직을 구현한 Python 기반 게임 엔진입니다. 본 프로젝트는 카드의 복잡한 상호작용과 게임 규칙을 정확하게 처리하고, 확장이 용이한 아키텍처를 구축하는 것을 목표로 합니다.


## 2. Core Features
현재 구현된 주요 기능은 다음과 같습니다.

### 게임 플로우 엔진

 - Mulligan & Game Start: 덱 유효성 검사(40장, 카드 3장 제한) 및 초기 드로우, 멀리건 로직 구현
 - Turn Management: 턴 시작/종료에 따른 PP 자동 관리 및 카드 드로우 시스템
 - Player Actions: 카드 플레이, 추종자 공격/진화/초진화 등 핵심 액션 처리 (후공 첫 턴 EP 포함)
 - 카드 및 게임 존 관리
   - Deck, Hand, Field, Graveyard 등 핵심 게임 존(Zone) 구현
   - 존 간의 카드 이동 및 상태 변화 추적
 - 효과 및 키워드 시스템
 - Effect Processing: 출격, 유언, 진화시 등 다양한 발동 조건을 가진 효과 처리 시스템 (현재 타겟팅은 임시로 무작위 대상 지정)
 - Keyword Abilities: 수호, 질주, 돌진, 흡혈, 필살 등 15개 이상의 공통 키워드 능력 구현 완료

### 확장 가능한 카드 데이터베이스

스크립트를 통한 카드 정보 자동 수집 및 JSON 데이터 변환
파서를 이용해 텍스트 기반의 카드 효과를 엔진이 처리 가능한 구조적 데이터로 변환하는 파이프라인 구축


## 3. Development Roadmap
향후 아래 기능들을 우선순위에 따라 개발할 예정입니다.

### 1순위 목표

  - 타겟팅 시스템 구현: 플레이어가 직접 효과의 대상을 지정하는 로직 개발
  - 클래스 고유 키워드 추가: 콤보, 주문증폭, 대지의 비술 등 직업별 핵심 메커니즘 구현

### 추후 계획

  - GUI 기반 디버깅 도구: 게임 상태를 시각적으로 확인하고 테스트할 수 있는 디버거 개발
  - 모드 능력 처리: 여러 효과 중 하나를 선택하여 발동하는 카드 능력 구현


## 4. Tech Stack
  - Main Language: Python
  - Data Collection: Selenium, BeautifulSoup
  - Data Handling: Pandas
