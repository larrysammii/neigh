from setuptools import setup, find_packages

setup(
    name="neigh",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "aiohttp>=3.11.12",
        "pydantic>=2.1.0",
        "requests>=2.32.3",
        "parsel>=1.10.0",
        "aiofiles>=23.2.1",
    ],
    author="Larry Chan",
    author_email="larrylaren2@gmail.com",
    description="A Python API client for HKJC racing information",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/larrysammii/neigh",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.12",
)