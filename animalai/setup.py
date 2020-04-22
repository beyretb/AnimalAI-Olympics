from setuptools import setup

setup(
    name="animalai",
    version="2.0.0b0",
    description="Animal AI competition interface",
    url="https://github.com/beyretb/AnimalAI-Olympics",
    author="Benjamin Beyret",
    author_email="bb1010@ic.ac.uk",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
    ],
    packages=[
        "animalai.envs",
        "animalai.envs.gym",
        "animalai.communicator_objects",
    ],  # Required
    zip_safe=False,
    install_requires=["mlagents-envs==0.15.0", "jsonpickle", "pyyaml"],
    python_requires=">=3.5",
)
