import subprocess
import tempfile
import os

def run(code):
    with tempfile.NamedTemporaryFile(suffix=".c", delete=False) as c_file:
        c_file.write(code.encode())
        c_file_name = c_file.name

    exe_file = c_file_name.replace(".c", ".exe")

    subprocess.run(["gcc", c_file_name, "-o", exe_file])
    subprocess.run([exe_file])

    os.remove(c_file_name)
    os.remove(exe_file)
