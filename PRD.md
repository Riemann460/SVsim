# PRD: 미구현 Enum 및 메커니즘 엔진 구현

## 1. 개요
- **목적**: Shadowverse Simulator (`SVsim`)의 `enums.py`에 정의되어 있으나 아직 엔진 상에 구현되지 않은 모든 미구현 키워드(EffectType), 프로세스(ProcessType), 타겟(TargetType)의 핵심 게임 로직을 구현 및 연동한다.
- **대상 프로젝트**: `SVsim`

## 2. 요구사항 및 상세 사양

### A. 콤보(COMBO) & 연계(RALLY) 상태 관리
- **콤보 (COMBO)**:
  - 플레이어가 해당 턴에 플레이한 카드의 장수를 추적합니다.
  - `Player` 클래스에 `combo_count` 필드를 추가하여 기본값 `0`으로 시작합니다.
  - 카드가 플레이될 때마다 해당 플레이어의 `combo_count`를 `1`씩 증가시킵니다.
  - 턴 종료 시 해당 플레이어의 `combo_count`를 `0`으로 초기화합니다.
- **연계 (RALLY)**:
  - 게임 시작부터 현재까지 필드에 소환된 아군 추종자의 누적 수를 관리합니다.
  - `Player` 클래스에 `rally_count` 필드를 추가하여 기본값 `0`으로 시작합니다.
  - 추종자 카드가 전장(`Zone.FIELD`)에 소환(플레이 혹은 효과 소환)될 때마다 소유주의 `rally_count`를 `1`씩 증가시킵니다.

### B. 사령술(NECROMANCY) & 사령 재생(REANIMATE)
- **사령술 (NECROMANCY)**:
  - 묘지(Graveyard)의 자원을 활용하는 메커니즘입니다.
  - `Player.graveyard` 또는 `Graveyard` 클래스에 `shadows_count` 필드를 추가하여 관리합니다.
  - 카드가 묘지로 이동할 때마다 `shadows_count`를 `1`씩 증가시킵니다.
  - 사령술 X 효과가 발동하면 `shadows_count`가 X 이상인지 검증하고, X만큼 차감합니다. 카드는 묘지에 그대로 유지됩니다.
- **사령 재생 (REANIMATE)**:
  - `REANIMATE X` 프로세스는 묘지에 존재하는 비용이 X 이하인 추종자 중 가장 비용이 높은 추종자 카드를 임의로 1장 선택하여 필드에 비용 없이 소환합니다.

### C. 흙의 비술(EARTH_RITE) & 비술 마법진(EARTH_SIGIL)
- **흙의 비술 (EARTH_RITE)**:
  - 흙의 비술 발동 시 필드(`Zone.FIELD`)에 존재하는 종족이 `EARTH_SIGIL`인 아군 마법진(Amulet) 중 **가장 먼저 소환된 마법진 1장**을 자동 파괴(묘지로 이동)합니다.

### D. 각성 (OVERFLOW)
- **각성 (OVERFLOW)**:
  - 플레이어의 최대 PP가 7 이상(`Player.max_pp >= 7`)일 때 상시 활성화되는 상태 조건입니다.
  - 효과 처리 시 플레이어의 각성 상태를 판별하여 조건부 능력을 발동합니다.

### E. 오의(SKYBOUND_ART) & 해방오의(SUPER_SKYBOUND_ART)
- **오의 및 해방오의**:
  - 카드 패(`Zone.HAND`)에 존재할 때, 아군 추종자가 진화(`EventType.FOLLOWER_EVOLVED`)하거나 초진화(`EventType.FOLLOWER_SUPER_EVOLVED`)할 때마다 해당 카드의 오의/해방오의 게이지(카운터)를 진행시킵니다.
  - 카드 객체 혹은 게이지 필드를 구현하여 관리합니다.

### F. 직접소환 (INVOKE)
- **직접소환 (INVOKE)**:
  - 턴 시작(`TURN_START`) 또는 턴 종료(`TURN_END`) 시점에 플레이어의 덱(`Zone.DECK`)을 탐색하여, 직접소환 조건을 만족하는 카드가 존재하면 코스트를 지불하지 않고 즉시 필드로 소환합니다.

### G. 변신(TRANSFORM) 및 조건부 효과(CONDITIONAL_EFFECT)
- **변신 (TRANSFORM)**:
  - 대상 카드를 지정된 신규 카드로 교체합니다. 이때 필드 퇴장에 따른 파괴(`DestroyedOnFieldEvent`) 유언 능력이 트리거되지 않도록 이벤트를 우회하여 직접 교체 처리합니다.
- **조건부 효과 (CONDITIONAL_EFFECT)**:
  - 세부 분기 조건을 파싱하고 판별하여, 조건 충족 시에만 후속 효과를 연결하여 처리합니다.

## 3. 진행 상황
- [x] 1. 미구현 Enum 기능 설계를 위한 실패 테스트 코드 작성 (TDD 환경 구축)
- [x] 2. 콤보 및 연계 메커니즘 엔진 구현
- [x] 3. 사령술 및 사령 재생 메커니즘 엔진 구현
- [x] 4. 흙의 비술 및 각성 메커니즘 엔진 구현
- [x] 5. 오의, 해방오의 및 직접소환 메커니즘 엔진 구현
- [x] 6. 변신, 조건부 효과 및 미구현 타겟 프로세서 구현
- [x] 7. 전체 통합 테스트 통과 검증 및 완료
