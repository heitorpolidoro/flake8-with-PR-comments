import os
from collections import defaultdict

from github import Github

from parsers.parser import LinterParser


def get_linters():
    linters = os.getenv("INPUT_LINTERS").split()

    return [LinterParser.get_linter(linter) for linter in linters]


def main():
    linters = get_linters()
    comments = defaultdict(list)
    returncode = 0
    for linter in linters:
        linter_returncode, linter_comments = linter.run()
        returncode = returncode or linter_returncode
        for file, file_comments in linter_comments.items():
            comments[file].extend(file_comments)

    if comments:
        token = os.environ["GITHUB_TOKEN"]
        gh = Github(token)
        repo = gh.get_repo(os.environ["GITHUB_REPOSITORY"])
        prs = repo.get_pulls(head=os.environ["GITHUB_ACTION_REF"])
        if prs.totalCount:
            pr = prs[0]
            commit = list(pr.get_commits())[-1]
            for file, file_comments in comments.items():
                for comment in file_comments:
                    comment_body = comment.pop("comment")
                    create_review_comment_args = comment
                    try:
                        pr.create_review_comment(
                            comment_body, commit, file, **create_review_comment_args
                        )
                    except Exception as e:
                        print(
                            f"Error in create comment at {file}:{create_review_comment_args}"
                        )
                        print(e)
                        print(create_review_comment_args)
    exit(returncode)


if __name__ == "__main__":
    # snap install shfmt
    # apt install shellcheck
    main()
