"""
Setup script for BoR-Proof SDK v1.0.0

Note: This file is kept for backward compatibility.
The package is primarily configured via pyproject.toml.
"""

from setuptools import find_packages, setup

setup(
    name="bor-sdk",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[],
    description="BoR-Proof SDK — Deterministic, Replay-Verifiable Proof of Reasoning",
    author="Kushagra Bhatnagar",
    author_email="bhatnagar.kushagra.m@gmail.com",
    license="MIT",
    python_requires=">=3.9",
)
