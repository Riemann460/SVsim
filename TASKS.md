# TASKS: 지연 바인딩으로 인한 AttributeError 해결 태스크 목록

## [완료된 태스크]
- [x] 1.1 `tests/test_card_loader.py`에 복수의 효과(`ENHANCE` 및 타 효과)를 갖는 카드를 생성하여 플레이 시 `enhance_cost` 에러를 재현하는 실패하는 테스트 코드 작성
- [x] 1.2 `pytest`를 실행하여 새로 추가한 테스트 코드가 정상적으로 실패(AttributeError 검출)하는지 확인
- [x] 2.1 `src/engine/main_game_logic.py`의 `_register_card_listeners` 내 루프 람다의 지연 바인딩 버그 수정
- [x] 2.2 `pytest`를 다시 실행하여 모든 기존 테스트 및 재현 테스트가 통과하는지 확인
- [x] 3.1 `SKILL.md` 원칙에 따라 TDD 재현을 위해 임시 추가한 테스트 코드는 파일에서 제거

## [진행 예정 태스크]
- [ ] 3.2 변경된 코드에 대한 의미 있는 최소 단위의 Git 커밋 수행
- [ ] 3.3 `fuzz_runner.py`를 실행하여 안정적으로 동작하는지 확인

