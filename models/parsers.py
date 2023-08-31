import json
import logging
import os
import re
import subprocess
from collections import defaultdict
from typing import Any

from github_actions_utils.log_utils import github_group


class LinterParser:
    cmd = ""
    default_parameters = ""

    @staticmethod
    def get_linter(linter):
        for l_ in LinterParser.__subclasses__():
            if l_.cmd == linter:
                return l_
        raise ValueError(f"Unknown linter: {linter}")

    @classmethod
    @github_group('Running $(cls.cmd)...')
    def run(cls):
        parameters = os.getenv(f"INPUT_{cls.cmd.upper()}_PARAMETERS", "")
        cmd = f"{cls.cmd} {parameters} {cls.default_parameters}"
        print(cmd)
        returncode, outs = cls._inner_run(cmd)
        comments = cls.parse(outs)
        return returncode, comments

    @classmethod
    def _inner_run(cls, cmd):  # pragma: no cover
        return subprocess.getstatusoutput(cmd)

    @classmethod
    def parse(cls, input_str):  # pragma: no cover
        raise NotImplementedError


class ShfmtParser(LinterParser):
    cmd = "shfmt"
    default_parameters = "-d ."

    @classmethod
    def parse(cls, output_dict):
        comments = {}
        for file, output_str in output_dict.items():
            output_splited = re.split(r"(@@.*?@@\n)", output_str, flags=re.DOTALL)[1:]
            chunks = []
            for index in range(0, len(output_splited), 2):
                lines_diff, suggestion = output_splited[index:index + 2]
                start = int(re.search(r"@@.*-(?P<start>\d+),\d+", lines_diff).groupdict()["start"])
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
            output_status, output_str = subprocess.getstatusoutput(f"cat {file} | {cmd}")
            status = status or output_status
            return_str[file] = output_str

        return status, return_str


class ShellCheckParser(LinterParser):
    cmd = "shellcheck"
    default_parameters = "-e SC2148 -f json"

    @classmethod
    def parse(cls, output_dict):
        comments = {}
        for file, output_json in output_dict.items():
            with open(file) as f:
                file_content = f.readlines()
            file_comments = []
            for output in output_json:
                message = file_content[output["line"] - 1]
                message += '{0: >{size}}'.format("^", size=output["column"])
                env_column_char = "^"
                end_column = output["endColumn"] - output["column"] - 1
                if end_column <= 0:
                    end_column = 2
                    env_column_char = "-"
                message += '{0:->{size}}'.format(env_column_char, size=end_column)
                message += f" {output['message']}"
                file_comments.append({
                    "line": output["line"],
                    "comment": message,
                })
            comments[file] = file_comments
        return comments

    @classmethod
    def _inner_run(cls, cmd):
        status, files = subprocess.getstatusoutput("shfmt -f .")
        return_json = {}
        for file in files.split("\n"):
            output_status, output_json = subprocess.getstatusoutput(f"{cmd} {file}")
            logging.debug(f"{output_status = } {output_json = }")
            status = status or output_status
            try:
                return_json[file] = json.loads(output_json)
            except json.decoder.JSONDecodeError:
                print(output_json)
                raise

        return status, return_json


class Flake8Parser(LinterParser):
    cmd = "flake8"

    @classmethod
    def parse(cls, input_str):
        comments = defaultdict(list)
        for line in input_str.split("\n"):
            if line:
                file, line, column, message = line.split(":")
                message = '\n{0: >{size}}'.format(f"^-- {message}", size=column)

                if file.startswith("./"):
                    file = file[2:]
                comments[file].append({
                    "line": int(line),
                    "comment": message,
                })

        return comments
