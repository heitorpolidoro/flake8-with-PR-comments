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
    def __init__(self, pr, token, commit_id, filename, code, comments=None, as_code=False, as_suggestion=False):

        self.pr = pr
        self.token = token
        self.commit_id = commit_id
        self.filename = filename
        self.start_line = None
        self.end_line = None
        self.code = code
        if isinstance(comments, str):
            comments = [comments]
        self._comments = comments or []
        self.as_code = as_code
        self.as_suggestion = as_suggestion
        self._define_lines()

    def post(self):
        nones = [k for k, v in self.__dict__.items() if v is None]
        assert [] == nones, ", ".join(nones) + " can't be None"
        data = json.dumps({
                  "body": self.comments,
                  "path": self.filename,
                  "commit_id": self.commit_id,
                  "start_line": self.start_line,
                  "line": self.end_line
              })
        headers = {
              'Authorization': f'token {self.token}',
              'User-Agent': 'PyGithub/Python',
              'Content-Type': 'application/json',
              "X-GitHub-Api-Version": "2022-11-28"
          }
        resp = requests.post(f"{self.pr.url}/comments", data=data, headers=headers)

        try:
            resp.raise_for_status()
            return json.loads(resp.content)
        except JSONDecodeError:
            return resp.content
        except:
            print(json.loads(resp.content))
            raise

    def _define_lines(self):
        hunk_index = 0
        file = get_file(self.pr, self.filename)
        for diff_index, diff_code in enumerate(file.patch.split('\n')):
            if diff_code[0] in ["+", " "]:
                hunk_index += 1
            if diff_code.strip() == f"+{self.code[0]}":
                self.start_line = hunk_index
                self.end_line = hunk_index + len(self.code)
                break


    @property
    def comments(self):
        comments = self._comments
        if self.as_suggestion or self.as_code:
            comments = ["```" + ("suggestion" if self.as_suggestion else "")] + comments + ["```"]
        return "\n".join(comments)
