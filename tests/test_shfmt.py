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
             'finish': 7,
             'start': 4},
            {'as_suggestion': True,
             'comment': '\tverbose=\'-printf "Copying %f\n',
             'start': 14},
            {'as_suggestion': True,
             'comment': 'if [[ $1 =~ "-v(erbose)?" ]]; then\n'
                        '\tverbose=\'-printf "Copying %f\n',
             'finish': 21,
             'start': 19},
            {'as_suggestion': True,
             'comment': 'find backups/ -iname *.tar.gz $verbose -exec scp {} '
                        '“myhost:backups” +\n',
             'finish': 28,
             'start': 27}
        ]
    }
