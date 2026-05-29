# PRD: 이벤트 리스너 등록 시 지연 바인딩으로 인한 AttributeError 해결

## 1. 개요
- **목적**: 퍼징 시뮬레이션 및 실제 카드 플레이 중 `Enhance` 효과가 포함된 카드를 낼 때 발생하는 `AttributeError: 'Effect' object has no attribute 'enhance_cost'` 오류의 근본 원인을 해결합니다.
- **대상 파일**:
  - [main_game_logic.py](file:///C:/Users/sys91/Documents/개발 프로젝트/SVsim/src/engine/main_game_logic.py)
  - [test_card_loader.py](file:///C:/Users/sys91/Documents/개발 프로젝트/SVsim/tests/test_card_loader.py)

## 2. 요구사항 및 상세 사양
- **원인 제거**: 
  - `main_game_logic.py`의 `_register_card_listeners` 내 루프문에서 생성되는 `condition` 람다 함수들이 파이썬의 지연 바인딩(Late Binding) 특성으로 인해 루프 마지막의 `effect` 인스턴스를 공유하여 오류가 발생합니다.
  - 이를 해결하기 위해 루프 내 람다 선언 시 `eff=effect`와 같이 디폴트 아규먼트를 주어 해당 시점의 `effect`를 올바르게 바인딩하도록 강제합니다.
- **단위 테스트 작성**:
  - `tests/test_card_loader.py`에 복수의 효과(`ENHANCE` 및 `ENGAGE`)를 갖는 카드를 생성하여 플레이했을 때, `enhance_cost` 관련 `AttributeError` 예외 없이 정상적으로 이벤트 리스너가 호출되고 처리되는지 검증하는 실패하는 테스트 코드를 추가합니다.

## 3. 주석 및 서식 규칙
- 코드 변경 시 모든 주석은 한글로 작성하고 온점(".")으로 끝맺어야 하며, 콜론(":")은 사용하지 않습니다.
