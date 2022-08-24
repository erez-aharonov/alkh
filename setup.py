import pathlib
from setuptools import setup

HERE = pathlib.Path(__file__).parent

README = (HERE / "README.md").read_text()

setup(
    name="alkh",
    version="0.1.4",
    description="algorithmic python debugging",
    python_requires='>=3.6.0',
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/erez-aharonov/alkh",
    author="Erez Aharonov",
    author_email="ahar.erez@gmail.com",
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    packages=["alkh"],
    include_package_data=False,
    install_requires=["pandas>=0.21.0", "nbformat>=5.1.3"],
)