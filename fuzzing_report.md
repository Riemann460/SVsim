# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** AssertionError
- **에러 메시지** 초진화 추종자 갈증의 현현 기르네리제 (ID 61)의 max_defense(2)가 기본 스탯 상승폭인 +3 미만입니다.

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 14
- **현재 턴 플레이어** player2
- **플레이어 1 체력** 20 (PP 0)
- **플레이어 2 체력** 17 (PP 1)

### 플레이어 1 손패 카드 목록
['용기로 가득한 자', '로스트 러브 데빌', '로스트 러브 데빌', '혼융의 계승자 샴 나쿠아', '규환과 증오', '용기로 가득한 자']

### 플레이어 2 손패 카드 목록
['진실의 기도자', '진실의 기도자', '불가사의한 철학자 필라소피라', '러블리 마스터피스', '불가사의한 철학자 필라소피라', '허구의 술식', '만식의 아나테마 라라안셈', '갈증의 감로']

### 플레이어 1 필드 카드 목록
['악랄한 레서 미라', '잔학한 전쟁 라우라', '어둠의 섭리 페디엘']

### 플레이어 2 필드 카드 목록
['만식의 아나테마 라라안셈', '차밍 몬스터', '갈증의 현현 기르네리제']

## 3 상세 트레이스백 정보
```text
Traceback (most recent call last):
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 306, in run_fuzzing
    validate_game_state_invariants(game)
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^^^^^^
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 224, in validate_game_state_invariants
    raise AssertionError(f"초진화 추종자 {card.get_display_name()} (ID {card.card_id})의 max_defense({card.max_defense})가 기본 스탯 상승폭인 +3 미만입니다.")
AssertionError: 초진화 추종자 갈증의 현현 기르네리제 (ID 61)의 max_defense(2)가 기본 스탯 상승폭인 +3 미만입니다.

```
