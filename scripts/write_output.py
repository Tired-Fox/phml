from subprocess import Popen

command = "mypy phml"
with open("result.txt", "+w", encoding="utf-8") as output:
    sub = Popen(command, stdout=output)
    sub.wait()
