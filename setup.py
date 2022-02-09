import os

from setuptools import setup, find_packages


def find_version():
    tag = os.environ.get("TAG", "0.0.0")
    return tag

# copied from the deepscriber_loader repo
deepscriber_loader_deps=[
  'audioread==2.1.8',
  'numpy==1.16.5',
  'scipy==1.4.1',
  'scikit-learn==0.22.2.post1',
  'joblib==0.14.1',
  'decorator==4.4.0',
  'six==1.16.0',
  'resampy==0.2.2',
  'SoundFile==0.10.3.post1',
  'llvmlite==0.31.0',
  'omegaconf==2.1.1',
  'docopt==0.6.2',
  'wcwidth==0.1.7',
  'threadpoolctl==2.2.0',
  'cffi==1.12.3',
  'antlr4-python3-runtime==4.8',
  'dataclasses==0.8',
  'PyYAML==5.4.1',
  'pycparser==2.19',
  'sentencepiece==0.1.96',
  'data-utils==0.2.0',
  'sox==1.3.7',
  'pyzmq==19.0.0',
  'librosa==0.7.2',
  'numba==0.48.0',
  'hydra-core==1.1.1',
]

# copied from the deepscriber_inference repo
deepscriber_inference_deps = [
  'tqdm==4.32.1',
  'tornado==6.0.4',
]

deepscribe_deps = deepscriber_loader_deps + deepscriber_inference_deps

setup(
    name='transcriber_api',
    version=find_version(),
    description='Speech API',
    author='Smarsh',
    packages=find_packages(),
    zip_safe=False,
    install_requires =

        # Install all the thirdparty deepscribe deps first which are pinned at specific versions
        # so that thirdparty libs wont simply pull in the latest versions, which would cause
        # version conflicts on startup.
        deepscribe_deps + [
            "deepscribe-inference==0.3.3",
            "deepscribe-loader==0.2.1",
            "torch==1.9.0",
            "torchvision==0.10.0",
            "torchaudio==0.9.0",
            "pydantic",
        ]
    ,
    extras_require={
        "dev": [
            f"ml8s-test==2.11.0",
            "pytest-mock",
            "aiohttp-devtools",
            "pytest-aiohttp",
        ],
    },
)
