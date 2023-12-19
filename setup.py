import re
from os import path

from setuptools import find_packages, setup

package_name = "dunce"
here = path.abspath(path.dirname(__file__))

setup(
    name=package_name,
    use_scm_version={
        "root": "./",
        "relative_to": __file__,
        "tag_regex": re.escape(package_name) + r"-v(?P<version>\d+(?:\.\d+){0,2}[^\+]+)(?:\+.*)?$",
        "git_describe_command": f'git describe --dirty --tags --long --match "{package_name}-v*"',
    },
    setup_requires=["setuptools_scm", "wheel"],
    description="Notes that have been marked down",
    url="https://github.com/mj2p/dunce.git",
    author="MJ2P",
    packages=find_packages(exclude=["tests"]),
    install_requires=["textual[syntax]==0.46.0", "thefuzz==0.20.0", "gitpython==3.1.40", "xdg-base-dirs==6.0.1"],
    extras_require={
        "dev": ["pre-commit==3.6.0"],
        "test": ["pytest", "textual-dev", "black", "flake8", "isort", "pytest-cov", "pytest-mocha", "pytest-mock"],
    },
    entry_points={"console_scripts": ["dunce = dunce.dunce:dunce"]},
    include_package_data=True,
)
