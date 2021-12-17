import os

from setuptools import setup, find_packages


def find_version():
    tag = os.environ.get("TAG", "0.0.0")
    return tag


setup(
    name='transcriber_api',
    version=find_version(),
    description='Speech API',
    author='Smarsh',
    packages=find_packages(),
    zip_safe=False,
    install_requires=[
        "torch==1.9.0",
        "torchvision==0.10.0",
        "torchaudio==0.9.0",
        "deepscribe-inference==0.3.3",
        "pydantic",
    ],
    extras_require={
        "dev": [
            f"ml8s-test==2.11.0",
            "pytest-mock",
            "aiohttp-devtools",
            "pytest-aiohttp",
        ],
    },
)
