# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** TypeError
- **에러 메시지** unsupported operand type(s) for -=: 'int' and 'str'

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 16
- **현재 턴 플레이어** player2
- **플레이어 1 체력** 5 (PP 1)
- **플레이어 2 체력** 20 (PP 6)

### 플레이어 1 손패 카드 목록
['단두의 참희 사가츠마츠', '비호의 현룡', '역전의 머맨', '비호의 현룡', '성정수의 흡수', '통제하는 《정의》 이란차']

### 플레이어 2 손패 카드 목록
['복개구리', '복개구리', '여금화 운케이', '맹렬한 《전차》 오르온', '가열의 참모']

### 플레이어 1 필드 카드 목록
['대해의 오르카']

### 플레이어 2 필드 카드 목록
['찰나의 쌍검사', '통음의 아나테마 기르다리아', '진왕의 칼날 황금의 기사', '철갑 기사']

## 3 상세 트레이스백 정보
```text
Traceback (most recent call last):
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 329, in run_fuzzing
    game.play_card(current_player, action["card_id"], action["enhanced_cost"], action["use_extra_pp"])
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 504, in play_card
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
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 1080, in resolve_effect
    handler(effect_data, target, game_state_manager)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 645, in _process_deal_damage
    if target.take_damage(value):
       ~~~~~~~~~~~~~~~~~~^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\models\card.py", line 56, in take_damage
    self.current_defense -= amount
TypeError: unsupported operand type(s) for -=: 'int' and 'str'

```
