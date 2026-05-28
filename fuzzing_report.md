# 퍼징 테스트 에러 분석 리포트

## 1 에러 기본 요약
- **에러 유형** AssertionError
- **에러 메시지** error.log 실시간 파싱 중 이상 에러 검출 - [ERROR] 임시 테스트 에러 로그가 출력되었습니다.

## 2 에러 발생 시점 게임 상태 스냅샷
- **현재 진행 턴** 1
- **현재 턴 플레이어** player1
- **플레이어 1 체력** 20 (PP 1)
- **플레이어 2 체력** 20 (PP 0)

### 플레이어 1 손패 카드 목록
['욕심쟁이 지천사 루비', '낙랑의 천궁 필도어', '신의 뇌정', '캐러밴 맘모스', '빛의 연주자 앙리에트']

### 플레이어 2 손패 카드 목록
['세찬 광명 아폴론', '고블린의 습격', '관찰하는 탐정', '신의 뇌정']

### 플레이어 1 필드 카드 목록
[]

### 플레이어 2 필드 카드 목록
[]

## 3 상세 트레이스백 정보
```text
Traceback (most recent call last):
  File "C:\Users\sys91\Documents\개발 프로젝트\SVsim\fuzz_runner.py", line 289, in run_fuzzing
    raise AssertionError(f"error.log 실시간 파싱 중 이상 에러 검출 - {logged_error}")
AssertionError: error.log 실시간 파싱 중 이상 에러 검출 - [ERROR] 임시 테스트 에러 로그가 출력되었습니다.

```
