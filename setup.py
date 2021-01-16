import pathlib

from setuptools import setup, find_packages

VERSION = "1.0.3"
PROJECT_DIR = pathlib.Path(__file__).parent
SRC_DIR = PROJECT_DIR / "src"

setup(
    name='pypleasant',
    version=VERSION,
    description="Python library and script to access the API of the pleasant password server.",
    long_description=(PROJECT_DIR / "README.md").read_text(),
    long_description_content_type="text/markdown",
    license="MIT",
    author='Dominik Bermühler',
    author_email='dominik.bermuehler@googlemail.com',
    url='https://github.com/dbermuehler/pypleasant',
    install_requires=['requests'],
    package_dir={'': str(SRC_DIR)},
    packages=find_packages(str(SRC_DIR)),
    entry_points={'console_scripts': ['pleasant-cli=pypleasant.cli:main']},
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "Topic :: Security",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: MIT License"
    ],
    python_requires='>=3.6'
)
