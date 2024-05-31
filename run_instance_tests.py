#!/usr/bin/env python3

"""Run evaluation"""
import argparse
import asyncio
import logging
import os
import re
import tempfile

from swebench.metrics.getters import get_eval_refs

from swebench_docker.constants import (
    KEY_INSTANCE_ID,
    KEY_MODEL,
    KEY_PREDICTION, MAP_REPO_TO_TEST_FRAMEWORK, )
from swebench_docker.run_docker import run_docker_evaluation
from swebench_docker.utils import get_instances

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("run_evaluation")


def parse_test_output(log_str: str, test_cmd: str, instance_id: str) -> str:
    # Start from the first instance of "Std. Output" or "Std. Error" after the test command
    test_cmd_idx = log_str.find(test_cmd)
    if test_cmd_idx == -1:
        return "Test command not found in log"
    
    stdout_idx = log_str.find("Std. Output", test_cmd_idx)
    stderr_idx = log_str.find("Std. Error", test_cmd_idx)
    if stdout_idx == -1 and stderr_idx == -1:
        return "No stdout or stderr found"
    start_idx = stdout_idx if stdout_idx != -1 else stderr_idx

    # End on the next log entry ("[instance_version] [instance_id]")
    pattern = re.compile(r"\n\[[^\]]*\] \[" + instance_id + r"\]")
    match = pattern.search(log_str, start_idx)
    end_idx = None if match is None else match.start()

    return log_str[start_idx:end_idx]


async def run_instance_tests(
    instance_id: str,
    patch: str,
    test_directives: list[str] = [],
    model: str = "diff",
    swe_bench_tasks: str = "princeton-nlp/SWE-bench_Lite",
    namespace: str = "aorwall",
    log_output: bool = False,
) -> str:
    """Run specified tests on an instance/patch and return the stdout and stderr"""
    if not patch:
        # TODO: Add support for running tests with empty patch
        raise ValueError("Must provide a valid patch to evaluate")
    
    tasks = get_eval_refs(swe_bench_tasks)
    task = tasks[instance_id]

    test_type = MAP_REPO_TO_TEST_FRAMEWORK[task["repo"]]

    # Show more detailed test output for troubleshooting
    if "--tb=no" in test_type:
        test_type = test_type.replace("--tb=no", "")

    test_cmd = f"{test_type} {' '.join(test_directives)}"

    instance = {
            KEY_INSTANCE_ID: instance_id,
            KEY_PREDICTION: patch,
            KEY_MODEL: model,
            "repo": task["repo"],
            "version": task["version"],
            "base_commit": task["base_commit"],
            "test_patch": task["test_patch"],
            "test_directives": test_directives,
            "test_cmd": test_cmd
    }

    with tempfile.TemporaryDirectory() as temp_dir:
        await run_docker_evaluation(instance, namespace, temp_dir)

        eval_log = os.path.join(temp_dir, f"{instance_id}.{instance[KEY_MODEL]}.eval.log")
        with open(eval_log, "r") as f:
            log_str = f.read()
            if log_output:
                logger.info(f"Instance {instance_id} evaluation logs:")
                logger.info(log_str)

        return parse_test_output(log_str, test_cmd, instance_id)
    

async def main(
    instance_id: str,
    predictions_path: str,
    test_directives: list[str],
    swe_bench_tasks: str,
    namespace: str,
    test_output_path: str,
):
    """
    Runs arbitrary tests on a single instance's prediction and returns the stdout and stderr

    Args:
        instance_id (str): Path to the predictions file.
        predictions_path (str): Path to the predictions file. If not specified the golden patch will be run.
        test_directives (list[str]): A list of directives to pass to the test.
        swe_bench_tasks (str): Path to the SWE-bench tasks file OR HF dataset name.
        namespace (str): Docker repository namespace.
        test_output_path (str): Optional path to write the test output.
    """
    if predictions_path:
        predictions_path = os.path.abspath(predictions_path)
        predictions = get_instances(predictions_path)
        prediction = [p for p in predictions if p[KEY_INSTANCE_ID] == instance_id][0]

        patch = prediction[KEY_PREDICTION]
        model = prediction[KEY_MODEL]
    else:
        tasks = get_eval_refs(swe_bench_tasks)
        task = tasks[instance_id]
        patch = task["patch"]
        model = "golden"

    output = await run_instance_tests(instance_id, patch, test_directives, model, swe_bench_tasks, namespace, verbose=True)
    if test_output_path:
        with open(test_output_path, "w") as f:
            f.write(output)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance_id", type=str, help="Instance ID", required=True)
    parser.add_argument("--swe_bench_tasks", type=str, help="Path to dataset file or HF datasets name", required=False, default="princeton-nlp/SWE-bench_Lite")
    parser.add_argument("--namespace", type=str, help="Docker repository namespace", required=False, default="aorwall")
    parser.add_argument("--predictions_path", type=str, help="Path to predictions file (must be .json)", required=False)
    parser.add_argument("--test_directives", type=str, help="Directives to pass to the test", required=False, nargs="*", default=[])
    args = parser.parse_args()
    output = asyncio.run(main(**vars(args)))
