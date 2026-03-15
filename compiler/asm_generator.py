import subprocess
import os

class ASMGenerator:
    def __init__(self, build_dir="build"):
        self.build_dir = build_dir

        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)

    def generate_assembly(self, c_file="query.c"):
        c_path = os.path.join(self.build_dir, c_file)
        asm_path = os.path.join(self.build_dir, "query.s")

        command = [
            "gcc",
            "-S",
            c_path,
            "-o",
            asm_path
        ]

        try:
            subprocess.run(command, check=True)
        except subprocess.CalledProcessError:
            raise RuntimeError("Assembly generation failed")

        return asm_path