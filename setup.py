from setuptools import setup

from version import __version__

# Get the long description from the README file
with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='nb2md',
    version=__version__,
    author='Michele Dallachiesa',
    author_email='michele.dallachiesa@minodes.com',
    packages=['nb2md'],
    scripts=[],
    url='https://github.com/elehcimd/nb2md',
    license='MIT',
    description='Conversion of Jupyter and Zeppelin notebooks to Jupyter or Markdown formats',
    long_description=long_description,
    python_requires=">=3.4",
    install_requires=[
        "nbformat",
        "boto3"
    ],
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'Intended Audience :: System Administrators',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3',
    ],
    entry_points={
        'console_scripts': [
            'nb2md = nb2md.nb2md:main',
        ]
    },
)
