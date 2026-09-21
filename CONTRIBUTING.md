# Contributing

Thanks for improving API Observer.

1. Fork the repository and create a focused branch.
2. Use Python 3.10+ and keep runtime code standard-library-only unless a dependency has a strong justification.
3. Add or update tests for behavior changes.
4. Run `python -m pip install -e . pytest` and then `python -m pytest -q`.
5. Keep network tests mocked so CI is deterministic.
6. Never commit API keys, tokens, private endpoints, `.env` files, or generated databases.
7. Update both English and Arabic README sections when user-facing behavior changes.

Please keep pull requests small, explain the motivation, and document any compatibility or security impact.
