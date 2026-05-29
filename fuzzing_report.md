# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** TypeError
- **에러 메시지** unsupported operand type(s) for +=: 'int' and 'str'

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 7
- **현재 턴 플레이어** player1
- **플레이어 1 체력** 19 (PP 0)
- **플레이어 2 체력** 20 (PP 0)

### 플레이어 1 손패 카드 목록
['블라스트 윙 피유라', '오야화 샤크도', '페이탈 테이커', '페이탈 테이커', '은빛 탄환 레이븐', '교지의 타천사 벨리알']

### 플레이어 2 손패 카드 목록
['청춘의 하모니', '패공의 무신 나타', '팔계화 게텐오', '갈욕의 네크로맨서', '갈욕의 네크로맨서']

### 플레이어 1 필드 카드 목록
['녹턴 제너럴 엑셀라']

### 플레이어 2 필드 카드 목록
['혼융의 긍정자']

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
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 829, in resolve_effect
    handler(effect_data, target, game_state_manager)
    ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\src\engine\effect_processor.py", line 384, in _process_stat_buff
    target.current_attack += attack
TypeError: unsupported operand type(s) for +=: 'int' and 'str'

```
