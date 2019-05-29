from setuptools import setup

setup(
    name='animalai_train',
    version='0.4.0',
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

    packages=['animalai_train.trainers', 'animalai_train.trainers.bc', 'animalai_train.trainers.ppo'],  # Required
    zip_safe=False,

    install_requires=[
        'animalai>=0.4.0',
        'tensorflow>=1.7,<1.8',
        'matplotlib',
        'Pillow>=4.2.1,<=5.4.1',
        'numpy>=1.13.3,<=1.14.5',
        'protobuf>=3.6,<3.7',
        'grpcio>=1.11.0,<1.12.0',
        'pyyaml>=5.1',
        'jsonpickle>=1.2',
        'pypiwin32==223;platform_system=="Windows"'],
    python_requires=">=3.5,<3.8",
)