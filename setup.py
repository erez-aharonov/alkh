import pathlib
from setuptools import setup
from setuptools import find_packages

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

use_min_versions = False

install_requires = [
    "numpy>=1.16.6",
    "pandas>=0.25.0",
    "nbformat>=5.1.3",
    "streamlit>=1.12.0",
    "libcst>=0.4.7",
    "networkx>=2.5.1"]

if use_min_versions:
    install_requires = [cond.replace(">=", "==") for cond in install_requires]


setup(
    name="alkh",
    version="0.4.1",
    description="algorithmic python debugging",
    python_requires='>=3.7.2',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/erez-aharonov/alkh",
    author="Erez Aharonov",
    author_email="ahar.erez@gmail.com",
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    packages=find_packages(),
    package_data={"alkh": ["assets/css/*.css", "assets/scripts/*.js"]},
    include_package_data=True,
    install_requires=install_requires,
)
