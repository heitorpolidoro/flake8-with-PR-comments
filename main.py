import os

from github import Github, GithubException

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
        if prs.totalCount:
            pr = prs[0]
            commit = list(pr.get_commits())[-1]
            for file, comments in comments.items():
                for comment in comments:
                    comment_body = comment.pop("comment")
                    create_review_comment_args = comment
                    try:
                        pr.create_review_comment(comment_body, commit, file, **create_review_comment_args)
                    except GithubException:
                        print(f"Error in create comment at {file}:{create_review_comment_args}")
                        raise
    exit(returncode)


if __name__ == "__main__":
    main()
