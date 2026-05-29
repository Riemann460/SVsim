# TASKS: 지연 바인딩으로 인한 AttributeError 해결 태스크 목록

## [완료된 태스크]
- [x] 1.1 에러가 발생했을 때의 스냅샷 시나리오를 재현하는 시나리오 단위 테스트(test_fuzz_crash_snapshot_scenario) 작성 및 검증 수행
- [x] 1.2 src/engine/main_game_logic.py의 _register_card_listeners 내 루프 람다의 지연 바인딩 버그 수정
- [x] 1.3 pytest를 다시 실행하여 모든 기존 테스트 및 새로 추가된 시나리오 재현 테스트가 정상 통과하는지 확인
- [x] 1.4 변경된 코드에 대한 의미 있는 최소 단위의 Git 커밋 수행

## [진행 예정 태스크]
