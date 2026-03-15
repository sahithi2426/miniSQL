import subprocess
import os

class Linker:
    def __init__(self, build_dir="build"):
        self.build_dir = build_dir

    def build_executable(self, c_file="query.c", output="query_exec"):
        c_path = os.path.join(self.build_dir, c_file)
        
        if os.name == 'nt' and not output.endswith('.exe'):
            output += '.exe'
            
        exe_path = os.path.join(self.build_dir, output)

        command = [
            "gcc",
            c_path,
            "-o",
            exe_path
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            raise RuntimeError("Executable build failed")

        return exe_path