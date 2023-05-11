# Linter with PR comments
![GitHub last commit](https://img.shields.io/github/last-commit/heitorpolidoro/lint-with-pr-comments)

[![Latest](https://img.shields.io/github/release/heitorpolidoro/lint-with-pr-comments.svg?label=latest)](https://github.com/heitorpolidoro/lint-with-pr-comments/releases/latest)
![GitHub Release Date](https://img.shields.io/github/release-date/heitorpolidoro/lint-with-pr-comments)

[![CI/CD](https://github.com/heitorpolidoro/lint-with-pr-comments/actions/workflows/ci_cd.yml/badge.svg)](https://github.com/heitorpolidoro/lint-with-pr-comments/actions/workflows/ci_cd.yml)
[![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=heitorpolidoro_lint-with-pr-comments&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=heitorpolidoro_lint-with-pr-comments)

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
        uses: heitorpolidoro/lint-with-PR-comments@v1
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```
#### Optional parameters
```yaml
flake_parameters: Aditional flake parameters
```