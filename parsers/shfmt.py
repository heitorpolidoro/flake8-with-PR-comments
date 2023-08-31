import re
import subprocess

from parsers.parser import LinterParser


class ShfmtParser(LinterParser):
    cmd = "shfmt"
    default_parameters = "-d ."
    install_cmd = "snap install shfmt"

    @classmethod
    def parse(cls, output_dict):
        comments = {}
        for file, output_str in output_dict.items():
            output_splited = re.split(r"(@@.*?@@\n)", output_str, flags=re.DOTALL)[1:]
            chunks = []
            for index in range(0, len(output_splited), 2):
                lines_diff, suggestion = output_splited[index: index + 2]
                start = int(
                    re.search(r"@@.*-(?P<start>\d+),\d+", lines_diff).groupdict()[
                        "start"
                    ]
                )
                chunk = {}  # type: dict[str, Any]
                suggestion_split = suggestion.split("\n")
                line_num = 0
                while line_num < len(suggestion_split):
                    line = suggestion_split[line_num]
                    if line.startswith("-") and not chunk.get("start_line"):
                        chunk["start_line"] = line_num + start
                    elif line.startswith("-") and chunk.get("start_line"):
                        chunk["line"] = line_num + start
                    elif line.startswith("+"):
                        chunk["comment"] = chunk.get("comment", "") + line[1:] + "\n"
                    elif chunk:
                        chunks.append(chunk)
                        chunk = {}
                    line_num += 1
                if suggestion_split[-1].startswith("+"):
                    chunks.append(chunk)
            comments[file] = [dict(as_suggestion=True, **chunk) for chunk in chunks]

        return comments

    @classmethod
    def _inner_run(cls, cmd):
        status, files = subprocess.getstatusoutput("shfmt -f .")
        return_str = {}
        for file in files.split("\n"):
            output_status, output_str = subprocess.getstatusoutput(
                f"cat {file} | {cmd}"
            )
            status = status or output_status
            return_str[file] = output_str

        return status, return_str
