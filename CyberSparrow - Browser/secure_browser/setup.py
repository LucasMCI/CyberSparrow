#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script de instalação do Navegador Seguro
"""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="secure-browser",
    version="1.0.0",
    author="Seu Nome",
    author_email="seu.email@exemplo.com",
    description="Um navegador web seguro para profissionais de cibersegurança",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/seu-usuario/secure-browser",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Security",
    ],
    python_requires=">=3.9",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "secure-browser=secure_browser.src.main:main",
        ],
    },
    package_data={
        "secure_browser": [
            "config/*.yaml",
            "config/*.json",
            "plugins/*.py",
        ],
    },
    include_package_data=True,
) 