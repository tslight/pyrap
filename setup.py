import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyrap",
    version="0.0.1",
    author="Toby Slight",
    author_email="tobyslight@gmail.com",
    description="Rsync wrapper to backup/restore users on a host",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tslight/rwrap",
    install_requires=['treepick'],
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'rwrap = rwrap.__main__:main',
        ],
    }
)
