import json
import subprocess

from parsers.parser import LinterParser


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
                message += "{0: >{size}}".format("^", size=output["column"])
                env_column_char = "^"
                end_column = output["endColumn"] - output["column"] - 1
                if end_column <= 0:
                    end_column = 2
                    env_column_char = "-"
                message += "{0:->{size}}".format(env_column_char, size=end_column)
                message += f" {output['message']}"
                file_comments.append(
                    {
                        "line": output["line"],
                        "comment": message,
                    }
                )
            comments[file] = file_comments
        return comments

    @classmethod
    def _inner_run(cls, cmd):
        status, files = subprocess.getstatusoutput("shfmt -f .")
        return_json = {}
        for file in files.split("\n"):
            output_status, output_json = subprocess.getstatusoutput(f"{cmd} {file}")
            status = status or output_status
            return_json[file] = json.loads(output_json)

        return status, return_json
