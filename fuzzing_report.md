# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** AttributeError
- **에러 메시지** 'str' object has no attribute 'type'

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 13
- **현재 턴 플레이어** player1
- **플레이어 1 체력** 13 (PP 0)
- **플레이어 2 체력** 17 (PP 0)

### 플레이어 1 손패 카드 목록
['불굴의 파이터', '세찬 광명 아폴론', '욕심쟁이 지천사 루비', '탐정의 돋보기', '고블린의 습격', '세찬 광명 아폴론', '탐정의 돋보기', '고블린의 습격', '낙랑의 천궁 필도어']

### 플레이어 2 손패 카드 목록
['격진의 골리앗', '격진의 골리앗', '모험가 길드', '관찰하는 탐정', '신의 뇌정', '캐러밴 맘모스', '관찰하는 탐정', '신의 뇌정']

### 플레이어 1 필드 카드 목록
['욕심쟁이 지천사 루비']

### 플레이어 2 필드 카드 목록
['욕심쟁이 지천사 루비', '불굴의 파이터']

## 3 상세 트레이스백 정보
```text
Traceback (most recent call last):
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 189, in run_fuzzing
    game.engage_card(action["card_id"], current_player)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 749, in engage_card
    self.process_events()
    ~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 141, in process_events
    self.event_manager.process_events()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\event_manager.py", line 45, in process_events
    listener.callback(event)
    ~~~~~~~~~~~~~~~~~^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 197, in _handle_card_effect
    self.effect_processor.resolve_effect(effect_to_resolve, card_id, self.game_state_manager, target_id)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 788, in resolve_effect
    handler(effect_data, target, game_state_manager)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 558, in _process_add_keyword
    print(f"[LOG] 처리 내용: 키워드 부여, 타겟: {target.get_display_name()}, 키워드: {value.type.value}")
                                                                                      ^^^^^^^^^^
AttributeError: 'str' object has no attribute 'type'

```
