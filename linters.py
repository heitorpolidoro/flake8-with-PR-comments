#!/bin/python
import json
import inspect
import os
import re
import subprocess
from json import JSONDecodeError
from string import Template

import requests
from github import Github

from models.comment import Comment
from models.parsers import available_linters


def gitlab_group(group_name):
    def wrapper(f):
        params = []
        for var in re.findall(r'\$(\w+)', group_name):
            if var in inspect.signature(f).parameters:
                params.append(var)

        def inner_wrapper(*args, **kwargs):
            template_dict = {}
            args = list(args)
            for param in params:
                if param in kwargs:
                    template_dict[param] = kwargs[param]
                    continue
                for index, name in enumerate(inspect.signature(f).parameters):
                    if param == name:
                        template_dict[name] = args[index]
            print(f"::group::{Template(group_name).safe_substitute(**template_dict)}")
            resp = f(*args, **kwargs)
            print("::endgroup::")
            return resp

        return inner_wrapper

    return wrapper


default_parameters = {
    "shellcheck": "$(shfmt -f .) -e SC2148 -f json",
    "shfmt": "-d .",
    "flake8": "",
}


def main():
    linters = os.getenv('INPUT_LINTERS').split()

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

    print(comments)
    if comments:
        token = os.environ['GITHUB_TOKEN']
        gh = Github(token)
        repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
        prs = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])

        print(prs)
        if prs:
            do_comment(comments, prs[0], repo, token)

    exit(final_returncode)


@gitlab_group('Running $linter...')
def run_linter(linter):
    parameters = os.getenv(f"INPUT_{linter.upper()}_PARAMETERS", "")
    cmd = f"{linter} {parameters} {default_parameters.get(linter, '')}"
    print(cmd)
    returncode, outs = subprocess.getstatusoutput(cmd)
    comments = available_linters[linter].parse(outs)
    return returncode, comments


@gitlab_group('Commenting')
def do_comment(comments, pr, repo, token):
    commit = list(pr.get_commits())[-1]
    pr_comments = [comment.body for comment in pr.get_comments()]
    for comment in comments:
        com = Comment(repo, pr, token, commit.sha, **comment)
        if com.comments not in pr_comments:
            com.post()


if __name__ == "__main__":
    main()
