import os.path
import re
from collections import defaultdict

from parsers.parser import LinterParser


class BlackParser(LinterParser):
    cmd = "black"
    default_parameters = "--diff ."

    @classmethod
    def parse(cls, input_str):
        comments = defaultdict(list)
        reading_file = False
        # original = ""
        suggestion = ""
        file = None
        start_line = 0
        end_line = 0
        for line in input_str.split("\n"):
            line = line + "\n"
            if reading_file:
                if line[0] == "@":
                    start_line, end_line = [
                        int(n) for n in re.match(r"@@ -(\d+),(\d+)", line).groups()
                    ]
                    continue
                if line[0] == "+":
                    suggestion += line[2:]
                if line[0] in ["-", " "]:
                    end_line += 1
                if line[0] not in ("+", "-", " "):
                    reading_file = False
                    comments[file].append(
                        {
                            "start_line": start_line,
                            "line": end_line,
                            "comment": suggestion,
                        }
                    )
            elif match := re.match(r"\+\+\+\s+(.*)\t+", line):
                file = os.path.relpath(match.group(1), ".")
                reading_file = True

        return comments
