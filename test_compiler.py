from compiler.asm_generator import ASMGenerator
from compiler.linker import Linker
import os

def test_compiler():
    build_dir = "build"
    c_file = "query.c"

    c_path = os.path.join(build_dir, c_file)

    if not os.path.exists(c_path):
        print("ERROR: build/query.c not found.")
        print("Run test_codegen.py first.")
        return

    try:
        print("\nGenerating Assembly...")
        asm_generator = ASMGenerator(build_dir)
        asm_path = asm_generator.generate_assembly(c_file)

        print("Assembly file created:")
        print(asm_path)

        print("\nBuilding Executable...")
        linker = Linker(build_dir)
        exe_path = linker.build_executable(c_file)

        print("Executable created:")
        print(exe_path)

        print("\nCOMPILER TEST SUCCESS")

    except Exception as e:
        print("\nCOMPILER ERROR:", e)

if __name__ == "__main__":
    test_compiler()