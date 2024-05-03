#!/usr/bin/env python3

"""Run evaluation"""
import argparse
import logging
import os
import tempfile

from swebench.constants import (
    KEY_INSTANCE_ID,
    KEY_MODEL,
    KEY_PREDICTION, MAP_REPO_TO_TEST_FRAMEWORK, )
from swebench.run_docker import run_docker_evaluation
from swebench.utils import get_instances, get_eval_refs, get_test_directives

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("run_evaluation")


def main(
    instance_id: str,
    swe_bench_tasks: str,
    predictions_path: str,
):
    """
    Runs evaluation on single instance's prediction

    Args:
        instance_id (str): Path to the predictions file.
        swe_bench_tasks (str): Path to the SWE-bench tasks file OR HF dataset name.
        predictions_path (str): Path to the predictions file. If not specified the golden patch will be run.
    """

    tasks = get_eval_refs(swe_bench_tasks)
    task = tasks[instance_id]

    test_type = MAP_REPO_TO_TEST_FRAMEWORK[task["repo"]]

    # Show more detailed test output for troubleshooting
    if "--tb=no" in test_type:
        test_type = test_type.replace("--tb=no", "")

    test_directives = get_test_directives(task)
    test_cmd = f"{test_type} {' '.join(test_directives)}"

    instance = {
            KEY_INSTANCE_ID: instance_id,
            "repo": task["repo"],
            "version": task["version"],
            "base_commit": task["base_commit"],
            "test_patch": task["test_patch"],
            "test_directives": test_directives,
            "test_cmd": test_cmd
    }

    task = tasks[instance_id]

    if predictions_path:
        predictions_path = os.path.abspath(predictions_path)
        predictions = get_instances(predictions_path)
        prediction = [p for p in predictions if p[KEY_INSTANCE_ID] == instance_id][0]

        instance[KEY_PREDICTION] = prediction[KEY_PREDICTION]
        instance[KEY_MODEL] = prediction[KEY_MODEL]
    else:
        instance[KEY_PREDICTION] = task["patch"]
        instance[KEY_MODEL] = "golden"

    with tempfile.TemporaryDirectory() as temp_dir:
        run_docker_evaluation(instance, temp_dir)

        logger.info(f"Instance {instance_id} evaluation logs:")
        with open(os.path.join(temp_dir, f"{instance_id}.{instance[KEY_MODEL]}.eval.log"), "r") as f:
            logger.info(f.read())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance_id", type=str, help="Instance ID", required=True)
    parser.add_argument("--swe_bench_tasks", type=str, help="Path to dataset file or HF datasets name", required=False, default="princeton-nlp/SWE-bench_Lite")
    parser.add_argument("--predictions_path", type=str, help="Path to predictions file (must be .json)", required=False)
    args = parser.parse_args()
    main(**vars(args))
