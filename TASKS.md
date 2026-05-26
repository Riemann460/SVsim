# TASKS: 문장 효과(Crest) 및 미구현 키워드 도입과 DB 분석

## 1. DB Merge and Unimplemented Keywords Listing
- [x] 1.1 현재 구현된 키워드와 미구현 키워드 분류를 검증하는 실패하는 테스트 코드 작성 (e.g. `test_keyword_analysis.py`)
- [x] 1.2 전체 셋 데이터베이스 병합 실행 및 미구현 추가 키워드 목록 리포트 작성
- [x] 1.3 `enums.py`에 문장(`GAIN_CREST`), 융합(`FUSE`), 버리기(`DISCARD`) 관련 프로세스 및 이벤트 추가 정의
- [x] 1.4 분석 및 Enums 연동 테스트(`test_keyword_analysis.py`) 통과 확인 및 테스트 파일 정리

## 2. Crest Mechanism Implementation and Verification
- [ ] 2.1 문장 획득 및 리스너 작동을 검증하는 실패하는 테스트 코드 작성 (e.g. `test_crest.py`)
- [ ] 2.2 `Player` 모델에 `crests` 상태 추가 및 `EffectProcessor`에 `GAIN_CREST` 핸들러 구현
- [ ] 2.3 `test_crest.py` 통과 확인 및 테스트 파일 정리

## 3. Fuse and Discard Core Mechanics Implementation
- [ ] 3.1 융합 및 버리기 코어 로직의 동작을 검증하는 실패하는 테스트 코드 작성 (e.g. `test_fuse_discard.py`)
- [ ] 3.2 `main_game_logic.py` 및 `effect_processor.py`에 융합/버리기 관련 프로세스 구현
- [ ] 3.3 `test_fuse_discard.py` 통과 확인 및 테스트 파일 정리
