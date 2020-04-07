import io
from pathlib import Path
from setuptools import setup, find_packages

parent_dir = Path(__file__).parent

version = io.open(parent_dir / "up42/_version.txt", encoding="utf-8").read()


setup(
    name="up42-py",
    version=version,
    description="Python SDK for UP42",
    long_description=Path(parent_dir / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/up42/up42-py",
    license="MIT",
    packages=find_packages(exclude=("tests", "docs", "examples")),
    package_data={"": ["_version.txt", "data/aoi_berlin.geojson",
                       "data/aoi_washington.geojson"]},
    include_package_data=True,
    zip_safe=False,
    install_requires=Path(parent_dir / "requirements.txt").read_text().splitlines(),
    entry_points="""
        [console_scripts]
        up42=up42.cli:main
    """,
)
