import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyrap",
    version="0.0.5",
    author="Toby Slight",
    author_email="tobyslight@gmail.com",
    description="Rsync Wrapper to Backup/Restore all Users.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tslight/pyrap",
    install_requires=['treepick', 'yorn'],
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ),
    entry_points={
        'console_scripts': [
            'pyrap = pyrap.__main__:main',
        ],
    }
)
