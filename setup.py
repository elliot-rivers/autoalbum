import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("VERSION", "r") as fh:
    version = fh.read()

setuptools.setup(
    name="autoalbum",
    version=version,
    author="Elliot",
    description="Automated Google Photos Albums",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="...",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'google-auth-oauthlib',
        'google-auth',
        'google-api-python-client',
        'python-dateutil',
        'inquirer',
    ],
)
