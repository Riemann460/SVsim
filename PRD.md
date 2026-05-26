# PRD: 더미 파일 정리 및 시뮬레이터 기능 검증 (Follow-up)

## 1. 개요
- **목적**: 깃허브 잔디 심기용 일일 더미 커밋 관련 파일을 완전히 삭제하여 저장소를 정리하고, 현재까지 구현된 Shadowverse Simulator (`SVsim`)의 기능을 분석 및 검증(Follow-up)한다.
- **대상 프로젝트**: `SVsim`

## 2. 요구사항
- **더미 파일 제거**:
  - `dummy.txt`, `update_dummy.py`, `test_update_dummy.py`, `test_git_stage.py`, `test_git_commit.py` 파일을 로컬 및 Git 저장소에서 완전히 삭제한다.
  - 삭제 이력을 Git에 반영한다 (커밋 메시지: `chore: remove daily dummy commit files and tests`).
- **기능 검증 (Follow-up)**:
  - 현재 시뮬레이터의 구현 구조를 파악하고, 핵심 동작(턴 진행, PP/EP/SEP 관리, 카드 드로우, 플레이, 진화/초진화, 전투, 카드 효과 트리거 등)의 정상 작동 여부를 검증한다.
  - 시뮬레이터 실행 파일(`main.py`)이 오류 없이 정상 작동하는지 확인한다.

## 3. 상세 사양
- **삭제 대상 목록**:
  - `SVsim/dummy.txt` [DELETE]
  - `SVsim/update_dummy.py` [DELETE]
  - `SVsim/test_update_dummy.py` [DELETE]
  - `SVsim/test_git_stage.py` [DELETE]
  - `SVsim/test_git_commit.py` [DELETE]
- **기능 분석 및 문서화**:
  - 현재 구현된 아키텍처 및 메커니즘을 파악하여 분석 보고서 형식으로 작성하거나 가이드한다.

## 4. 예상 난관 및 논리적 대응
- **난관**: `dummy.txt`가 이미 Git에 추적되고 있어 단순 파일 삭제 시 Git status 상에 변동이 남아있게 됨.
  - **대응**: `git rm` 명령을 사용하거나 로컬 파일 삭제 후 `git add -A` 및 `git commit`을 진행하여 완전히 반영함.
- **난관**: `tkinter` 기반 GUI가 환경 요인(예: GUI 환경 미지원 등)으로 인해 테스트/실행 단계에서 차단될 수 있음.
  - **대응**: GUI 실행이 불가한 경우를 대비하여, GUI를 Mocking하거나 게임 엔진 자체의 단위 테스트 또는 콘솔 실행 스크립트를 통해 코어 로직의 정상 여부를 검증함.

## 5. 진행 상황
- [x] 1. Delete Dummy Files and Commit (2026-05-26 완료)
- [x] 2. Core Game Logic and GUI Follow-up Verification (2026-05-26 완료)
