#!/bin/python
import os
import re
import subprocess
import sys

from github import Github


class LintError:
    def __init__(self, filename, error):
        self.filename = filename
        self.error = error
        self._comment = []
        self._formatted_comment = None
        self._code = None

    @property
    def code(self):
        if self._code is None:
            self._code = '\n'.join(self._comment[:-1])
        return self._code

    @property
    def comment(self):
        if self._formatted_comment is None:
            comments = '\n'.join(self._comment)
            self._formatted_comment = f"""
{self.error}
```
{comments}
```
"""
        return self._formatted_comment

    def add_comment_line(self, line):
        self._comment.append(line)


def already_commented(file, diff_index, body, comments):
    for comment in comments:
        if file.filename == comment.path and diff_index == comment.position and body == comment.body:
            return True
    return False


def parse_shellcheck(outs):
    filename = None
    line_no = None
    errors = None
    comments = []
    errors_ref = {}
    gathering_information = False

    for line in outs.split("\n"):
        match = re.match(r'In (.*) line (\d+)', line)
        if match:
            filename, line_no = match.group(1, 2)
            errors = []
        elif line == "For more information:":
            gathering_information = True
        elif gathering_information:
            error_code = re.match(r'.*wiki/(.*) --.*', line).group(1)
            errors_ref[error_code] = line
        elif line.strip():
            try:
                errors.append(line)
            except AttributeError:
                print(line)
                raise
        elif filename:
            comments.append((filename, line_no, ["```"] + errors + ["```"]))
            filename = None

    for error_code, error_ref in errors_ref.items():
        for comment in comments:
            if error_code in ''.join(comment[2][1:]):
                if "For more information:" not in comment[2][1:]:
                    comment[2].append("For more information:")
                comment[2].append(error_ref)

    return comments


default_parameters = {
    "shellcheck": "$(shfmt -f .) -e SC2148"
}


def main():
    available_linters = {name: func for name, func in globals().items() if name.startswith("parse_")}
    linters = os.environ.get('INPUT_LINTERS').split()

    invalid_linters = [linter for linter in linters if f"parse_{linter}" not in available_linters]
    if invalid_linters:
        if len(invalid_linters) == 1:
            print(f"Linter '{invalid_linters[0]}' is not available.")
        else:
            print(f"Linters {', '.join(invalid_linters)} are not available.")
        print(f"Available linters: {', '.join([l.replace('parse_', '') for l in available_linters.keys()])}")

    final_returncode = 0
    comments = []
    for linter in linters:
        print(f"::group::Running {linter}")
        parameters = os.environ.get(f"INPUT_{linter.upper()}_PARAMETERS", "")
        cmd = f"{linter} {default_parameters[linter]} {parameters}"
        print(cmd)
        returncode, outs = subprocess.getstatusoutput(cmd)
        print(outs)
        final_returncode = final_returncode or returncode
        comments.extend(available_linters[f"parse_{linter}"](outs))
        print('::endgroup::')

    gh = Github(os.environ['GITHUB_TOKEN'])
    repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
    prs = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])
    if prs:
        pr = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])[0]
        commit = list(pr.get_commits())[-1]
        pr_comments = [comment.body for comment in pr.get_comments()]
        for comment in comments:
            filename, line_no, error_comment = comment
            if isinstance(error_comment, list):
                error_comment = "\n".join(error_comment)
            if error_comment not in pr_comments:
                pr.create_review_comment(error_comment, commit, filename, int(line_no))

    exit(final_returncode)


main()
