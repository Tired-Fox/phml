from pathlib import Path
from subprocess import Popen, PIPE
import phml as module

from badges import *

if __name__ == "__main__":
    from tempfile import TemporaryFile
    from re import search, finditer

    project = "phml"
    primary = "9cf"

    project_badges: list[tuple[str, str, Parameters]] = [
        (
            "version",
            Create.badge("verson", str(module.__version__), "9cf"),
            {"style": "flat-square", "logo": "aiohttp", "logoColor": "white"},
        ),
        (
            "license",
            f"github/license/tired-fox/{project}.svg",
            {"style": "flat-square", "color": primary}
        ),
        (
            "maintained",
            "badge/Maintained%3F-yes-2CBA00.svg",
            {"style": "flat-square"}
        ),
        (
            "documentation",
            "badge/view-Documentation-blue",
            {"style": "for-the-badge"}
        ),
        (
            "built_with_love",
            "badge/Built_With-❤-D15D27",
            {"style": "for-the-badge", "labelColor": "E26D25"}
        ),
    ]

    def _get_test_links() -> list[tuple[Name, Url]]:
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

    for badge in project_badges:
        badges.badge(*badge)

    badges.collect("assets/badges/")
    header_badges = f"""
<!-- Header Badges -->

<div align="center">
  
![version](assets/badges/version.svg)
[![License](assets/badges/license.svg)](https://github.com/Tired-Fox/{project}/blob/main/LICENSE)
[![Release](https://img.shields.io/github/v/release/tired-fox/{project}.svg?style=flat-square&color=9cf)](https://github.com/Tired-Fox/phml/releases)
[![Issues](https://img.shields.io/github/issues/tired-fox/{project}.svg?style=flat-square&color=9cf)](https://github.com/Tired-Fox/phml/issues)
[![Pull Requests](https://img.shields.io/github/issues-pr/tired-fox/{project}.svg?style=flat-square&color=9cf)](https://github.com/Tired-Fox/phml/pulls)

![Maintained](assets/badges/maintained.svg)
![testing](assets/badges/tests.svg)
![test coverage](assets/badges/coverage.svg)
  
<!-- !PERF: Make sure to edit this lines link! -->
[![view - Documentation](assets/badges/documentation.svg)](https://tired-fox.github.io/{project}/phml.html 'Go to project documentation')
  
</div>

<!-- End Badges -->
"""
    footer_badges = """\
<!-- Footer Badges --!>

<br>
<div align="center">

  ![Made with Python](assets/badges/made_with_python.svg)
  ![Built with love](assets/badges/built_with_love.svg)

</div>

<!-- End Badges -->\
"""
    print("Copying badge: made_with_python")
    Path("assets/badges/made_with_python.svg").write_text(PRESETS["made_with_python"])

    print(header_badges)
    print(footer_badges)

