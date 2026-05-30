# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** TypeError
- **에러 메시지** cannot unpack non-iterable int object

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 7
- **현재 턴 플레이어** player1
- **플레이어 1 체력** 20 (PP 2)
- **플레이어 2 체력** 20 (PP 1)

### 플레이어 1 손패 카드 목록
['마인드 아츠 카르라', '겁 많은 개척자', '음속의 비행병', '옛 천부 요그젠타', '천부의 심연', '엄격한 교관 일루자', '스트리트 런']

### 플레이어 2 손패 카드 목록
['진왕의 칼날 황금의 기사', '검성의 동포', '여금화의 산재', '정통성의 왕관', '약탈의 계승자 신세라이즈', '소드 프린세스 로제']

### 플레이어 1 필드 카드 목록
['폭연의 총장 츠바사']

### 플레이어 2 필드 카드 목록
['기사']

## 3 상세 트레이스백 정보
```text
Traceback (most recent call last):
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 329, in run_fuzzing
    game.play_card(current_player, action["card_id"], action["enhanced_cost"], action["use_extra_pp"])
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 505, in play_card
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
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 1065, in resolve_effect
    handler(effect_data, target, game_state_manager)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 498, in _process_stat_buff
    attack, defense = value
    ^^^^^^^^^^^^^^^
TypeError: cannot unpack non-iterable int object

```
