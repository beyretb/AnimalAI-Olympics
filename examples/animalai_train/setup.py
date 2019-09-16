from setuptools import setup

setup(
    name='animalai_train',
    version='1.1.1',
    description='Animal AI competition training library',
    url='https://github.com/beyretb/AnimalAI-Olympics',
    author='Benjamin Beyret',
    author_email='bb1010@ic.ac.uk',

    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6'
    ],

    packages=['animalai_train.trainers', 'animalai_train.trainers.bc', 'animalai_train.trainers.ppo',
              'animalai_train.dopamine'],  # Required
    zip_safe=False,

    install_requires=[
        'animalai>=1.0.5',
        'dopamine-rl',
        'tensorflow==1.14',
        'matplotlib',
        'Pillow>=4.2.1,<=5.4.1',
        'numpy>=1.13.3,<=1.14.5',
        'protobuf>=3.6,<3.7',
        'grpcio>=1.11.0,<1.12.0',
        'pyyaml>=5.1',
        'atari-py',
        'jsonpickle>=1.2',
        'docopt',
        'pypiwin32==223;platform_system=="Windows"'],
    python_requires=">=3.5,<3.8",
)
