# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** AttributeError
- **에러 메시지** 'str' object has no attribute 'get'

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 5
- **현재 턴 플레이어** player1
- **플레이어 1 체력** 18 (PP 0)
- **플레이어 2 체력** 20 (PP 0)

### 플레이어 1 손패 카드 목록
['추격선언 뮤', '폭연의 총장 츠바사', '플래시 블링크', '마음 있는 협공', '빛의 섭리 루 오']

### 플레이어 2 손패 카드 목록
['와일드 걸', '숲의 행진', '고요한 응원', '고요한 응원']

### 플레이어 1 필드 카드 목록
['옛 천부 요그젠타', '암옥의 잔광 재스퍼', '패스트 코어']

### 플레이어 2 필드 카드 목록
['혼탁에 물든 시민', '혼탁에 물든 시민']

## 3 상세 트레이스백 정보
```text
Traceback (most recent call last):
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 329, in run_fuzzing
    game.play_card(current_player, action["card_id"], action["enhanced_cost"], action["use_extra_pp"])
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 477, in play_card
    self.process_events()
    ~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 142, in process_events
    self.event_manager.process_events()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\event_manager.py", line 45, in process_events
    listener.callback(event)
    ~~~~~~~~~~~~~~~~~^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 201, in _handle_card_effect
    self.effect_processor.resolve_effect(effect_to_resolve, card_id, self.game_state_manager, target_id)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 973, in resolve_effect
    handler(effect_data, target, game_state_manager)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 1168, in _process_transform
    new_card = game_state_manager.create_card_instance(new_card_data, owner_id)
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\game_state_manager.py", line 58, in create_card_instance
    card = Card(card_data_obj, owner_id, new_card_id)
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\models\card.py", line 17, in __init__
    self.current_cost = card_data.get("cost", 0)  # 현재 코스트입니다. 주문 증폭 등에 의해 변경될 수 있습니다.
                        ^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

```
