# Runner for 28 R101 Remediation Tests
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../02_SOURCE_CODE")))
from test_phase05b_engines import TestPhase05BRunner

if __name__ == "__main__":
    runner = TestPhase05BRunner()
    tests = [getattr(runner, m) for m in sorted(dir(runner)) if m.startswith("test_r101_")]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"[PASS] {t.__name__}")
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
    print(f"R101 Remediation Tests: {passed}/{len(tests)} PASSED")
    sys.exit(0 if passed == len(tests) else 1)
