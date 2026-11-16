# Runner for 11 Architecture Alignment Tests
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../../02_SOURCE_CODE")))
from test_phase05b_engines import TestPhase05BRunner

if __name__ == "__main__":
    runner = TestPhase05BRunner()
    tests = [getattr(runner, m) for m in sorted(dir(runner)) if m.startswith("test_align_")]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
            print(f"[PASS] {t.__name__}")
        except Exception as e:
            print(f"[FAIL] {t.__name__}: {e}")
    print(f"Architecture Alignment Tests: {passed}/{len(tests)} PASSED")
    sys.exit(0 if passed == len(tests) else 1)
