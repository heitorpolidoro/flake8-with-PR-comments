#!/bin/python
import os
import re
import subprocess

from github import Github

class LintError:
    def __init__(self, filename, error):
        self.filename = filename
        self.error = error
        self._comment = []
        self._formated_comment = None
        self._code = None

    @property
    def code(self):
        if self._code is None:
            self._code = '\n'.join(self._comment[:-1])
        return self._code

    @property
    def comment(self):
        if self._formated_comment is None:
            comments = '\n'.join(self._comment)
            self._formated_comment = f"""
{self.error}
```
{comments}
```
"""
        return self._formated_comment

    def add_comment_line(self, line):
        self._comment.append(line)

def already_commented(file, diff_index, body, comments):
    for comment in comments:
        if file.filename == comment.path and diff_index == comment.position and body == comment.body:
            return True
    return False


def run_flake():
    flake_cmd = 'flake8 --show-source ' + os.environ.get('INPUT_FLAKE_PARAMETERS', '')
    print(flake_cmd)
    returncode, outs = subprocess.getstatusoutput(flake_cmd)
    print(outs)
    lint_error = None
    errors = {}
    for line in outs.split('\n'):
        if line.startswith('./'):
            if lint_error:
                errors[lint_error.filename] = errors.get(lint_error.filename, []) + [lint_error]
            info = re.search(r'\./(?P<path>.*?):\d*:\d*: *(?P<error>.*)', line).groupdict()
            lint_error = LintError(info['path'], info['error'])
        else:
            lint_error.add_comment_line(line)
    if lint_error:
        errors[lint_error.filename] = errors.get(lint_error.filename, []) + [lint_error]

    return errors, bool(returncode)


def main():
    print('::group::Flake8')
    errors, fail = run_flake()

    gh = Github(os.environ['GITHUB_TOKEN'])
    repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
    prs = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])
    if prs:
        pr = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])[0]
        commit = list(pr.get_commits())[-1]
        comments = [comment for comment in pr.get_comments() if comment.user.login == 'github-actions[bot]']

        for file in pr.get_files():
            if file.filename in errors:
                for diff_index, diff_code in enumerate(file.patch.split('\n')):
                    if diff_code[0] == '+':
                        for error in errors[file.filename]:
                            if error.code == diff_code[1:]:
                                body = error.comment
                                if not already_commented(file, diff_index, body, comments):
                                    pr.create_review_comment(body, commit, file.filename, diff_index)
    print('::endgroup::')
    exit(fail)


main()
