# 역할 정의. 퍼징 시뮬레이션의 정상 구동과 예외 처리 흐름을 검증하는 단위 테스트 클래스입니다.

import unittest
from fuzz_runner import run_fuzzing


class TestFuzzRunner(unittest.TestCase):
    """퍼징 시뮬레이션을 검증하는 테스트 클래스입니다."""

    def test_run_fuzzing_one_session(self):
        """퍼징 시뮬레이션 1회가 오류 없이 작동하는지 검증합니다."""
        success, error = run_fuzzing(runs=1, max_turns=5)
        self.assertTrue(success)
        self.assertIsNone(error)
