import base64
import json
from functools import lru_cache
from json import JSONDecodeError

import requests


@lru_cache
def get_pr_files(pr):
    return pr.get_files()


@lru_cache
def get_file(pr, filename):
    for file in get_pr_files(pr):
        if file.filename == filename:
            return file


class Comment:
    def __init__(self, repo, pr, token, commit_id, filename, code=None, comments=None, as_code=False,
                 as_suggestion=False, start_line=None, end_line=None):
        self.repo = repo
        self.pr = pr
        self.token = token
        self.commit_id = commit_id
        self.filename = filename
        self.start_line = start_line
        self.end_line = end_line
        self.code = code or []
        if isinstance(comments, str):
            comments = [comments]
        self._comments = comments or []
        self.as_code = as_code
        self.as_suggestion = as_suggestion

    def post(self):
        if self.start_line is None:
            self._define_lines()
        nones = [k for k, v in self.__dict__.items() if v is None and k != "end_line"]
        assert [] == nones, ", ".join(nones) + " can't be None"
        print(f"Commenting in {self.filename}:{self.start_line}")

        data = {
            "body": self.comments,
            "path": self.filename,
            "commit_id": self.commit_id,
        }
        if self.end_line is None:
            data["line"] = self.start_line
        else:
            data["start_line"] = self.start_line
            data["line"] = self.end_line

        headers = {
            'Authorization': f'token {self.token}',
            'User-Agent': 'PyGithub/Python',
            'Content-Type': 'application/json',
            "X-GitHub-Api-Version": "2022-11-28"
        }
        resp = requests.post(f"{self.pr.url}/comments", json=data, headers=headers)

        try:
            resp.raise_for_status()
            return json.loads(resp.content)
        except JSONDecodeError:
            return resp.content
        except Exception:
            print(json.loads(resp.content))
            raise

    def _define_lines(self):
        # hunk_index = 0
        file = get_file(self.pr, self.filename)
        file_content = base64.b64decode(
            self.repo.get_contents(file.filename, ref=self.commit_id).content).decode().split("\n")
        starting_index = file_content.index(self.code[0])
        for index in range(starting_index, len(file_content)):
            if file_content[index:index + len(self.code)] == self.code:
                self.start_line = index + 1
                self.end_line = index + len(self.code)

    @property
    def comments(self):
        comments = self._comments
        if self.as_suggestion or self.as_code:
            comments = ["```" + ("suggestion" if self.as_suggestion else "")] + comments + ["```"]
        return "\n".join(comments)
