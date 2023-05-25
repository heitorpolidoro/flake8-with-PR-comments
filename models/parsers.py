import json
import re


class LinterParser:
    def __init__(self, filename_regex=None, error_regex=None, code_regex=r"(.*)", as_code=False, as_suggestion=False,
                 break_comment_regex=None):
        self.filename_regex = filename_regex
        self.error_regex = error_regex
        self.code_regex = code_regex
        self.as_code = as_code
        self.as_suggestion = as_suggestion
        self.break_comment_regex = break_comment_regex

    def parse(self, output):
        def _match(regex, txt):
            _m = re.match(regex, txt)
            if _m:
                try:
                    return _m.group(1) or ''
                except IndexError:
                    return _m.group(0)

        def _add_comment(_filename, _code, _errors):
            if _code and _errors:
                comments.append({
                    "filename": _filename,
                    "code": _code.copy(),
                    "comments": _errors.copy(),
                    "as_code": self.as_code,
                    "as_suggestion": self.as_suggestion
                })
                _code.clear()
                _errors.clear()

        filename = None
        code = []
        errors = []
        comments = []
        for line in output.split("\n"):
            break_comment = _match(self.break_comment_regex, line)
            if break_comment:
                _add_comment(filename, code, errors)
                continue
            match_filename = _match(self.filename_regex, line)
            if match_filename:
                if filename:
                    _add_comment(filename, code, errors)
                filename = match_filename
                continue
            match_error = _match(self.error_regex, line)
            if match_error is not None:
                errors.append(match_error)
                continue
            match_code = _match(self.code_regex, line)
            if match_code is not None:
                code.append(match_code)
                continue
            if code and errors:
                _add_comment(filename, code, errors)

        _add_comment(filename, code, errors)
        return comments


class ShellCheckParser(LinterParser):
    def parse(self, output):
        comments = {}
        for error in json.loads(output):
            filename = error["file"]
            code = [c.rstrip() for c in open(filename).readlines()[error["line"] - 1:error["endLine"]]]
            key = json.dumps({"filename": filename, "code": code})
            if key not in comments:
                comments[key] = code
            comments[key].append(
                " " * (error["column"] - 1) + f"^-- SC{error['code']} ({error['level']}) {error['message']}")

        merged_comments = []
        for k, v in comments.items():
            merged_comments.append(dict(comments=v, as_code=True, **json.loads(k)))
        return merged_comments


class LineParser(LinterParser):
    def __init__(self, *args, line_regex=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.line_regex = line_regex

    def parse(self, output):
        comments = []
        for line in output.split("\n"):
            match = re.match(self.line_regex, line)
            if match:
                dict_info = match.groupdict()
                dict_info["start_line"] = int(dict_info["start_line"])
                dict_info["end_line"] = dict_info["start_line"] + 1
                comments.append(dict_info)
        return comments


available_linters = {
    "shellcheck": ShellCheckParser(),
    "shfmt": LinterParser(
        filename_regex=r'\+\+\+ (.*)',
        error_regex=r"\+(.*)",
        code_regex=r"-([^-].*)?$",
        break_comment_regex=r"@@",
        as_suggestion=True
    ),
    "flake8": LineParser(line_regex=r"\./(?P<filename>[^:]+):(?P<start_line>\d+):\d+: (?P<comments>.*)"),
}
