#!/bin/python
import os
import re
import subprocess

from github import Github


def already_commented(file, diff_index, body, comments):
    for comment in comments:
        if file.filename == comment.path and diff_index == comment.position and body == comment.body:
            return True
    return False


def run_flake():
    flake_cmd = 'flake8 --show-source ' + os.environ['INPUT_FLAKE_PARAMETERS']
    print(flake_cmd)
    returncode, outs = subprocess.getstatusoutput(flake_cmd)
    print(outs)
    return outs, returncode


def generate_comments(outs):
    splitted_outs = outs.split('\n')
    lines_with_errors = {}
    for errors_index in range(0, len(splitted_outs), 3):
        if splitted_outs[errors_index]:
            info = re.search(r'(?P<path>.*?):(?P<line>\d*):\d*: *(?P<error>.*)',
                             splitted_outs[errors_index]).groupdict()
            lwe = lines_with_errors.get(info['line'], {})
            lwe['errors'] = lwe.get('errors', []) + [info['error']]
            lwe['code'] = splitted_outs[errors_index + 1].strip()
            lines_with_errors[info['line']] = lwe
    return lines_with_errors


def main():
    print('::group::Flake8')
    outs, returncode = run_flake()
    lines_with_errors = generate_comments(outs)

    gh = Github()
    repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
    pr = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])[0]
    commit = list(pr.get_commits())[-1]
    comments = [comment for comment in pr.get_comments() if comment.user.login == 'github-actions[bot]']

    for file in pr.get_files():
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
