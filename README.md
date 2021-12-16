# Linter with PR comments Action
[![Create GitHub Release](https://github.com/heitorpolidoro/flake8-with-PR-comments/actions/workflows/auto-release.yml/badge.svg)](https://github.com/heitorpolidoro/flake8-with-PR-comments/actions/workflows/auto-release.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/heitorpolidoro/flake8-with-pr-comments)

[![Latest](https://img.shields.io/github/release/heitorpolidoro/flake8-with-pr-comments.svg?label=latest)](https://github.com/heitorpolidoro/flake8-with-pr-comments/releases/latest)
![GitHub Release Date](https://img.shields.io/github/release-date/heitorpolidoro/flake8-with-pr-comments)

![GitHub](https://img.shields.io/github/license/heitorpolidoro/flake8-with-pr-comments)

Run flake8 on repository and comment in PR

### Usage
```yaml
name: Linters
on:
  pull_request:
    types: [opened, synchronize, reopened]

jobs:
  linters:
    name: Linters
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Run Linters
        uses: heitorpolidoro/lint-with-PR-comments@master
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
#### Optional parameters
```yaml
flake_parameters: Aditional flake parameters
```