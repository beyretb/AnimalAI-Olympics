# Submission

In order to participate in the competition you will need to upload a [docker container](https://docs.docker.com/get-started/) 
containing your trained agent that interfaces with the `animalai` library. We detail the steps for participating 
below.

## Create an EvalAI account and add submission details

The competition is kindly hosted by EvalAI. Head over to [the website](https://evalai.cloudcv.org/), create an account, 
and enroll your team in the AnimalAI challenge _add link_. To be able to submit and be eligible for prizes you will also need to register your personal details using _add link_.

**Any question related solely to the submission process should be posted to the EvalAI forum** _add link_

## Docker

Docker offers a containerized platform for running applications in a closed environment. You can install all the libraries your agent will require, which we will use directly run the tests as they would run on your local machine.

Take the time to read the [Docker documentation](https://docs.docker.com/get-started/) and follow the install process.

### Adding CUDA capabilities to Docker (optional)

As part of the evaluation we offer GPU compute on an AWS 
[p2.xlarge instance](https://aws.amazon.com/ec2/instance-types/p2/). These compute instances will run an Amazon 
[Deep Learning Base AMI](https://aws.amazon.com/marketplace/pp/B077GCZ4GR) with several CUDA libraries installed. The 
native docker engine does not provide a pass-through to these libraries, rendering any use of GPU capable libraries (such as `tensorflow-gpu`) impossible.

To overcome this issue, NVIDIA provides a specific version of docker. We can recommend 
[this tutorial](https://marmelab.com/blog/2018/03/21/using-nvidia-gpu-within-docker-container.html#installing-nvidia-docker) for installing this version. Note we cannot provide help with installing these.

## Creating the docker for submission

Once you have docker up and running, you can start building your submission. Head over to `examples/sumission` and have a look at the `Dockerfile`. This script installs all the requirements for the environment, we do not recommend editing anything outside of the commented block saying `YOUR COMMANDS GO HERE`.

If your submission only requires the `animalai-train` library to run, you can use `Dockerfile` without any modification. While in `examples/submission` run:

```
docker build --tag=submission .
```

You can give your docker the name you want, it does not have to be `submission`. Note that the Dockerfile creates two 
folders `/aaio` and `/aaio/data` at the root of the container, and copies the agent and associated data from your local 
machine onto the container. Your submission must keep this architecture and references to these folders in 
your code **should use absolute paths** (see the example agent provided in `examples/submission`).


## Test your docker

As uploading and evaluating containers takes a while, and you are only allowed a maximum of one submission per day, it is recommended to ensure your docker runs properly before submitting. If there is a failure during testing **you will only have access to abridged outputs** which may not be enough to debug on your own. If you cannot find a solution using the provided submission testing volume you will need to raise a question on the forum and we will investigate for you (which might take time).

Bottom line: be sure to test your submission prior to uploading!

First, copy the AnimalAI linux environment (and AnimalAI_Data folder) to `examples/submission/test_submission/env`. 

Next, you need to  run the container by mounting the `test_submission` folder and its content as a volume, and execute the `testDocker.py` script. To do so, from the `submission` folder, run:

```
docker run -v "$PWD"/test_submission:/aaio/test submission python /aaio/test/testDocker.py 
```

If your container and agent are set properly, you should not get any error, and the script should output the rewards for 5 simple tests and conclude with `SUCCESS`

## Submit your docker

You can now submit your container to EvalAI for evaluation as explained at _add link_
