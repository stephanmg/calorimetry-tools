""" Setup calorimetry tools """
from setuptools import setup


def load_requirements(filename):
    """Load dependencies from requirements.txt"""
    with open(filename, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.startswith("#")
        ]


setup(
    name="calorimetry_tools",
    version="0.1.0",
    install_requires=load_requirements("../requirements.txt"),
)
