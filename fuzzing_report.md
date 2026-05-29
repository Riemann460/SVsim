# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** TypeError
- **에러 메시지** unsupported operand type(s) for -=: 'int' and 'str'

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 7
- **현재 턴 플레이어** player1
- **플레이어 1 체력** 19 (PP 2)
- **플레이어 2 체력** 20 (PP 1)

### 플레이어 1 손패 카드 목록
['꽃피는 근육 피오리토', '청략의 첩보병', '대담한 부단장 게르트', '결의의 휘룡 아서', '삼장희의 난격', '약탈의 계승자 신세라이즈']

### 플레이어 2 손패 카드 목록
['저글링 까마귀', '특기표적 헤렘허니', '외줄타기 고양이', '데드 프리젠터 맥밀란', '데드 프리젠터 맥밀란']

### 플레이어 1 필드 카드 목록
[]

### 플레이어 2 필드 카드 목록
['뱀파 키보디스트 루루미']

## 3 상세 트레이스백 정보
```text
Traceback (most recent call last):
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 329, in run_fuzzing
    game.play_card(current_player, action["card_id"], action["enhanced_cost"], action["use_extra_pp"])
    ~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\main_game_logic.py", line 460, in play_card
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
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 849, in resolve_effect
    handler(effect_data, target, game_state_manager)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 483, in _process_deal_damage
    if target.take_damage(value):
       ~~~~~~~~~~~~~~~~~~^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\models\card.py", line 51, in take_damage
    self.current_defense -= amount
TypeError: unsupported operand type(s) for -=: 'int' and 'str'

```
