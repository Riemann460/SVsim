# SVsim: Shadowverse Simulation Engine


## 1. About The Project
SVsim은 Cygames의 디지털 카드 게임 '섀도우버스: 월즈 비욘드'의 핵심 게임플레이 로직을 구현한 Python 기반 게임 엔진입니다. 본 프로젝트는 카드의 복잡한 상호작용과 게임 규칙을 정확하게 처리하고, 확장이 용이한 아키텍처를 구축하는 것을 목표로 합니다.


## 2. Core Features
현재 구현된 주요 기능은 다음과 같습니다.

### 게임 엔진

 - Game Start: 덱 로드, 초기 드로우 & 멀리건
 - Turn Management: 턴 진행에 따른 PP 관리 및 드로우
 - Player Actions: 카드 플레이, 추종자 공격 등 플레이어 선택에 따른 액션 처리
 - Card & Zone Management
   - Deck, Hand, Field, Graveyard 등 Zone 구현
   - Zone 사이의 카드이동 및 상태 변화 처리
 - Effect Processing: 출격, 유언, 진화시 등 다양한 카드 효과 처리 로직
   - Event & Listner Management
   - Keyword Abilities: 수호, 질주, 돌진, 흡혈, 필살 등 15개 이상의 공통 키워드 능력 구현 완료
 - GUI: Tk 활용 GUI 디버깅 도구

### 카드 DB 파이프라인

 - 스크립트를 통한 카드 정보 자동 수집 및 JSON 데이터 변환
 - 파서를 이용해 텍스트 기반의 카드 효과를 엔진이 처리 가능한 구조적 데이터로 변환
 - 2탄 카드팩까지의 raw_data 수집 완료


## 3. Development Roadmap
향후 아래 기능들을 우선순위에 따라 개발할 예정입니다.

### 1순위 목표

  - 미구현 카드 효과 메커니즘 추가 구현(모드, 콤보, 주문증폭, 대지의 비술 등)

### 추후 계획

  - 기본 ai 구현(random 함수 기반)
  - ai 강화 학습 구현


## 4. Tech Stack
  - Main Language: Python
  - Data Collection: Selenium
  - Data Handling: Pandas
