# Linter with PR comments
![GitHub last commit](https://img.shields.io/github/last-commit/heitorpolidoro/lint-with-pr-comments)
[![Create GitHub Release](https://github.com/heitorpolidoro/lint-with-PR-comments/actions/workflows/auto-release.yml/badge.svg)](https://github.com/heitorpolidoro/lint-with-PR-comments/actions/workflows/auto-release.yml)

[![Latest](https://img.shields.io/github/release/heitorpolidoro/lint-with-pr-comments.svg?label=latest)](https://github.com/heitorpolidoro/lint-with-pr-comments/releases/latest)
![GitHub Release Date](https://img.shields.io/github/release-date/heitorpolidoro/lint-with-pr-comments)

![GitHub](https://img.shields.io/github/license/heitorpolidoro/lint-with-pr-comments)

Run linters on repository and comment in PR

### Usage
```yaml
name: Lint with comments

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