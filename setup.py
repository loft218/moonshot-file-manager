# setup.py
from setuptools import setup, find_packages

setup(
    name="moonshot-file-manage",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests",
    ],
    entry_points={
        "console_scripts": [
            "my-python-project = main:main",  # 更新为你的实际模块和函数
        ],
    },
)
