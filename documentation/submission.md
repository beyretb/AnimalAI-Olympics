# Submission

In order to participate in the competition you will need to upload a [docker container](https://docs.docker.com/get-started/) 
containing your trained agent that interfaces with the `animalai` library. We detail the steps for participating 
below.

## Python agent and associated data

Submissions need to implement the [agent script provided](https://github.com/beyretb/AnimalAI-Olympics/blob/master/agent.py). 
This script must implement the methods present in the base script and keep the same class name. The methods are:
- `__init__`: this will only be called once when the agent is loaded first. It can contain loading of the model and other 
related parameters.
- `reset(t)`: will be called each time the arena resets. At test time the length of episodes will vary across the 300 
experiments we will run, therefore we provide the agent with the length of the episode to come.
- `step(obs, reward, done, info)`: the method we will call each time the agent will have to take a step. The arguments 
are the ones returned by the Gym environment `AnimalAIEnv` from `animalai.envs.environment`. If you wish to directly 
work on the ML Agents `BrainInfo` you can access them via `info['brain_info']`

Make sure any data loaded in there is referred to using **absolute paths** in the container or the form `/aaio/data/...` 
(see below). An example of the code is provided [here](https://github.com/beyretb/AnimalAI-Olympics/blob/master/examples/submission/agent.py)

## Create an EvalAI account and add submission details

The competition is kindly hosted by EvalAI. Head over to [their website](https://evalai.cloudcv.org/), create an account, 
and enroll your team in the AnimalAI challenge _add link_. To be able to submit and be eligible for prizes you will also need to register your personal details using the form provided.

**Any question related solely to the submission process should be posted to the** [EvalAI forum](https://evalai-forum.cloudcv.org/c/animal-ai-olympics-2019)

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

You can now submit your container to EvalAI for evaluation as explained on the [EvalAI submission page](https://evalai.cloudcv.org/web/challenges/challenge-page/396/submission).


## Docker evaluation and results

On the EvalAI page you will see that the number of valid submissions is limited to one a day. A submission is valid if it fulfils the following requirements:

- it does not crash at any point before the first two experiments are complete (this include loading the agent, resetting it and completing the two experiments)
- loading the agent takes less than 5 minutes
- running the first two experiments takes less than 10 minutes

If your submission meets these requirements it will be flagged as valid and will void prevent you from submitting again that day. Otherwise, you will be allowed 
to submit again.

Completing the other 298 experiments cannot take longer than 70 minutes plus the remaining of the 10 minutes from the first two configurations. If your submission 
goes over the limit it will stop. You will however get partial results for the experiments that were completed.

Example scenarios:

- FAIL: agent loads in 2 minutes, crashes during test number 2
- FAIL: agent loads in 1 minute, takes more than 10 minutes to complete tests 1 and 2
- SUCCESS: your agent loads in 3 minutes, takes 30 seconds for test 1, takes 1 minute for test two, it therefore has 78.5 minutes to complete the remaining 298 experiments
- SUCCESS: agent loads in 4 minute, completes test 1 and 2 in 1 minute, uses all the 79 minutes remaining to complete only 100 tests, you will get results based on the 102 experiments ran
