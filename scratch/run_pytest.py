import subprocess
import sys

res = subprocess.run(
    [sys.executable, "-m", "pytest", "tests/test_scenario_builder.py", "-k", "test_slaus_random_ability_activation", "--tb=long"],
    capture_output=True,
    text=True,
    encoding="cp949",
    errors="replace"
)
stdout = res.stdout
idx = stdout.find("FAILURES")
if idx != -1:
    print("FOUND FAIL SEGMENT:")
    print(stdout[idx:idx+6000])
else:
    print("NO FAIL SEGMENT FOUND, PRINTING ALL:")
    print(stdout)
