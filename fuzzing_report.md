# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** AttributeError
- **에러 메시지** 'str' object has no attribute 'get'

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 18
- **현재 턴 플레이어** player2
- **플레이어 1 체력** 10 (PP 1)
- **플레이어 2 체력** 12 (PP 6)

### 플레이어 1 손패 카드 목록
['치유의 수녀', '안식의 단결자', '추앙의 매니저 이니시아', '격진의 골리앗', '전달의 성조', '미동 없는 성기사', '속단의 서슬 아니에스', '절망의 격류']

### 플레이어 2 손패 카드 목록
['파괴의 긍정자', '스톤 브레이크', '합주하는 마음 츠바이', '퓨처 코어', '탐정의 돋보기', '진소화의 굽어봄', '갱생한 야왕 쇼']

### 플레이어 1 필드 카드 목록
['절망의 현현 마윈', '투영의 새 동상']

### 플레이어 2 필드 카드 목록
['New Revelation', '대담한 그래피터', '신비의 아티팩트', '고대의 아티팩트']

## 3 상세 트레이스백 정보
```text
Traceback (most recent call last):
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 341, in run_fuzzing
    game.engage_card(action["card_id"], current_player)
    ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 793, in engage_card
    self.process_events()
    ~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 143, in process_events
    self.event_manager.process_events()
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\event_manager.py", line 45, in process_events
    listener.callback(event)
    ~~~~~~~~~~~~~~~~~^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 204, in _handle_card_effect
    self.effect_processor.resolve_effect(effect_to_resolve, card_id, self.game_state_manager, target_id)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 1090, in resolve_effect
    handler(effect_data, target, game_state_manager)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 632, in _process_summon
    card = game_state_manager.create_card_instance(data, target_id)
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\game_state_manager.py", line 69, in create_card_instance
    card = Card(card_data_obj, owner_id, new_card_id)
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\models\card.py", line 17, in __init__
    self.current_cost = card_data.get("cost", 0)  # 현재 코스트입니다. 주문 증폭 등에 의해 변경될 수 있습니다.
                        ^^^^^^^^^^^^^
AttributeError: 'str' object has no attribute 'get'

```
