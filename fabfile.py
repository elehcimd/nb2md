import importlib
import os
import sys

from fabric.api import local
from fabric.decorators import task

# make sure that we import the awsflow package from this directory
sys.path = ["."] + sys.path

import version

# Initialise project directory and name
project_dir = os.path.abspath(os.path.dirname(__file__))
project_name = os.path.basename(project_dir)

# Change directory to directory containing this script
os.chdir(project_dir)


def fatal(msg):
    print("Fatal error: {}; exiting.".format(msg))
    sys.exit(1)


def get_version():
    return sys.modules[project_name].version.__version__


@task
def inc_version():
    """
    Increment micro release version (in 'major.minor.micro') in version.py and re-import it.
    Major and minor versions must be incremented manually in  version.py.
    """

    importlib.import_module(project_name + ".version")

    current_version = get_version()

    values = list(map(lambda x: int(x), current_version.split('.')))
    values[2] += 1

    new_version = '{}.{}.{}'.format(values[0], values[1], values[2])

    with open('version.py', 'w') as f:
        f.write('__version__ = "{}"\n'.format(new_version))
    with open('{project_name}/version.py'.format(project_name=project_name), 'w') as f:
        f.write('__version__ = "{}"\n'.format(new_version))

    sys.modules[project_name].version.__version__ = new_version

    print('Increased minor version: {} => {}'.format(current_version, new_version))


@task
def git_check():
    """
    Check that all changes , besides versioning files, are committed
    :return:
    """

    # check that changes staged for commit are pushed to origin
    output = local(
        'git diff --name-only | egrep -v "^({}/version.py)|(version.py)$" | tr "\\n" " "'.format(project_name),
        capture=True).strip()
    if output:
        fatal('Stage for commit and commit all changes first: {}'.format(output))

    output = local(
        'git diff --cached --name-only | egrep -v "^({}/version.py)|(version.py)$" | tr "\\n" " "'.format(project_name),
        capture=True).strip()
    if output:
        fatal('Commit all changes first: {}'.format(output))


def git_push():
    """
    Push new version and corresponding tag to origin
    :return:
    """

    # get current version
    new_version = version.__version__
    values = list(map(lambda x: int(x), new_version.split('.')))

    # Push to origin new version and corresponding tag:
    # * commit new version
    # * create tag
    # * push version,tag to origin
    local('git add {}/version.py version.py'.format(project_name))

    local('git commit -m "updated version"')
    local('git tag {}.{}.{}'.format(values[0], values[1], values[2]))
    local('git push origin --tags')
    local('git push')


@task
def test(params=''):
    """
    Run all tests in docker container
    :param params: parameters to py.test
    """
    local('py.test {}'.format(params))


@task
def test_sx(params=''):
    """
    Execute all tests in docker container printing output and terminating tests at first failure
    :param params: parameters to py.test
    """
    local('py.test -sx {}'.format(params))


@task
def test_pep8():
    """
    Execute  only pep8 test in docker container
    """
    local('py.test tests/test_pep8.py')


@task
def fix_pep8():
    """
    Fix a few common and easy PEP8 mistakes in docker container
    """
    local('autopep8 --select E251,E303,W293,W291,W391,W292,W391,E302 --aggressive --in-place --recursive .')


@task
def build():
    """
    Build package in docker container
    :return:
    """
    local('python3 setup.py sdist bdist_wheel')


@task
def release():
    """
    Release new package version to pypi
    :return:
    """

    from secrets import pypi_auth

    # Check that all changes are committed before creating a new version
    # git_check()

    # Test package
    test()

    # Increment version
    inc_version()

    # Commit new version, create tag for version and push everything to origin
    # git_push()

    # Build and publish package
    build()
    pathname = 'dist/{}-{}.tar.gz'.format(project_name, get_version())
    local('twine upload -u {user} -p {pass} {pathname}'.format(pathname=pathname, **pypi_auth))

    # Remove temporary files
    clean()


@task
def clean():
    """
    Rempove temporary files
    """
    local('rm -rf .cache .eggs .pytest_cache build dist')
