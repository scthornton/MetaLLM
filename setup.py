"""
MetaLLM Framework Setup
"""

from setuptools import setup, find_packages
import os

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="metaLLM",
    version="1.0.0-alpha",
    author="Scott Thornton",
    author_email="scott@perfecxion.ai",
    description="The First Comprehensive AI Security Testing Framework",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/perfecXion-ai/MetaLLM",
    project_urls={
        "Bug Tracker": "https://github.com/perfecXion-ai/MetaLLM/issues",
        "Documentation": "https://github.com/perfecXion-ai/MetaLLM/docs",
        "Source Code": "https://github.com/perfecXion-ai/MetaLLM",
    },
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Developers",
        "Topic :: Security",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.10",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "metaLLM=metaLLM.__main__:main",
        ],
    },
    include_package_data=True,
    package_data={
        "metaLLM": [
            "data/**/*",
            "modules/**/*.py",
        ],
    },
    keywords=[
        "ai security",
        "llm security",
        "penetration testing",
        "ai red team",
        "prompt injection",
        "adversarial ml",
        "rag security",
        "mlops security",
    ],
    license="Apache 2.0",
    zip_safe=False,
)
