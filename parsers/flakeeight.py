from collections import defaultdict

from parsers.parser import LinterParser


class Flake8Parser(LinterParser):
    cmd = "flake8"
    default_parameters = (
        "--format='%(path)s|SEP|%(row)s|SEP|%(col)s|SEP|%(code)s %(text)s'"
    )

    @classmethod
    def parse(cls, input_str):
        comments = defaultdict(list)
        for line in input_str.split("\n"):
            if line:
                file, line, column, message = line.split("|SEP|")
                message = "\n{0: >{size}}".format(f"^-- {message}", size=column)

                if file.startswith("./"):
                    file = file[2:]
                comments[file].append(
                    {
                        "line": int(line),
                        "comment": message,
                    }
                )

        return comments
