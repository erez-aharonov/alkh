import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="alkh",
    version="0.0.0",
    description="algorithmic python debugging",
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
    ],
    packages=["alkh"],
    include_package_data=False,
    install_requires=["pandas>=1.3.4", "nbformat>=5.1.3"],
)