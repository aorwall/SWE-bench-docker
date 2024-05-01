This is a Dockerfile based solution of the [SWE-Bench evaluation framework](https://github.com/princeton-nlp/SWE-bench/tree/main/swebench/harness).

The solution is designed so that each "testbed" for testing a version of a repository is built in a separate Docker
image. Each test is then run in its own Docker container. This approach ensures more stable test results because the
environment is completely isolated and is reset for each test. Since the Docker container can be recreated each time,
there's no need for reinstallation, speeding up the benchmark process.

## Supported repositories
_Only verified with the SWE-Bench Lite data set for now..._

- [ ] astropy/astropy
- [x] django/django
- [ ] marshmallow-code/marshmallow
- [x] matplotlib/matplotlib
- [ ] mwaskom/seaborn
- [ ] pallets/flask
- [ ] psf/requests
- [ ] pvlib/pvlib-python
- [ ] pydata/xarray
- [ ] pydicom/pydicom
- [ ] pylint-dev/astroid
- [ ] pylint-dev/pylint
- [ ] pytest-dev/pytest
- [ ] pyvista/pyvista
- [ ] scikit-learn/scikit-learn
- [ ] sphinx-doc/sphinx
- [ ] sqlfluff/sqlfluff
- [ ] swe-bench/humaneval
- [ ] sympy/sympy

## Usage



```
python run_evaluation.py \
    --predictions_path [Required]  Path to the predictions file 
    --log_dir          [Required]  Path to directory to save evaluation log files 
    --swe_bench_tasks  [Required]  Path to SWE-bench task instances file or dataset 
    --skip_existing    [Optional]  Skip evaluating task instances with logs that already exist
    --timeout          [Optional]  Timeout for installation + test script execution
```

### Generate and build the Docker images

#### Generate Dockerfiles 

```
python generate_dockerfiles.py \
    --swe_bench_tasks  [Required]  Path to SWE-bench task instances file or dataset 
    --namespace        [Required]  Namespace of the Docker repository 
    --docker_dir       [Required]  Path to the directory where the Dockerfiles will be saved
```

#### Build Docker images

```bash
sh build.sh [Dockerfiles directory] [Namespace]
```
