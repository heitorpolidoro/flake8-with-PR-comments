# Flake8 with PR comments Action
[![Create GitHub Release](https://github.com/heitorpolidoro/flake8-with-PR-comments/actions/workflows/auto-release.yml/badge.svg)](https://github.com/heitorpolidoro/flake8-with-PR-comments/actions/workflows/auto-release.yml)
![GitHub last commit](https://img.shields.io/github/last-commit/heitorpolidoro/flake8-with-pr-comments)

[![Latest](https://img.shields.io/github/release/heitorpolidoro/flake8-with-pr-comments.svg?label=latest)](https://github.com/heitorpolidoro/flake8-with-pr-comments/releases/latest)
![GitHub Release Date](https://img.shields.io/github/release-date/heitorpolidoro/flake8-with-pr-comments)

![GitHub](https://img.shields.io/github/license/heitorpolidoro/flake8-with-pr-comments)

Run flake8 on repository and comment in PR

### Usage
```yaml
    steps:
      - name: Checkout
        uses: actions/checkout@v2

      - name: Create GitHub Release
        uses: heitorpolidoro/auto-release@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
Must have a file named `VERSION` in root with the project version in `MAJOR.MINOR.BUGFIX` format.
#### Optional parameters
```yaml
flake_parameters: Aditional flake parameters
```