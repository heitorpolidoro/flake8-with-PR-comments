import os

import pytest


@pytest.fixture(autouse=True)
def sh_file():
    try:
        with open("test.sh", "w") as f:
            f.write(
                """#!/bin/bash
## Example: ShellCheck can detect many different kinds of quoting issues

if ! grep -q backup=true.* "~/.myconfig"
then
  echo 'Backup not enabled in $HOME/.myconfig, exiting'
  exit 1
fi

if [[ $1 =~ "-v(erbose)?" ]]; then
    verbose='-printf "Copying %f
"'
fi

if [[ $1 =~ "-v(erbose)?" ]]
then
  verbose='-printf "Copying %f\n"'
fi

find backups/ \
  -iname *.tar.gz \
  $verbose \
  -exec scp {}  “myhost:backups” +

"""
            )
        yield
    finally:
        os.remove("test.sh")


@pytest.fixture(autouse=True)
def py_file():
    try:
        with open("test.py", "w") as f:
            f.write(
                """#!/bin/python
import os

def greeting(name):
    print(f'Hello, {name}!')

def calculate_sum(a, b):
    return a + b



def main():
    name = input('Enter your name: ')
    greeting(name)

    a = 10
    b = 5

    result = calculate_sum(a, b)
    print(f'The sum of {a} and {b} is: {result}')

if __name__ == '__main__':
    main()

"""
            )
        yield
    finally:
        os.remove("test.py")
