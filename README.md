This is a Dockerfile based solution of the [SWE-Bench evaluation framework](https://github.com/princeton-nlp/SWE-bench/tree/main/swebench/harness).

The solution is designed so that each "testbed" for testing a version of a repository is built in a separate Docker
image. Each test is then run in its own Docker container. This approach ensures more stable test results because the
environment is completely isolated and is reset for each test. Since the Docker container can be recreated each time,
there's no need for reinstallation, speeding up the benchmark process.

## Progress
Docker images for testbeds used in the `SWE-Bench_Lite` dataset has been built and tested. See results in the 
`evaluations` folder. 

The following test beds and benchmark instances currently fails when applying the golden patch:

| Instance ID | Repository | Testbed version |
| ----------- | ---------- | --------------- |
| [pydata__xarray-4094](https://github.com/aorwall/SWE-bench-docker/blob/main/evaluations/SWE-bench_Lite_golden/logs/pydata__xarray-4094.SWE-bench_Lite_golden.eval.log) | pydata/xarray | 0.12 |
| [pydata__xarray-4493](https://github.com/aorwall/SWE-bench-docker/blob//main/evaluations/SWE-bench_Lite_golden/logs/pydata__xarray-4493.SWE-bench_Lite_golden.eval.log) | pydata/xarray | 0.12 |

## Run evaluation
Run `run_evaluation.py` to evaluate a predictions file. A log for each test is written to log_dir in the same format
as in the SWE-bench evaluation tools, and the same tooling can then be used to generate a report. 

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
python generate_dockerfiles.py 
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

### Build single Docker image

```bash
scripts/build_docker_images.sh [Namespace] [Testbed directory]
```
