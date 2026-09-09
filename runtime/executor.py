import subprocess
import os

class RuntimeExecutor:
    def __init__(self, build_dir="build"):
        self.build_dir = build_dir

    def run(self, executable="query_exec"):

        if os.name == 'nt' and not executable.endswith('.exe'):
            executable += '.exe'

        exe_path = os.path.join(self.build_dir, executable)

        if not os.path.exists(exe_path):
            raise FileNotFoundError(f"Executable not found: {exe_path}")

        os.chmod(exe_path, 0o755)

        try:
            result = subprocess.run(
                [exe_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            print(result.stdout)

            if result.stderr:
                print("Runtime error:")
                print(result.stderr)

        except Exception as e:
            print("Execution failed:", e)