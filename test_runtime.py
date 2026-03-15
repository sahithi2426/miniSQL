from runtime.executor import RuntimeExecutor
import os

def test_runtime():
    build_dir = "build"
    executable = "query_exec.exe"

    exe_path = os.path.join(build_dir, executable)

    if not os.path.exists(exe_path):
        print("ERROR: executable not found.")
        print("Run test_compiler.py first.")
        return

    try:
        print("\nRunning executable...\n")

        runtime = RuntimeExecutor(build_dir)
        runtime.run(executable)

        print("\nRUNTIME TEST SUCCESS")

    except Exception as e:
        print("\nRUNTIME ERROR:", e)

if __name__ == "__main__":
    test_runtime()