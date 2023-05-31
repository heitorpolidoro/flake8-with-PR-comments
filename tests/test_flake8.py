from models.parsers import Flake8Parser


def test_parse(sh_file):
    returncode, comments = Flake8Parser.run()
    assert returncode == 1
    assert comments == {
        "test.py": [{'comment': "\n^--  F401 'os' imported but unused",
                     'start': 2},
                    {'comment': '\n'
                                '^--  E302 expected 2 blank lines, found '
                                '1',
                     'start': 4},
                    {'comment': '\n'
                                '^--  E302 expected 2 blank lines, found '
                                '1',
                     'start': 7},
                    {'comment': '\n^--  E303 too many blank lines (3)',
                     'start': 12},
                    {'comment': '\n'
                                '^--  E305 expected 2 blank lines after '
                                'class or function definition, found 1',
                     'start': 22},
                    {'comment': '\n^--  W391 blank line at end of file',
                     'start': 24}]
    }
