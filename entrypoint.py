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

    @property
    def code(self):
        return '\n'.join(self._comment[:-1])

    @property
    def comment(self):
        return '\n'.join(self._comment)

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
    # code = False
    lint_error = None
    errors = []
    for line in outs.split('\n'):
        if line.startswith('./'):
            if lint_error:
                errors.append(lint_error)
            info = re.search(r'\./(?P<path>.*?):\d*:\d*: *(?P<error>.*)', line).groupdict()
            lint_error = LintError(info['path'], info['error'])
            # code = True
        else:
            lint_error.add_comment_line(line)

    return errors, bool(returncode)


def generate_comments(outs):
    splitted_outs = outs.split('\n')
    comments = {}
    # lines_with_errors = {}
    for errors_index in range(0, len(splitted_outs), 3):
        if splitted_outs[errors_index]:
            info = re.search('(?P<path>.*?):(?P<line>\d*):\d*: *(?P<error>.*)',
                             splitted_outs[errors_index])
            if info:
                info_dict = info.groupdict()
                cmt = f"""{info_dict['error']}
```
{splitted_outs[errors_index + 1]}
{splitted_outs[errors_index + 2]}
```"""
                comments[info_dict.path] = comments.get(info_dict.path, []) + [cmt]
    #             lwe = lines_with_errors.get(info_dict['line'], {})
    #             lwe['errors'] = lwe.get('errors', []) + [info_dict['error']]
    #             lwe['code'] = splitted_outs[errors_index + 1].strip()
    #             lines_with_errors[info_dict['line']] = lwe
    # return lines_with_errors


def main():
    print('::group::Flake8')
    errors, fail = run_flake()
    # lines_with_errors = generate_comments(outs)

    gh = Github(os.environ['GITHUB_TOKEN'])
    repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
    prs = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])
    if prs:
        pr = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])[0]
        commit = list(pr.get_commits())[-1]
        comments = [comment for comment in pr.get_comments() if comment.user.login == 'github-actions[bot]']

        for file in pr.get_files():
            if file.status == 'removed':
                continue
            for diff_index, diff_code in enumerate(file.patch.split('\n')):
                if diff_code[0] == '+':
                    for lwe in lines_with_errors.values():
                        if lwe['code'] == diff_code[1:].strip():
                            body = '\n'.join(lwe['errors'])
                            if not already_commented(file, diff_index, body, comments):
                                pr.create_review_comment(body, commit, file.filename, diff_index)
    print('::endgroup::')
    exit(returncode)


main()
