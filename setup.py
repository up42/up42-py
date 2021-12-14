from pathlib import Path
from setuptools import setup, find_packages

parent_dir = Path(__file__).resolve().parent

setup(
    name="up42-py",
    version=parent_dir.joinpath("up42/_version.txt").read_text(encoding="utf-8"),
    author="UP42",
    author_email="support@up42.com",
    description="Python SDK for UP42",
    long_description=parent_dir.joinpath("README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/up42/up42-py",
    license="MIT",
    packages=find_packages(exclude=("tests", "docs", "examples")),
    package_data={
        "": ["_version.txt", "data/aoi_berlin.geojson", "data/aoi_washington.geojson"]
    },
    include_package_data=True,
    zip_safe=False,
    install_requires=parent_dir.joinpath("requirements.txt").read_text().splitlines(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
    ],
    python_requires=">=3.7, <=3.10",
)
