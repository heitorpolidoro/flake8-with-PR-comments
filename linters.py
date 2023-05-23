#!/bin/python
import json
import os
import subprocess
from json import JSONDecodeError
from string import Template

import requests
from github import Github

from models.comment import Comment
from models.parsers import available_linters


def _request(method, url, headers, data=None):
    resp = requests.request(method, url, data=data, headers=headers)

    try:
        resp.raise_for_status()
        return json.loads(resp.content)
    except JSONDecodeError:
        return resp.content
    except Exception:
        print(json.loads(resp.content))
        raise


def _get(url, headers):
    return _request('get', url, headers)


def _post(url, data, headers):
    return _request('post', url, headers, data)


def gitlab_action_group(info):
    def decorator(func):
        def wrapper(*args, **kwargs):
            info_ = info
            if "$" in info_:
                info_ = Template(info).safe_substitute(**kwargs)
            arg_index = 0
            while "$" in info_ and arg_index < len(args):
                info_ = Template(info_).safe_substitute(**{f"arg{arg_index}": args[arg_index]})
            print(f"::group::{info_}")
            resp = func(*args, **kwargs)
            print('::endgroup::')
            return resp

        return wrapper

    return decorator


default_parameters = {
    "shellcheck": "$(shfmt -f .) -e SC2148 -f json",
    "shfmt": "-d .",
    "flake8": "",
}


def main():
    linters = os.environ.get('INPUT_LINTERS').split()

    invalid_linters = [linter for linter in linters if linter not in available_linters]
    if invalid_linters:
        if len(invalid_linters) == 1:
            print(f"Linter '{invalid_linters[0]}' is not available.")
        else:
            print(f"Linters {', '.join(invalid_linters)} are not available.")
        print(f"Available linters: {', '.join([l.replace('parse_', '') for l in available_linters.keys()])}")
        exit(1)

    final_returncode = 0
    comments = []
    for linter in linters:
        linter_returncode, linter_comments = run_linter(linter)
        final_returncode = final_returncode or linter_returncode
        comments.extend(linter_comments)

    if comments:
        token = os.environ['GITHUB_TOKEN']
        gh = Github(token)
        repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
        prs = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])

        if prs:
            do_comment(comments, prs[0], repo, token)

    exit(final_returncode)


@gitlab_action_group('Running $arg0')
def run_linter(linter):
    parameters = os.environ.get(f"INPUT_{linter.upper()}_PARAMETERS", "")
    cmd = f"{linter} {parameters} {default_parameters.get(linter, '')}"
    print(cmd)
    returncode, outs = subprocess.getstatusoutput(cmd)
    comments = available_linters[linter].parse(outs)
    return returncode, comments


@gitlab_action_group('Commenting')
def do_comment(comments, pr, repo, token):
    commit = list(pr.get_commits())[-1]
    pr_comments = [comment.body for comment in pr.get_comments()]
    for comment in comments:
        com = Comment(repo, pr, token, commit.sha, **comment)
        if com.comments not in pr_comments:
            com.post()


main()
