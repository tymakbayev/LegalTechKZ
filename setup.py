#!/usr/bin/env python3
"""
Setup script for Legal Expert System for Kazakhstan NPA
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="npa-legal-expert",
    version="1.0.0",
    author="Legal Expert Team",
    description="AI-powered legal examination system for Kazakhstan normative legal acts",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tymakbayev/npa-legal-expert",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Topic :: Legal :: Analysis",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: Russian",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "legal-expert=legaltechkz.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
