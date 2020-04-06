import io
from pathlib import Path
from setuptools import setup, find_packages


version = io.open(
    Path(__file__).resolve().parent / "up42/_version.txt", encoding="utf-8"
).read()

setup(
    name="up42-py",
    version=version,
    description="Python SDK for UP42",
    url="https://github.com/up42/up42-py",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["Click",],
    entry_points="""
        [console_scripts]
        up42=up42.cli:main
    """,
)
