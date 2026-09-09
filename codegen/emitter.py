import os

class CodeEmitter:
    def __init__(self, build_dir="build"):
        self.build_dir = build_dir

        if not os.path.exists(self.build_dir):
            os.makedirs(self.build_dir)

    def write_c_file(self, code, filename="query.c"):
        path = os.path.join(self.build_dir, filename)

        with open(path, "w") as f:
            f.write(code)

        return path