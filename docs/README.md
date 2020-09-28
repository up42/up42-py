# up42-py docs

Live on github pages:
[https://up42.github.io/up42-py/](https://up42.github.io/up42-py/)

Redirected to custom domain [https://sdk.up42.com/](https://sdk.up42.com/)

## Installation for doc development:
```
cd docs
pip install -r requirements_dev.txt
```

## HTML Preview
Directly integrated in mkdocs, automatically reloads when you edit a file.
```
make serve
```
Access at `http://127.0.0.1:8000/`

## Build site (Not really neccessary due to preview function):
```
mkdocs build
```

## Update Python API reference preview via mkdocstrings
Reinstall Python package via 
```
pip install -e .
```

## Publish
```
make gh-deploy
```
Pushes to the `gh-deploy` branch and republishes as github pages.

For more infos see readme here:
https://github.com/up42/docs_mkdocs
