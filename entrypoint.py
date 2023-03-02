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


# def parse_flake():
#     flake_cmd = 'flake8 --show-source ' + os.environ.get('INPUT_FLAKE_PARAMETERS', '')
#     print(flake_cmd)
#     returncode, outs = subprocess.getstatusoutput(flake_cmd)
#     print(outs)
#     lint_error = None
#     errors = {}
#     for line in outs.split('\n'):
#         if line.startswith('./'):
#             if lint_error:
#                 errors[lint_error.filename] = errors.get(lint_error.filename, []) + [lint_error]
#             info = re.search(r'\./(?P<path>.*?):\d*:\d*: *(?P<error>.*)', line).groupdict()
#             lint_error = LintError(info['path'], info['error'])
#         elif lint_error:
#             lint_error.add_comment_line(line)
#     if lint_error:
#         errors[lint_error.filename] = errors.get(lint_error.filename, []) + [lint_error]
#
#     return errors, bool(returncode)

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
            errors.append(line)
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
    "shellcheck": "$(shfmt -f .)"
}


def main():
    available_linters = {name: func for name, func in globals().items() if name.startswith("parse_")}
    linters = os.environ.get('INPUT_LINTERS').split()



    invalid_linters = [l for l in linters if l not in available_linters]
    if invalid_linters:
        if len(invalid_linters) == 1:
            print(f"Linter {invalid_linters[0]} is not available.")
        else:
            print(f"Linters {', '.join(invalid_linters)} are not available.")
        print(f"Available lints: {', '.join([l.replace('parse_', '') for l in available_linters.keys()])}")

    final_returncode = 0
    comments = []
    for linter in linters:
        print(f"::group::{linter}")
        parameters = os.environ.get(f"INPUT_{linter}_PARAMETERS", "")
        cmd = f"{linter} {default_parameters[linter]} {parameters}"
        print(cmd)
        returncode, outs = subprocess.getstatusoutput(cmd)
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
        comments = [c for c in comments if c[2] not in pr_comments]
        for comment in comments:
            filename, line_no, error_comment = comment
            if isinstance(error_comment, list):
                error_comment = "\n".join(error_comment)
            pr.create_review_comment("body", commit, filename, int(line_no))
            pr.create_review_comment(error_comment, commit, filename, int(line_no))



        # for file in pr.get_files():
        #     for diff_index, diff_code in enumerate(file.patch.split('\n')):
        #         print(file.filename)
        #         if file.filename == "entrypoint.sh":
        #             print(file.filename, diff_index, diff_code)
        #             pr.create_review_comment("body", commit, file.filename, 2)
        #             exit()
        #             if diff_code[0] == '+':
        #                 for error in errors[file.filename]:
        #                     if error.code == diff_code[1:]:
        #                         body = error.comment
        #                         if not already_commented(file, diff_index, body, comments):
        #                             pr.create_review_comment(body, commit, file.filename, diff_index)
    # print('::endgroup::')
    # exit(fail)


main()
