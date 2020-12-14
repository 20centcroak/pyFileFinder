import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyFileFinder", 
    version="0.6",
    author="20centCroak",
    author_email="",
    description="module to easily find files in system, zip archives or ftp servers using regex",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/20centcroak/pyFileFinder",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)