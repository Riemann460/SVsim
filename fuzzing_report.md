# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** AttributeError
- **에러 메시지** 'str' object has no attribute 'get'

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 31
- **현재 턴 플레이어** player1
- **플레이어 1 체력** 16 (PP 1)
- **플레이어 2 체력** 2 (PP 1)

### 플레이어 1 손패 카드 목록
['은빛얼음의 용소녀 필레인', '현란한 봉황 호짱', '루인 제노사이더', '흑염의 격류', '전단지 돌리는 용인', '완숙 해수어', '모멸의 나라', '은빛얼음의 숨결']

### 플레이어 2 손패 카드 목록
['옛 천정 카르기덴틀라', '허구의 술식', '언리쉬', '마련의 연정 시임', '프리티 프레데터', '위대의 증명']

### 플레이어 1 필드 카드 목록
['시련의 석판', '시련의 석판', '모멸의 나라', '푸른 하늘을 나아가는 기공사 그랑&지타', '은빛얼음의 용소녀 필레인']

### 플레이어 2 필드 카드 목록
['드래고닉 스트라이크', '러브 맥스 봄버', '위대의 현현 마젤베인']

## 3 상세 트레이스백 정보
```text
Traceback (most recent call last):
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 329, in run_fuzzing
    game.play_card(current_player, action["card_id"], action["enhanced_cost"], action["use_extra_pp"])
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 478, in play_card
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
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 1034, in resolve_effect
    handler(effect_data, target, game_state_manager)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 569, in _process_add_card_to_hand
    card = game_state_manager.create_card_instance(data, target_id)
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\game_state_manager.py", line 69, in create_card_instance
    card = Card(card_data_obj, owner_id, new_card_id)
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\models\card.py", line 17, in __init__
    self.current_cost = card_data.get("cost", 0)  # 현재 코스트입니다. 주문 증폭 등에 의해 변경될 수 있습니다.
                        ^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

```
