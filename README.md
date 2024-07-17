## Hosted Evaluation Solution
_Since the SWE-Bench team has developed a more stable containerized evaluation harness, this project will no longer be maintained. However, to continue promoting easier evaluation runs, I've set up a hosted solution for running evaluations that I'm trying out right now._

### How to use the hosted evaluation solution
1. Go to [moatless.ai](https:/moatless.ai)
2. Upload your prediction file and login with your Github account.
3. Your file will be evaluated in under 20 minutes (if no other evaluations are already running).

**Note**: This is a test solution to help streamline the evaluation process. Please send any feedback to [albert@moatless.ai](mailto:albert@moatless.ai).



***



## SWE-bench-docker

This is a Dockerfile based solution of the [SWE-Bench evaluation framework](https://github.com/princeton-nlp/SWE-bench/tree/main/swebench/harness).

The solution is designed so that each "testbed" for testing a version of a repository is built in a separate Docker
image. Each test is then run in its own Docker container. This approach ensures more stable test results because the
environment is completely isolated and is reset for each test. Since the Docker container can be recreated each time,
there's no need for reinstallation, speeding up the benchmark process.

## Validation

### SWE-Bench_Lite
Docker images for testbeds used in the `SWE-Bench_Lite` dataset has been built and tested on _gold predictions_. 
2 benchmark instances are currently failing. 
See results in the [evaluations/SWE-bench_Lite_golden](https://github.com/aorwall/SWE-bench-docker/blob/main/evaluations/SWE-bench_Lite_golden) folder. 

### SWE-Bench
Docker images for testbeds used in the `SWE-Bench` dataset has been built and tested on the `check-harness` predictions
[published by SWE-bench](https://github.com/princeton-nlp/SWE-bench/tree/main/docs/20240415_eval_bug). 
10 benchmark instances are currently failing. 
See results in the [evaluations/SWE-bench_check_harness](https://github.com/aorwall/SWE-bench-docker/blob/main/evaluations/SWE-bench_Lite_golden_harness) folder.

### Comparing results from other agents
I have tested running Docker benchmarks on the SWE-Agents GPT-4 benchmark and Auto Code Rover's first benchmark run.

The [SWE-Agent](https://github.com/princeton-nlp/SWE-agent) GPT-4 predictions yield exactly the same
[results of 18% (54) resolved issues](https://github.com/aorwall/SWE-bench-docker/blob/main/evaluations/20240402_sweagent_gpt4) 
as SWE-Agent's own [results](https://github.com/swe-bench/experiments/blob/main/evaluation/lite/20240402_sweagent_gpt4/results/results.json), 
which seems to show that the Docker image approach works with the same accuracy. 

However, the Docker benchmark provides better results for [AutoCodeRover](https://github.com/nus-apr/auto-code-rover). 
In AutoCodeRover's own benchmarks, they achieve 16.00% (48), 15.67% (47), and 16.67% (50) resolved issues. In 
swe-bench-docker, the same predictions result in [18.00% (54)](https://github.com/aorwall/SWE-bench-docker/blob/main/evaluations/auto-code-rover-run-1), 
[19% (57)](https://github.com/aorwall/SWE-bench-docker/blob/main/evaluations/auto-code-rover-run-2) and 
[19% (57)](https://github.com/aorwall/SWE-bench-docker/blob/main/evaluations/auto-code-rover-run-3) resolved issues. 
This adds up to a pass@3 of 26% (78) compared to 22.33% (67) reported in the [AutoCodeRover paper](https://arxiv.org/pdf/2404.05427).
This suggests that other agents' benchmarks may show lower results than they actually achieve because it's challenging
to conduct evaluations with completely accurate results.

## Docker images types
There are currently three different Docker images for running benchmarks.

### Conda
Testbeds are set up in a Conda environment similar to the original SWE-bench environment.

### Pyenv
Since each benchmark is tested in its own container, using Conda may be overkill. Testbeds are set up with only the
correct Python version installed via Pyenv. This approach has been shown to result in fewer erroneous benchmark 
instances in repositories where it has been tested, and the image becomes smaller. Currently, `django`, `psf/requests` 
and `scikit-learn` use this type of Docker image. Hopefully, more repositories can be run this way.

### Instance image
In `scikit-learn`, some benchmarks seem to fail because Cython code isn't compiled. To avoid building the project before each test, an image is built for each benchmark instance.


## Run evaluation
Run `run_evaluation.py` to evaluate a predictions file. A log for each test is written to log_dir in the same format as in the SWE-bench evaluation tools, and the same tooling can then be used to generate a report. 

Each prediction will be provided to the docker image in a base64 encoded environment variable. This might fail if the predictions are too large. To avoid this the export environment variable `SWEBENCH_DOCKER_FORK_DIR` can be set to provide the prediction in a file in a mounted volume instead.

```bash
git clone https://github.com/aorwall/SWE-bench-docker.git
export SWEBENCH_DOCKER_FORK_DIR=/path/to/SWE-bench-docker
```

Run evaluation
```
python run_evaluation.py 
    --predictions_path [Required]  Path to the predictions file 
    --log_dir          [Required]  Path to directory to save evaluation log files 
    --swe_bench_tasks  [Required]  Path to SWE-bench task instances file or dataset 
    --namespace        [Optional]  Namespace of the Docker repository 
    --log_suffix       [Optional]  Suffix to append to log file names
    --skip_existing    [Optional]  Skip evaluating task instances with logs that already exist
    --timeout          [Optional]  Timeout for installation + test script execution
    --num_processes    [Optional]  Number of processes to run in parallel (-1 for unlimited)
```

### Pull Docker images
It might be worth pulling all Images before running the script to achieve more consistent timing in the evaluation. 

```bash
scripts/pull_docker_images.sh [Dockerfiles directory] [Namespace]
```

## Build Docker images

### Generate Dockerfiles
Generates Dockerfiles for all test beds in a SWE-Bench benchmark dataset. These can then be used to build Docker images.

```
python run_dockerfile_generator.py 
    --swe_bench_tasks  [Required]  Path to SWE-bench task instances file or dataset 
    --namespace        [Required]  Namespace of the Docker repository 
    --docker_dir       [Required]  Path to the directory where the Dockerfiles will be saved
```

### Build Docker images
This script builds Docker images from all Dockerfiles.

```bash
scripts/build_docker_images.sh [Dockerfiles directory] [Namespace]
```

### Push Docker images
This script builds Docker images from all Dockerfiles.

```bash
scripts/push_docker_images.sh [Dockerfiles directory] [Namespace]
```

## Troubleshooting

### Run single instance
Run a single instance and print logs to stdout. 

```
python run_single_instance.py 
    --instance_id      [Required]  Instance ID of the task to run
    --swe_bench_tasks  [Optional]  Path to SWE-bench task instances file or dataset (default is princeton-nlp/SWE-bench_Lite)
    --namespace        [Optional]  Namespace of the Docker repository
    --predictions_path [Optional]  Path to the predictions file, if not set the golden patch will be used
```

### Run arbitrary tests on instance
Run any or all tests in an instance repo and print logs to stdout.

```
python run_instance_tests.py
    --instance_id      [Required]  Instance ID of the task to run
    --swe_bench_tasks  [Optional]  Path to SWE-bench task instances file or dataset (default is princeton-nlp/SWE-bench_Lite)
    --namespace        [Optional]  Namespace of the Docker repository
    --predictions_path [Optional]  Path to the predictions file, if not set the golden patch will be used
    --test_directives  [Optional]  List of tests to run, e.g. "path/to/test.py::test1 path/to/test.py::test2". If empty, run all tests.
    --test_output_dir  [Optional]  Path to directory to save test output
```

### Build single Docker image

```bash
scripts/build_docker_images.sh [Namespace] [Testbed directory]
```
