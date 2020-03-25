from setuptools import setup, find_packages

setup(
    name="up42-py",
    version="0.1",
    description="Python API & SDK for UP42",
    url="https://github.com/up42/up42-py",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["Click",],
    entry_points="""
        [console_scripts]
        up42=up42.cli:main
    """,
)
