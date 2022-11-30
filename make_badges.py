import requests
from subprocess import Popen, PIPE
from tempfile import TemporaryFile
from re import search, finditer

def get_score(command: str) -> float:
    """Get pylint score"""

    with TemporaryFile() as file:
        data = Popen(command, stdout=file, stderr=PIPE)
        data.wait()
        file.seek(0)
        output = file.read().decode("utf-8")
        
    start = output.find("Your code has been rated at ")
    if start == -1:
        raise ValueError(f'Could not find quality score in "{output.rstrip()}".')

    start += len("Your code has been rated at ")
    end = start + output[start:].find("/")
    score = float(output[start:end])

    return score


def get_color(score: float) -> str:
    """Get color for shield"""

    if score < .6:
        return "critical"

    elif score < .8:
        return "orange"

    elif score < .9:
        return "yellow"

    elif score < .95:
        return "yellowgreen"

    else:
        return "brightgreen"
    
def get_test_color(score: float) -> str:

    if score < .6:
        return "critical"

    elif score < .8:
        return "orange"

    elif score < .9:
        return "yellow"

    elif score < 1:
        return "yellowgreen"

    else:
        return "brightgreen"


def create_link(label: str, score: float) -> str:
    """Create link using shields.io"""

    label = label.replace(" ", "_")
    color = get_color(score/10)
    return f"https://img.shields.io/badge/{label}-{score}-{color}"


def write_quality_badge(command: str, output_file: str) -> None:
    """Write badge for code quality"""

    score = get_score(command)
    link = create_link("code rating", score)

    with open(output_file, "wb") as output:
        data = requests.get(link).content
        output.write(data)


def write_version_badge(output_file: str) -> None:
    """Write badge for version badge"""

    from phml import __version__ as version

    link = f"https://img.shields.io/badge/version-{version}-9cf"

    with open(output_file, "wb") as output:
        data = requests.get(link).content
        output.write(data)

def get_test_results(command: str) -> tuple[int, int, int]:
    """Get pytest-cov results"""

    passed, total, covered = 0, 0, 0
    with TemporaryFile() as file:
        data = Popen(command, stdout=file, stderr=PIPE)
        data.wait()
        file.seek(0)
        output = file.read().decode("utf-8")
    
    for line in output.split("\n"):
        if search(r"TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%", line) is not None:
            stmnt, missed, covered = search(r"TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%", line).groups()
            covered = int(covered)
        elif search(r"(failed|passed)", line) is not None:
            for status in finditer(r"\s(\d{1,})\s([a-z]+),?", line):
                count, condition = status.groups()
                if condition == "passed":
                    passed = int(count)
                total += int(count)
                   
    return passed, total, covered

def write_test_badges(command: str, test_output: str, test_cov_output: str):
    
    passed, total, covered = get_test_results(command)
    
    test_link = f"https://img.shields.io/badge/testing-{passed}/{total}-{get_test_color(passed/total)}"
    test_cov_link = f"https://img.shields.io/badge/test_coverage-{covered}%25-{get_color(covered/100)}"

    with open(test_output, "wb") as output:
        data = requests.get(test_link).content
        output.write(data)
        
    with open(test_cov_output, "wb") as output:
        data = requests.get(test_cov_link).content
        output.write(data)
        
def main() -> None:
    """Main method"""

    write_quality_badge("pylint phml", "assets/badges/quality.svg")
    write_version_badge("assets/badges/version.svg")
    write_test_badges("make test", "assets/badges/testing.svg", "assets/badges/test_cov.svg")


if __name__ == "__main__":
    main()