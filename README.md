# nb2md: conversion of Jupyter and Zeppelin notebooks to Jupyter or Markdown formats

`nb2md` relies on [nbconvert](https://github.com/jupyter/nbconvert) and lets you convert Jupyter and Zeppelin notebooks to Jupyter or Markdown formats.

## Installation

You can install or update the package with pip:

```
pip install -U nb2md
```

## Usage

The format of input notebooks can be either Jupyter or Zeppelin.
The format of output notebooks can be either Jupyter or Markdown.
Input and output formats are guessed by the extension of the pathname base name: `.ipynb` for Jupyter, `.json` for Zeppelin and `.md` for Markdown.

To convert a Zeppelin notebook to Markdown:

```
nb2md --src notebooks/example1.json --dst example1.md
```
To convert a Zeppelin notebook to Markdown, using the notebook name to form the destination pathname:

```
nb2md --src notebooks/example1.json
```

To convert a Zeppelin notebook hosted on AWS S3:

```
nb2md --src s3://bucketname/your/path/2E6XDUATX/note.json
```

To convert a Jupyter notebook to Markdown:

```
nb2md --src notebooks/example2.ipynb --dst example2.md
```

To convert a Zeppelin notebook to the Jupyter format:

```
nb2md --src notebooks/example1.json --dst example1.ipynb
```

## Credits and license

The pynb project is released under the MIT license. Please see [LICENSE.txt](https://github.com/elehcimd/nb2md/blob/master/LICENSE.txt).

## Development

### Create Python environment

Instructions that work on MacOS Catalina:

* Install a specific version of Python: `pyenv install 3.8.3`
* Create virtualenv: `pyenv virtualenv 3.8.3 nb2md`
* Activate virtualenv: `pyenv activate nb2md`
* Update pip: `pip install --upgrade pip`
* Install packages: `pip install -r requirements.txt`
* Install package in development mode: `pip install -e .`
* Remove virtualenv: `pyenv virtualenv-delete nb2md`

Install pyenv/virtualenv:

```
brew update
brew install pyenv
brew install pyenv-virtualenv
```

Add to `~.zshrc`:

```
if command -v pyenv 1>/dev/null 2>&1; then
  eval "$(pyenv init -)"
  export PYENV_VIRTUALENV_DISABLE_PROMPT=1
fi

if which pyenv-virtualenv-init > /dev/null; then eval "$(pyenv virtualenv-init -)"; fi
```

The fabfile assumes you have `zsh` as shell and the `pynb` virtual env. 

### Building and publishing a new release

Create a file `secrets.py` in the project directory with the Pypi credentials in this format:

```
pypi_auth = {
    'user': 'youruser',
    'pass': 'yourpass'
}
```

To release a new version:

```
fab release
```

### Running the tests

* To run the py.test tests: `fab test`
* To run tests printing output and stopping at first error: `fab test-sx`
* To run the pep8 test: `fab test-pep8`
* To fix some common pep8 errors in the code: `fab fix-pep8`

## Contributing

1. Fork it
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Create a new Pull Request
