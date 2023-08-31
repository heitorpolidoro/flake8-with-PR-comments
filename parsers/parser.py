import os
import subprocess

from github_actions_utils.log_utils import github_group


class LinterParser:
    cmd = ""
    default_parameters = ""
    install_cmd = ""

    @staticmethod
    def get_linter(linter):
        for l_ in LinterParser.__subclasses__():
            if l_.cmd == linter:
                return l_
        raise ValueError(f"Unknown linter: {linter}")

    @classmethod
    @github_group("Running $(cls.cmd)...")
    def run(cls):
        if cls.install_cmd:
            returncode, outs = subprocess.getstatusoutput(cls.install_cmd)
            if returncode != 0:
                raise ValueError(f"Installation failed: {outs}")
        parameters = os.getenv(f"INPUT_{cls.cmd.upper()}_PARAMETERS", "")
        cmd = f"{cls.cmd} {parameters} {cls.default_parameters}"
        print(cmd)
        returncode, outs = cls._inner_run(cmd)
        comments = cls.parse(outs)
        return returncode, comments

    @classmethod
    def _inner_run(cls, cmd):  # pragma: no cover
        return subprocess.getstatusoutput(cmd)

    @classmethod
    def parse(cls, input_str) -> dict:  # pragma: no cover
        raise NotImplementedError
