from setuptools import setup, find_packages

setup(
    name="animalai_train",
    version="2.0.0b0",
    description="Animal AI training library",
    url="https://github.com/beyretb/AnimalAI-Olympics",
    author="Benjamin Beyret",
    author_email="beyretb@gmail.com",
    classifiers=[
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    zip_safe=False,
    install_requires=["animalai==2.0.0b0", "mlagents==0.15.0"],
    python_requires=">=3.6.1",
)
