# TASKS: 문장 효과(Crest) 및 미구현 키워드 도입과 DB 분석

## 1. DB Merge and Unimplemented Keywords Listing
- [x] 1.1 현재 구현된 키워드와 미구현 키워드 분류를 검증하는 실패하는 테스트 코드 작성 (e.g. `test_keyword_analysis.py`)
- [x] 1.2 전체 셋 데이터베이스 병합 실행 및 미구현 추가 키워드 목록 리포트 작성
- [x] 1.3 `enums.py`에 문장(`GAIN_CREST`), 융합(`FUSE`), 버리기(`DISCARD`) 관련 프로세스 및 이벤트 추가 정의
- [x] 1.4 분석 및 Enums 연동 테스트(`test_keyword_analysis.py`) 통과 확인 및 테스트 파일 정리

## 2. Crest Mechanism Implementation and Verification
- [x] 2.1 문장 획득 및 리스너 작동을 검증하는 실패하는 테스트 코드 작성 (e.g. `test_crest.py`)
- [x] 2.2 `Player` 모델에 `crests` 상태 추가 및 `EffectProcessor`에 `GAIN_CREST` 핸들러 구현
- [x] 2.3 `test_crest.py` 통과 확인 및 테스트 파일 정리

## 3. Card Parsing Rate Optimization (Success rate >= 90%)
- [x] 3.1 파싱 성공률 측정 환경(check_parsing_rate.py) 구축 및 전체 데이터베이스(100~107, 900 팩) 대상 Baseline 통계 측정
- [x] 3.2 parse_script.py 내 전처리 로직 고도화 (HTML 태그 및 특수문자 제거 필터, 마침표 및 세미콜론 기준 문장 정밀 분할기 구현)
- [x] 3.3 미구현/미파싱 문장에 매칭되는 정규식 패턴 추가 (EFFECT_PATTERNS 및 ACTION_PATTERNS 추가)
- [x] 3.4 파싱 중 포착된 미구현 Action 및 Target 명칭을 수집하여 enums.py에 추가 정의하고 ADR-006 준수 주석 작성
- [x] 3.5 최종 데이터베이스 일괄 빌드 및 check_parsing_rate.py를 통한 최종 성공률 96.89% 검증 완료

## 4. Fuse and Discard Core Mechanics Implementation
- [ ] 4.1 융합 및 버리기 코어 로직의 동작을 검증하는 실패하는 테스트 코드 작성 (e.g. `test_fuse_discard.py`)
- [ ] 4.2 `main_game_logic.py` 및 `effect_processor.py`에 융합/버리기 관련 프로세스 구현
- [ ] 4.3 `test_fuse_discard.py` 통과 확인 및 테스트 파일 정리
