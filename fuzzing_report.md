# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** AttributeError
- **에러 메시지** 'str' object has no attribute 'get'

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 12
- **현재 턴 플레이어** player2
- **플레이어 1 체력** 20 (PP 0)
- **플레이어 2 체력** 16 (PP 0)

### 플레이어 1 손패 카드 목록
['적염의 무희 안스리아', '적염의 무희 안스리아', '화기애애한 요정', '낙원숭이', '낙원숭이', '폭풍의 천업 그림니르', '꽃이 만발한 정원']

### 플레이어 2 손패 카드 목록
['블라스트 윙 피유라', '패공의 무신 나타', '쌍륜야행 긴세츠&유즈키', '혼융의 기도자', '청춘의 하모니', '향락의 상류시민', '오야화의 개전', '페이탈 테이커']

### 플레이어 1 필드 카드 목록
['울창한 숲의 전사', '화기애애한 요정', '요정']

### 플레이어 2 필드 카드 목록
[]

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
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 1025, in resolve_effect
    handler(effect_data, target, game_state_manager)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 589, in _process_summon
    card = game_state_manager.create_card_instance(data, target_id)
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\game_state_manager.py", line 68, in create_card_instance
    card = Card(card_data_obj, owner_id, new_card_id)
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\models\card.py", line 17, in __init__
    self.current_cost = card_data.get("cost", 0)  # 현재 코스트입니다. 주문 증폭 등에 의해 변경될 수 있습니다.
                        ^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

```
