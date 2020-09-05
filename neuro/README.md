# Detect, Understand, Act: Neuro-Symbolic Hierarchical Reinforcement Learning

## Requirements

This project requires Python v3.6.x and pip3 to run.

## Installing dependencies

Dependency management is done through pip.

We recommend setting up a virtual environment and activating it before installing the dependencies with: `pip3 install -r requirements.txt`

## Available Scripts

### Configuration

Ensure that the filepath at the beginning of each script mentioned below is updated to reflect your own filepath.

From the root directory, you can run:

`python3 train.py [options]` to train a new macro action on a given curriculum.

`python3 big_test.py` to run a full testing run the whole AnimalAI 2019 testbed.

Multiple notebooks are also provided in the `/notebooks` directory which contain various testing scripts, automated curriculum generation scripts and visualization scripts.