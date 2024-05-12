#!/usr/bin/env python3

"""Run evaluation"""
import argparse
import asyncio
import hashlib
import logging
import os

from swebench import get_eval_refs

from swebench_docker.constants import (
    KEY_INSTANCE_ID,
    KEY_MODEL,
    KEY_PREDICTION, MAP_REPO_TO_TEST_FRAMEWORK,
)
from swebench_docker.run_docker import run_docker_evaluation
from swebench_docker.utils import get_instances, get_test_directives

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("run_evaluation")


def deterministic_hash(input_string: str, length: int = None):
    input_bytes = input_string.encode('utf-8')
    sha256_hash = hashlib.sha256(input_bytes)
    hex_digest = sha256_hash.hexdigest()
    if length is None:
        return hex_digest
    return hex_digest[:length]


def validate_predictions(predictions_path, tasks_ids):
    # Check that predictions file exists
    if not any([predictions_path.endswith(x) for x in [".json", ".jsonl"]]):
        raise ValueError("Predictions path must be .json or .jsonl file")
    predictions = get_instances(predictions_path)
    not_in_tasks = []
    # Check that predictions are correctly formatted
    for pred in predictions:
        if any([x not in pred for x in [KEY_INSTANCE_ID, KEY_MODEL, KEY_PREDICTION]]):
            raise ValueError(f"Every prediction must have {KEY_INSTANCE_ID}, {KEY_MODEL}, and {KEY_PREDICTION} fields")
        if pred[KEY_INSTANCE_ID] not in tasks_ids:
            not_in_tasks.append(pred[KEY_INSTANCE_ID])
    # Check that instance IDs specified by predictions exist
    if len(not_in_tasks) > 0:
        logger.warning(
            "Predictions for the following instance_ids were not "
            + "found in the tasks file and will not be considered: "
            + ", ".join(not_in_tasks)
        )

async def main(
    predictions_path: str,
    swe_bench_tasks: str,
    namespace: str,
    log_dir: str,
    log_suffix: str = "",
    skip_existing: bool = False,
    timeout: int = 900,
    num_processes: int = -1,
):
    """
    Runs evaluation on predictions for each model/repo/version combination.

    Args:
        predictions_path (str): Path to the predictions file.
        swe_bench_tasks (str): Path to the SWE-bench tasks file OR HF dataset name.
        namespace (str): Docker repository namespace.
        log_dir (str): Path to the directory where logs will be saved.
        log_suffix (str): Suffix to append to log file names.
        skip_existing (bool): Whether to skip evaluations for predictions that already have logs.
        timeout (int): Timeout for each evaluation.
        num_processes (int): Number of processes to run in parallel (-1 = unlimited)

    Raises:
        ValueError: If log_dir is not a directory, testbed is not a directory, or swe_bench_tasks does not exist.
    """
    # Validate arguments
    if not os.path.exists(log_dir) or not os.path.isdir(log_dir):
        raise ValueError("--log_dir must exist and point at a directory")

    tasks = list(get_eval_refs(swe_bench_tasks).values())

    # Verify arguments are formatted correctly
    if not isinstance(tasks, list):
        raise ValueError(f"{swe_bench_tasks} must contain an array of tasks")
    tasks_map = {t[KEY_INSTANCE_ID]: t for t in tasks}
    predictions_path = os.path.abspath(predictions_path)
    validate_predictions(predictions_path, [t[KEY_INSTANCE_ID] for t in tasks])

    predictions = get_instances(predictions_path)

    if len(predictions) == 0:
        logger.info("No predictions to evaluate")
        return

    # Remove predictions that have already been evaluated
    if skip_existing:
        # Skip logs that already exist
        predictions_filtered = []
        for p in predictions:
            log_file_name = f"{p[KEY_INSTANCE_ID]}.{p[KEY_MODEL]}.eval.log"
            if log_suffix:
                log_file_name = f"{p[KEY_INSTANCE_ID]}.{p[KEY_MODEL]}.{log_suffix}.eval.log"
            log_file = os.path.join(log_dir, log_file_name)
            if not os.path.exists(log_file):
                predictions_filtered.append(p)
        if len(predictions_filtered) == 0:
            logger.info(f"All predictions already exist, skipping")
            return
        else:
            logger.info(
                f"# of predictions to evaluate: {len(predictions_filtered)} " +
                f"({len(predictions) - len(predictions_filtered)} already evaluated)"
            )
            predictions = predictions_filtered
    else:
        logger.info(
            f"# of predictions to evaluate: {len(predictions)}"
        )

    task_instances = []

    # Set the relevant data on task_instances
    for prediction in predictions:
        task = tasks_map[prediction[KEY_INSTANCE_ID]]

        test_type = MAP_REPO_TO_TEST_FRAMEWORK[task["repo"]]
        test_directives = get_test_directives(task)
        test_cmd = f"{test_type} {' '.join(test_directives)}"

        task_instances.append({
            "repo": task["repo"],
            "version": task["version"],
            "base_commit": task["base_commit"],
            KEY_INSTANCE_ID: prediction[KEY_INSTANCE_ID],
            KEY_MODEL: prediction[KEY_MODEL],
            KEY_PREDICTION: prediction[KEY_PREDICTION],
            "test_patch": task["test_patch"],
            "test_directives": test_directives,
            "test_cmd": test_cmd
        })

    task_instances = sorted(task_instances, key=lambda x: x[KEY_INSTANCE_ID])

    sem = asyncio.Semaphore(num_processes if num_processes > 0 else len(task_instances))
    async with asyncio.TaskGroup() as tg:
        for task_instance in task_instances:
            if task_instance[KEY_PREDICTION]:
                async def run_docker_throttled(*args, **kwargs):
                    async with sem:
                        return await run_docker_evaluation(*args, **kwargs)

                tg.create_task(run_docker_throttled(task_instance, namespace, log_dir, timeout, log_suffix))
            else:
                logger.info(f"[{task_instance[KEY_INSTANCE_ID]}] No prediction found.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions_path", type=str, help="Path to predictions file", required=True)
    parser.add_argument("--log_dir", type=str, help="Path to log directory", required=True)
    parser.add_argument("--swe_bench_tasks", type=str, help="Path to dataset file or HF datasets name", required=True)
    parser.add_argument("--namespace", type=str, help="Docker repository namespace", required=False, default="aorwall")
    parser.add_argument("--log_suffix", type=str, help="(Optional) Suffix to append to log file names", default="")
    parser.add_argument("--skip_existing", action="store_true", help="(Optional) Skip existing logs")
    parser.add_argument("--timeout", type=int, help="(Optional) Timeout in seconds (default: 900)", default=1800)
    parser.add_argument("--num_processes", type=int, help="(Optional) Number of processes to run in parallel (-1 for unlimited)", default=-1)
    args = parser.parse_args()
    asyncio.run(main(**vars(args)))
