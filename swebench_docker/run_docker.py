import asyncio
import base64
import json
import logging
import subprocess
import time

logger = logging.getLogger(__name__)


async def run_docker_evaluation(task_instance: dict, namespace: str, log_dir: str, timeout: int = 900, log_suffix: str = ""):
    repo_name = task_instance['repo'].replace("/", "_")

    # Base64 encode the instance JSON to be sure it can be passed as an environment variable
    instance_b64 = base64.b64encode(json.dumps(task_instance).encode('utf-8')).decode('utf-8')

    docker_image = f"{namespace}/swe-bench-{repo_name}-testbed:{task_instance['version']}"

    container_log_dir = '/home/swe-bench/logs'

    docker_command = [
        'docker', 'run',
        '--rm',
        '-v', f"{log_dir}:{container_log_dir}",
        '-e', f"INSTANCE={instance_b64}",
        '-e', f"LOG_DIR={container_log_dir}",
        '-e', f"TIMEOUT={timeout}",
        '-e', f"LOG_SUFFIX={log_suffix}",
        docker_image
    ]

    cmd_string = ' '.join(docker_command)
    start_time = time.time()

    process = await asyncio.create_subprocess_shell(cmd_string, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = await process.communicate()
    stdout = stdout.decode()
    if stderr:
        stderr = stderr.decode()

    elapsed_time = time.time() - start_time

    if process.returncode != 0:
        logger.warning(
            f"[{task_instance['instance_id']}][{docker_image}]  Error running container:")
        logger.warning(f"Command: {cmd_string}")
        logger.warning(f"Stdout - {stdout}")
        logger.warning(f"Stderr - {stderr}")

    elif "Evaluation succeeded" not in stdout:
        logger.warning(f"[{task_instance['instance_id']}][{docker_image}]  Container ran successfully in {elapsed_time} seconds, but evaluation failed.")
        logger.warning(f"Command: {cmd_string}")
        logger.warning(f"stdout - {stdout}")
    else:
        logger.info(f"[{task_instance['instance_id']}][{docker_image}] Container ran successfully in {elapsed_time} seconds.")
