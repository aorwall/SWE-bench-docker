import argparse
import logging
import os
from typing import List

from jinja2 import FileSystemLoader, Environment

from swebench_docker.constants import MAP_VERSION_TO_INSTALL, MAP_REPO_TO_DEB_PACKAGES
from swebench_docker.utils import get_eval_refs, get_requirements, get_environment_yml

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("build_docker")


def group_task_instances(task_instances):
    task_instances_grouped = {}
    for instance in task_instances:

        # Group task instances by repo, version
        repo = instance["repo"]
        version = instance["version"] if "version" in instance else None
        if repo not in task_instances_grouped:
            task_instances_grouped[repo] = {}
        if version not in task_instances_grouped[repo]:
            task_instances_grouped[repo][version] = []
        task_instances_grouped[repo][version].append(instance)

    return task_instances_grouped


def generate_testbed_base_dockerfile(
    namespace: str, repo_name: str, deb_packages: List[str], docker_dir: str
):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template("Dockerfile.testbed_base")

    base_image = f"{namespace}/swe-bench-base:latest"

    dockerfile_content = template.render(
        base_image=base_image,
        deb_packages=" ".join(deb_packages) if deb_packages else None,
        repo_name=repo_name,
    )

    repo_dir = f"{docker_dir}/{repo_name}"
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)

    output_file = f"{repo_dir}/Dockerfile"
    with open(output_file, "w") as f:
        f.write(dockerfile_content)

    print(f"Dockerfile generated: {output_file}")


def generate_testbed_dockerfile(
    namespace: str,
    repo: str,
    version: str,
    pre_install_cmds: List[str],
    install_cmds: List[str],
    environment_setup_commit: str,
    docker_dir: str,
    python_version: str,
    conda_create_cmd: str = None,
    path_to_reqs: str = None,
    path_to_env_file: str = None,
):
    env = Environment(loader=FileSystemLoader("templates"))
    repo_name = _repo_name(repo)
    image_name = repo.replace("/", "_")

    if conda_create_cmd:
        template = env.get_template("Dockerfile.conda_testbed")
        base_image = f"{namespace}/swe-bench-{image_name}:latest"
    else:
        template = env.get_template("Dockerfile.python_testbed")
        base_image = f"{namespace}/swe-bench-{image_name}-python:{python_version}"

    dockerfile_content = template.render(
        base_image=base_image,
        repo_name=repo_name,
        version=version,
        testbed=repo_name + "__" + version,
        conda_create_cmd=conda_create_cmd,
        pre_install_cmds=pre_install_cmds,
        install_cmds=install_cmds,
        path_to_reqs=path_to_reqs,
        environment_setup_commit=environment_setup_commit,
        path_to_env_file=path_to_env_file,
    )

    testbed_dir = f"{docker_dir}/{repo_name}/{version}"
    if not os.path.exists(testbed_dir):
        os.makedirs(testbed_dir)

    output_file = f"{testbed_dir}/Dockerfile"
    with open(output_file, "w") as f:
        f.write(dockerfile_content)

    print(f"Dockerfile generated: {output_file}")


def generate_instance_dockerfile(
    namespace: str,
    instance: dict,
    install_cmd: str,
    docker_dir: str,
):
    """
    Build one Docker image per benchmark instance to not have to build the environment each time before testing in
    repositories using Cython.
    """
    env = Environment(loader=FileSystemLoader("templates"))
    repo = instance["repo"]
    version = instance["version"]
    repo_name = _repo_name(repo)
    image_name = repo.replace("/", "_")

    base_image = f"{namespace}/swe-bench-{image_name}-testbed:{instance['version']}"
    template = env.get_template("Dockerfile.instance")

    dockerfile_content = template.render(
        base_image=base_image,
        repo_name=repo_name,
        install_cmd=install_cmd,
        base_commit=instance["base_commit"],
    )

    instance_dir = f"{docker_dir}/{repo_name}/{version}/{instance['instance_id']}"
    if not os.path.exists(instance_dir):
        os.makedirs(instance_dir)

    output_file = f"{instance_dir}/Dockerfile"
    with open(output_file, "w") as f:
        f.write(dockerfile_content)

    print(f"Dockerfile generated: {output_file}")


def build(swe_bench_tasks: str, namespace: str = "aorwall", docker_dir: str = "docker"):
    task_instances = list(get_eval_refs(swe_bench_tasks).values())

    # Group repos by repo, then version
    task_instances_grouped = group_task_instances(task_instances)

    testbeds = set()

    for repo, map_version_to_instances in task_instances_grouped.items():
        logger.info(f"Repo {repo}: {len(map_version_to_instances)} versions")

        # Determine instances to use for environment installation
        for version, instances in map_version_to_instances.items():
            logger.info(f"\tVersion {version}: {len(instances)} instances")
            # Use the first instance as set up for each version
            setup_ref_instance = instances[0]

            deb_packages = None
            if repo in MAP_REPO_TO_DEB_PACKAGES:
                deb_packages = MAP_REPO_TO_DEB_PACKAGES[repo]

            repo_name = _repo_name(repo)

            specifications = MAP_VERSION_TO_INSTALL[repo][version]

            if repo_name not in testbeds:
                generate_testbed_base_dockerfile(
                    namespace, repo_name, deb_packages, docker_dir
                )

                testbeds.add(repo_name)

            repo_name = _repo_name(repo)

            env_name = f"{repo_name}__{version}"

            test_bed_dir = f"{docker_dir}/{repo_name}/{version}"

            environment_setup_commit = setup_ref_instance.get(
                "environment_setup_commit", setup_ref_instance["base_commit"]
            )

            path_to_reqs = None
            path_to_env_file = None
            install_cmds = []

            testbed_dir = f"{docker_dir}/{repo_name}/{version}"
            if not os.path.exists(testbed_dir):
                os.makedirs(testbed_dir)

            pre_install_cmds = specifications.get("pre_install", None)

            # Create conda environment according to install instructinos
            pkgs = specifications["packages"] if "packages" in specifications else ""
            if pkgs == "requirements.txt":
                # Create environment
                conda_create_cmd = (
                    f"conda create -n {env_name} python={specifications['python']} -y"
                )

                path_to_reqs = get_requirements(
                    setup_ref_instance, save_path=test_bed_dir
                )
                install_cmds.append("pip install -r requirements.txt")

            elif pkgs == "environment.yml":
                if "no_use_env" in specifications and specifications["no_use_env"]:
                    # Create environment from yml
                    path_to_env_file = get_environment_yml(
                        setup_ref_instance, env_name, save_path=test_bed_dir
                    )

                    # `conda create` based installation
                    conda_create_cmd = f"conda create -c conda-forge -n {env_name} python={specifications['python']} -y"

                    # Install dependencies
                    install_cmds.append(f"conda env update -f environment.yml")
                else:
                    # Create environment from yml
                    path_to_env_file = get_environment_yml(
                        setup_ref_instance,
                        env_name,
                        save_path=test_bed_dir,
                        python_version=specifications["python"],
                    )

                    conda_create_cmd = f"conda env create -f environment.yml"
            else:
                conda_create_cmd = f"conda create -n {env_name} python={specifications['python']} {pkgs} -y"

            # Install additional packages if specified
            if "pip_packages" in specifications:
                pip_packages = " ".join(specifications["pip_packages"])
                install_cmds.append(f"pip install {pip_packages}")

            if "install" in specifications and (
                "instance_image" not in specifications
                or not specifications["instance_image"]
            ):
                install_cmds.append(specifications["install"])

            generate_testbed_dockerfile(
                namespace=namespace,
                repo=repo,
                version=version,
                python_version=specifications["python"],
                conda_create_cmd=conda_create_cmd,
                pre_install_cmds=pre_install_cmds,
                install_cmds=install_cmds,
                environment_setup_commit=environment_setup_commit,
                path_to_reqs=path_to_reqs,
                path_to_env_file=path_to_env_file,
                docker_dir=docker_dir,
            )

            if "instance_image" in specifications and specifications["instance_image"]:
                for instance in instances:
                    install_cmd = specifications["install"]
                    generate_instance_dockerfile(
                        namespace=namespace,
                        instance=instance,
                        install_cmd=install_cmd,
                        docker_dir=docker_dir,
                    )


def _repo_name(repo: str) -> str:
    return repo.replace("/", "__")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--swe_bench_tasks",
        type=str,
        help="Path to candidate task instances file",
        required=True,
    )
    parser.add_argument(
        "--namespace",
        type=str,
        help="Docker repository namespace",
        required=False,
        default="aorwall",
    )
    parser.add_argument(
        "--docker_dir", type=str, help="Path to docker directory", required=True
    )
    build(**vars(parser.parse_args()))
