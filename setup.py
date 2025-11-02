"""Setup configuration for Octa Music."""

from setuptools import setup, find_packages
import os

# Read version from version.py
version = {}
with open(os.path.join("src", "version.py")) as f:
    exec(f.read(), version)

# Read long description from README
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="octa-music",
    version=version["__version__"],
    author=version["__author__"],
    author_email="",
    description="A simple web application to search for artists on Spotify and view their information",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/octa-music",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/octa-music/issues",
        "Production Site": "https://octa-music.onrender.com/",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: Other/Proprietary License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Framework :: Flask",
        "Topic :: Multimedia :: Sound/Audio",
    ],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "octa-music=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["static/**/*", "templates/**/*"],
    },
    zip_safe=False,
    license=version["__license__"],
)
