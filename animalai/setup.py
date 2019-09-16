from setuptools import setup

setup(
    name='animalai',
    version='1.1.1',
    description='Animal AI competition interface',
    url='https://github.com/beyretb/AnimalAI-Olympics',
    author='Benjamin Beyret',
    author_email='bb1010@ic.ac.uk',

    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6'
    ],

    packages=['animalai.envs', 'animalai.envs.gym', 'animalai.communicator_objects'],  # Required
    zip_safe=False,

    install_requires=[
        'Pillow>=4.2.1,<=5.4.1',
        'numpy>=1.13.3,<=1.14.5',
        'protobuf>=3.6,<3.7',
        'grpcio>=1.11.0,<1.12.0',
        'pyyaml>=5.1',
        'jsonpickle>=1.2',
        'gym'],
    python_requires=">=3.5,<3.8",
)
