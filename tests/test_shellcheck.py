from models.parsers import ShellCheckParser


def test_parse(sh_file):
    returncode, comments = ShellCheckParser.run()
    assert returncode == 1
    assert comments == {
        'test.sh': [
            {
                'comment': 'if ! grep -q backup=true.* "~/.myconfig"\n'
                           '             ^-----------^ Quote the grep pattern so '
                           "the shell won't interpret it.",
                'line': 4
            },
            {
                'comment': 'if ! grep -q backup=true.* "~/.myconfig"\n'
                           '                            ^---------^ Tilde does '
                           'not expand in quotes. Use $HOME.',
                'line': 4
            },
            {
                'comment': "  echo 'Backup not enabled in $HOME/.myconfig, "
                           "exiting'\n"
                           '       '
                           '^----------------------------------------------^ '
                           "Expressions don't expand in single quotes, use "
                           'double quotes for that.',
                'line': 6
            },
            {
                'comment': 'if [[ $1 =~ "-v(erbose)?" ]]; then\n'
                           '            ^-----------^ Remove quotes from '
                           'right-hand side of =~ to match as a regex rather '
                           'than literally.',
                'line': 10
            },
            {
                'comment': 'if [[ $1 =~ "-v(erbose)?" ]]\n'
                           '            ^-----------^ Remove quotes from '
                           'right-hand side of =~ to match as a regex rather '
                           'than literally.',
                'line': 15
            },
            {
                'comment': '  verbose=\'-printf "Copying %f\n'
                           '          ^-- Quotes/backslashes will be treated '
                           'literally. Use an array.',
                'line': 17
            },
            {
                'comment': 'find backups/   -iname *.tar.gz   $verbose   -exec '
                           'scp {}  “myhost:backups” +\n'
                           '                       ^------^ Quote the parameter '
                           "to -iname so the shell won't interpret it.",
                'line': 21
            },
            {
                'comment': 'find backups/   -iname *.tar.gz   $verbose   -exec '
                           'scp {}  “myhost:backups” +\n'
                           '                       ^-- Use ./*glob* or -- *glob* '
                           "so names with dashes won't become options.",
                'line': 21
            },
            {
                'comment': 'find backups/   -iname *.tar.gz   $verbose   -exec '
                           'scp {}  “myhost:backups” +\n'
                           '                                  ^------^ '
                           'Quotes/backslashes in this variable will not be '
                           'respected.',
                'line': 21
            },
            {
                'comment': 'find backups/   -iname *.tar.gz   $verbose   -exec '
                           'scp {}  “myhost:backups” +\n'
                           '                                  ^------^ Double '
                           'quote to prevent globbing and word splitting.',
                'line': 21
            },
            {
                'comment': 'find backups/   -iname *.tar.gz   $verbose   -exec '
                           'scp {}  “myhost:backups” +\n'
                           '                                                           '
                           '^-- This is a unicode quote. Delete and retype it '
                           '(or quote to make literal).',
                'line': 21
            },
            {
                'comment': 'find backups/   -iname *.tar.gz   $verbose   -exec '
                           'scp {}  “myhost:backups” +\n'
                           '                                                                          '
                           '^-- This is a unicode quote. Delete and retype it '
                           '(or quote to make literal).',
                'line': 21
            }
        ]
    }
