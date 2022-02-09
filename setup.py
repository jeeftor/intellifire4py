import setuptools  # type: ignore

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="intellifire4py", # Replace with your own username
    version="0.9.5",
    author="Jeef",
    author_email="",
    license="MIT",
    description="An API to read the status of an intellifire wifi module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeeftor/intellifire4py",
    packages=setuptools.find_packages(),
    install_requires=['aiohttp', 'pydantic', 'requests'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
