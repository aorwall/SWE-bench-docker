#!/usr/bin/env python3

"""Run evaluation"""
import argparse
import asyncio
import logging
import os
import tempfile

from swebench.metrics.getters import get_logs_eval, get_id_from_lp, get_eval_refs
from swebench.metrics.report import get_eval_report

from swebench_docker.constants import (
    KEY_INSTANCE_ID,
    KEY_MODEL,
    KEY_PREDICTION, MAP_REPO_TO_TEST_FRAMEWORK, )
from swebench_docker.run_docker import run_docker_evaluation
from swebench_docker.utils import get_instances, get_test_directives

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("run_evaluation")


async def main(
    instance_id: str,
    swe_bench_tasks: str,
    namespace: str,
    predictions_path: str,
):
    """
    Runs evaluation on single instance's prediction

    Args:
        instance_id (str): Path to the predictions file.
        swe_bench_tasks (str): Path to the SWE-bench tasks file OR HF dataset name.
        namespace (str): Docker repository namespace.
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
        await run_docker_evaluation(instance, namespace, temp_dir, verbose=True)

        logger.info(f"Instance {instance_id} evaluation logs:")
        eval_log = os.path.join(temp_dir, f"{instance_id}.{instance[KEY_MODEL]}.eval.log")
        with open(eval_log, "r") as f:
            logger.info(f.read())

        eval_sm, has_report = get_logs_eval(eval_log)
        eval_refs = get_eval_refs(swe_bench_tasks)

        instance_id = get_id_from_lp(eval_log)
        if instance_id not in eval_refs:
            print(f"Gold results not found for {instance_id}")
            exit(1)

        gold_results = eval_refs[instance_id]

        report = get_eval_report(eval_sm, gold_results)

        if report["FAIL_TO_PASS"]["failure"] or report["PASS_TO_PASS"]["failure"]:
            logger.info("Found failing tests")
            logger.info("Prediction:")
            logger.info(instance[KEY_PREDICTION])

            if report["PASS_TO_PASS"]["failure"]:
                logger.info("Pass to pass:")
                for pass_ in report["PASS_TO_PASS"]["failure"]:
                    logger.info(f" - {pass_}")

            if report["FAIL_TO_PASS"]["failure"]:
                logger.info("Fail to pass:")
                for fail in report["FAIL_TO_PASS"]["failure"]:
                    logger.info(f" - {fail}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance_id", type=str, help="Instance ID", required=True)
    parser.add_argument("--swe_bench_tasks", type=str, help="Path to dataset file or HF datasets name", required=False, default="princeton-nlp/SWE-bench_Lite")
    parser.add_argument("--namespace", type=str, help="Docker repository namespace", required=False, default="aorwall")
    parser.add_argument("--predictions_path", type=str, help="Path to predictions file (must be .json)", required=False)
    args = parser.parse_args()
    asyncio.run(main(**vars(args)))
