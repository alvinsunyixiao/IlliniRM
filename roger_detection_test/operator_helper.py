import subprocess

recog_py_path = "real_program.py"
command = ["python", recog_py_path]

while True:
    raw_input("Press enter to recognize current hit location")
    output = subprocess.check_output(command)
    print output
