from setuptools import setup, find_packages

setup(
    name="gizmo",
    version="0.0.10",
    packages=find_packages(),
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "gizmo = gizmo.__main__:main",
        ],
    },
)
