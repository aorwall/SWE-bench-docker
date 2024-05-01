This is a Dockerfile based solution of the [SWE-Bench evaluation framework](https://github.com/princeton-nlp/SWE-bench/tree/main/swebench/harness).

## Supported repositories

[ ] astropy/astropy
[x] django/django (SWE-Bench Lite dataset)
[ ] marshmallow-code/marshmallow
[ ] matplotlib/matplotlib
[ ] mwaskom/seaborn
[ ] pallets/flask
[ ] psf/requests
[ ] pvlib/pvlib-python
[ ] pydata/xarray
[ ] pydicom/pydicom
[ ] pylint-dev/astroid
[ ] pylint-dev/pylint
[ ] pytest-dev/pytest
[ ] pyvista/pyvista
[ ] scikit-learn/scikit-learn
[ ] sphinx-doc/sphinx
[ ] sqlfluff/sqlfluff
[ ] swe-bench/humaneval
[ ] sympy/sympy

## Usage

```
python run_evaluation.py \
    --predictions_path [Required]  Path to the predictions file \
    --log_dir          [Required]  Path to directory to save evaluation log files \
    --swe_bench_tasks  [Required]  Path to SWE-bench task instances file or dataset \
    --skip_existing    [Optional]  Skip evaluating task instances with logs that already exist \
    --timeout          [Optional]  Timeout for installation + test script execution \
```

### Generate and build the Docker images

Generate Dockerfiles: 

```bash
python generate_dockerfiles.py \
    --swe_bench_tasks  [Required]  Path to SWE-bench task instances file or dataset \
    --namespace        [Required]  Namespace of the repository to use for the images \
    --docker_dir       [Required]  Path to directory to save the Dockerfiles
```

Build Docker images:

```bash
sh build.sh [Dockerfiles directory] [Namespace]
```