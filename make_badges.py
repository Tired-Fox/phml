from subprocess import Popen, PIPE
import phml as module

from badges import *

if __name__ == "__main__":
    from tempfile import TemporaryFile
    from re import search, finditer

    @badge(project="phml")
    def _get_test_links(project: str) -> list[tuple[Name, Url]]:
        passed, total, covered = 0, 0, 0
        with TemporaryFile() as file:
            data = Popen(f'pytest --cov="./{project}" tests/', stdout=file, stderr=PIPE)
            data.wait()
            file.seek(0)
            output = file.read().decode("utf-8")

        for line in output.split("\n"):
            if search(r"TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%", line) is not None:
                _, _, covered = search(r"TOTAL\s+(\d+)\s+(\d+)\s+(\d+)%", line).groups()
                covered = int(covered)
            elif search(r"(failed|passed)", line) is not None:
                for status in finditer(r"\s(\d{1,})\s(?!warning)([a-z]+),?", line):
                    count, condition = status.groups()
                    if condition == "passed":
                        passed = int(count)
                    total += int(count)

        test_link = sheild_io_link(
            Create.badge(
                "tests",
                f"{passed}/{total}",
                Color.percentage(passed / total if passed > 0 else 0),
            ),
            {
                "style": "flat-square",
                "logo": "testcafe",
                "logoColor": "white",
            },
        )

        test_cov_link = sheild_io_link(
            Create.badge("coverage", f"{covered}%25", Color.percentage(covered / 100)),
            {
                "style": "flat-square",
                "logo": "codeforces",
                "logoColor": "white",
            },
        )

        return [("tests", test_link), ("coverage", test_cov_link)]

    badges = Badges(_get_test_links)
    badges.badge(
        "version",
        Create.badge("verson", str(module.__version__), "9cf"),
        {"style": "flat-square", "logo": "aiohttp", "logoColor": "white"},
    )

    badges.collect('assets/badges/')
