# Begin

## Init project environment

- git init
- git config
- pipenv install
- git commit

## Develop

- code
- git commit
- tox

## Delivery

### Run tox

Run tox to format code style and check test.

```shell script
tox
```

### Git tag

Modify package version value, then commit.

Add tag

```shell script
git tag -a v0.1.0
```

### Build

Build this tag distribution package.

```shell script
python setup.py bdist_wheel
```

### Upload index server

Upload to pypi server, or pass `--repository-url https://pypi.org/simple` to specify index server.

```shell script
twine upload ./dist/*.whl
```
