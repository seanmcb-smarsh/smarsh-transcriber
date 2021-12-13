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
          'deepscribe-inference==0.3.3',
      ])