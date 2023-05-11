#!/bin/python
import json
import os
import re
import subprocess
from collections import defaultdict
from json import JSONDecodeError

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
    except:
        print(json.loads(resp.content))
        raise


def _get(url, headers):
    return _request('get', url, headers)


def _post(url, data, headers):
    return _request('post', url, headers, data)




def parse_shfmt(outs):
    filename = None
    errors = None
    code = None
    comments_by_file = defaultdict(list)

    for line in outs.split("\n"):
        if line.startswith("+++"):
            filename = line[4:]
    return []


default_parameters = {
    "shellcheck": "$(shfmt -f .) -e SC2148 -f json",
    "shfmt": "-d ."
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
        print(f"::group::Running {linter}")
        parameters = os.environ.get(f"INPUT_{linter.upper()}_PARAMETERS", "")
        cmd = f"{linter} {parameters} {default_parameters.get(linter, '')}"
        print(cmd)
        returncode, outs = subprocess.getstatusoutput(cmd)
        final_returncode = final_returncode or returncode
        comments.extend(available_linters[linter].parse(outs))
        print('::endgroup::')

    if comments:
        token = os.environ['GITHUB_TOKEN']
        gh = Github(token)
        repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
        prs = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])

        if prs:
            pr = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])[0]
            commit = list(pr.get_commits())[-1]
            pr_comments = [comment.body for comment in pr.get_comments()]
            print("::group::Commenting")
            for comment in comments:
                # Comment(pr, token, commit.sha, **comment)
                com = Comment(repo, pr, token, commit.sha, **comment)
                if com.comments not in pr_comments:
                    com.post()
            print('::endgroup::')

    exit(final_returncode)


main()
