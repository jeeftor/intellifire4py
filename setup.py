import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="intellifire4py", # Replace with your own username
    version="0.1",
    author="Jeef",
    author_email="",
    license="MIT",
    description="An API to read the status of an intellifire wifi module",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/jeeftor/intellifire4py",
    packages=setuptools.find_packages(),
    install_requires=['pydantic','requests'],
    download_url='https://github.com/jeeftor/intellifire4py/archive/refs/tags/0.1.tar.gz',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)