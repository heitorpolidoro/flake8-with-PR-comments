import os

from github import Github

from models.parsers import LinterParser


def get_linters():
    linters = os.getenv('INPUT_LINTERS').split()

    return [LinterParser.get_linter(linter) for linter in linters]


def main():
    linters = get_linters()
    comments = {}
    returncode = 0
    for linter in linters:
        linter_returncode, linter_comments = linter.run()
        returncode = returncode or linter_returncode
        comments.update(linter_comments)

    if comments:
        token = os.environ['GITHUB_TOKEN']
        gh = Github(token)
        repo = gh.get_repo(os.environ['GITHUB_REPOSITORY'])
        prs = repo.get_pulls(head=os.environ['GITHUB_ACTION_REF'])
        if prs:
            pr = prs[0]
            commit = list(pr.get_commits())[-1]
            for file, comments in comments.items():
                for comment in comments:
                    pr.create_review_comment(
                        comment["comment"],
                        commit,
                        file,
                        comment["line"],
                        comment.get("start_line"),
                        as_suggestion=comment["as_suggestion"])


if __name__ == "__main__":
    main()
