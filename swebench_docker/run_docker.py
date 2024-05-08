import base64
import json
import logging
import subprocess
import time

from swebench_docker.constants import MAP_VERSION_TO_INSTALL

logger = logging.getLogger(__name__)


def run_docker_evaluation(task_instance: dict, log_dir: str, timeout: int = 900, log_suffix: str = ""):
    repo_name = task_instance['repo'].replace("/", "_")

    # Base64 encode the instance JSON to be sure it can be passed as an environment variable
    instance_b64 = base64.b64encode(json.dumps(task_instance).encode('utf-8')).decode('utf-8')

    specifications = MAP_VERSION_TO_INSTALL[task_instance["repo"]][task_instance["version"]]
    if specifications.get("instance_image", False):
        docker_image = f"aorwall/swe-bench-{repo_name}-instance:{task_instance['instance_id']}"
    else:
        docker_image = f"aorwall/swe-bench-{repo_name}-testbed:{task_instance['version']}"

    container_log_dir = '/home/swe-bench/logs'

    docker_command = [
        'docker', 'run',
        '-v', f"{log_dir}:{container_log_dir}",
        '-e', f"INSTANCE={instance_b64}",
        '-e', f"LOG_DIR={container_log_dir}",
        '-e', f"TIMEOUT={timeout}",
        '-e', f"LOG_SUFFIX={log_suffix}",
        docker_image
    ]

    cmd_string = ' '.join(docker_command)
    start_time = time.time()
    result = subprocess.run(docker_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    elapsed_time = time.time() - start_time

    if result.returncode != 0:
        logger.warning(
            f"[{task_instance['instance_id']}][{docker_image}]  Error running container:")
        logger.warning(f"Command: {cmd_string}")
        logger.warning(f"Stdout - {result.stdout}")
        logger.warning(f"Stderr - {result.stderr}")

    elif "Evaluation succeeded" not in result.stdout:
        logger.warning(f"[{task_instance['instance_id']}][{docker_image}]  Container ran successfully in {elapsed_time} seconds, but evaluation failed.")
        logger.warning(f"Command: {cmd_string}")
        logger.warning(f"stdout - {result.stdout}")
    else:
        logger.info(f"[{task_instance['instance_id']}][{docker_image}] Container ran successfully in {elapsed_time} seconds.")
