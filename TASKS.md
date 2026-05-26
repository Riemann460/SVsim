# TASKS: 미구현 Enum 및 메커니즘 엔진 구현

## 1. TDD Fail Tests Environment Setup
- [x] 1.1 각 미구현 메커니즘의 실패 조건과 연동을 검증할 단위 테스트 코드 작성 (e.g. `tests/test_unimplemented_enums.py`)
- [x] 1.2 테스트 실행하여 실패 확인

## 2. Combo and Rally Implementation
- [x] 2.1 `Player` 모델에 `combo_count` 및 `rally_count` 속성 추가
- [x] 2.2 카드가 손패에서 플레이될 때 `combo_count` 증가 및 턴 종료 시 `0`으로 초기화 연동
- [x] 2.3 추종자가 필드에 진입할 때 `rally_count` 증가 연동
- [x] 2.4 단위 테스트로 콤보 및 연계 작동 검증

## 3. Necromancy and Reanimate Implementation
- [x] 3.1 `Graveyard` 모델에 `shadows_count` 속성 추가 및 카드가 묘지로 갈 때 1씩 증가 처리
- [x] 3.2 `EffectProcessor`에 `ProcessType.GAIN_SHADOW` (묘지 카운트 증가) 구현
- [x] 3.3 `EffectProcessor`에 사령술(Necromancy) 처리를 위한 `_process_necromancy` (또는 조건 판별 및 묘지 소모) 연동
- [x] 3.4 `EffectProcessor`에 `ProcessType.REANIMATE` 구현 (묘지 내 비용 X 이하 최고 비용 추종자 무작위 소환)
- [x] 3.5 단위 테스트로 사령술 및 사령 재생 작동 검증

## 4. Earth Rite and Overflow Implementation
- [x] 4.1 `EffectProcessor`에 `ProcessType.GAIN_EARTH_SIGIL` 구현 및 `EARTH_SIGIL` 마법진 파괴 기능 구현
- [x] 4.2 `Player` 모델에 각성(Overflow) 상태 판별 프로퍼티 `is_overflow` 추가
- [x] 4.3 `EffectProcessor`에서 흙의 비술 작동 시 필드에 먼저 소환된 `EARTH_SIGIL` 마법진 파괴 처리 연동
- [x] 4.4 단위 테스트로 흙의 비술 및 각성 작동 검증

## 5. Skybound Art and Invoke Implementation
- [x] 5.1 오의 및 해방오의 카드를 위한 게이지 속성을 `Card` 모델에 설계 및 진화/초진화 시 게이지 차감 로직 연동
- [x] 5.2 `main_game_logic.py` 내의 턴 시작(`TURN_START`) 및 턴 종료(`TURN_END`) 시점에 직접소환(`INVOKE`) 검사 및 자동 소환 수행 로직 연동
- [x] 5.3 단위 테스트로 오의 및 직접소환 작동 검증

## 6. Transform, Conditional Effect and Target Types Implementation
- [x] 6.1 `EffectProcessor`에 `ProcessType.TRANSFORM` 구현 (파괴 유언 발동 없이 대상 카드를 지정 카드로 필드 교체)
- [x] 6.2 `EffectProcessor`에 `ProcessType.CONDITIONAL_EFFECT` 및 조건 분기 판별 로직 구현
- [x] 6.3 미구현 TargetType 핸들러(e.g., `ALL_FOLLOWERS`, `ALL_OPPONENTS`, `ANOTHER_ALLY_FOLLOWER_RANDOM` 등)들을 `effect_processor.py`에 구현 및 연동
- [x] 6.4 단위 테스트로 변신, 조건부 효과, 신규 타겟 작동 검증

## 7. Integration and Validation
- [x] 7.1 전체 테스트 실행 및 오류 디버깅
- [x] 7.2 최종 PRD 및 TASKS 진행 상황 완료 마크 최신화
