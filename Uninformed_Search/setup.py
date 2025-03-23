# filepath: c:\Users\pink\Documents\Study\Uni Study\Second Year\Semester 2\COS30019_IntroAI\cos30019\Uninformed_Search\setup.py
from setuptools import setup, find_packages

setup(
    name="dfs_routing",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "networkx>=2.5",
    ],
)