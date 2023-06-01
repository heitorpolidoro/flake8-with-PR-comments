from models.parsers import ShfmtParser


def test_parse(sh_file):
    returncode, comments = ShfmtParser.run()
    assert returncode == 1
    assert comments == {
        "test.sh": [
            {'as_suggestion': True,
             'comment': 'if ! grep -q backup=true.* "~/.myconfig"; then\n'
                        "\techo 'Backup not enabled in $HOME/.myconfig, "
                        "exiting'\n"
                        '\texit 1\n',
             'line': 7,
             'start_line': 4},
            {'as_suggestion': True,
             'comment': '\tverbose=\'-printf "Copying %f\n',
             'start_line': 14},
            {'as_suggestion': True,
             'comment': 'if [[ $1 =~ "-v(erbose)?" ]]; then\n'
                        '\tverbose=\'-printf "Copying %f\n',
             'line': 21,
             'start_line': 19},
            {'as_suggestion': True,
             'comment': 'find backups/ -iname *.tar.gz $verbose -exec scp {} '
                        '“myhost:backups” +\n',
             'line': 28,
             'start_line': 27}
        ]
    }
