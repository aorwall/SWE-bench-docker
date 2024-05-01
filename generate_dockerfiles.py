import argparse
import logging
import os
from typing import List

from jinja2 import FileSystemLoader, Environment

from swebench.constants import MAP_VERSION_TO_INSTALL, SUPPORTED_REPOS, MAP_REPO_TO_DEB_PACKAGES
from swebench.utils import get_eval_refs, get_requirements, get_environment_yml

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


def generate_testbed_base_dockerfile(namespace: str, repo_name: str, deb_packages: List[str], docker_dir: str):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template('Dockerfile.testbed_base')

    dockerfile_content = template.render(
        namespace=namespace,
        deb_packages=" ".join(deb_packages) if deb_packages else None,
        repo_name=repo_name
    )

    repo_dir = f"{docker_dir}/{repo_name}"
    if not os.path.exists(repo_dir):
        os.makedirs(repo_dir)

    output_file = f"{repo_dir}/Dockerfile"
    with open(output_file, 'w') as f:
        f.write(dockerfile_content)

    print(f"Dockerfile generated: {output_file}")


def generate_testbed_dockerfile(
    base_image: str,
    repo_name: str,
    version: str,
    conda_create_cmd: str,
    install_cmds: List[str],
    environment_setup_commit: str,
    docker_dir: str,
    path_to_reqs: str = None,
    path_to_env_file: str = None
):
    env = Environment(loader=FileSystemLoader("templates"))
    template = env.get_template('Dockerfile.testbed')

    dockerfile_content = template.render(
        base_image=base_image,
        repo_name=repo_name,
        version=version,
        testbed=repo_name + "__" + version,
        conda_create_cmd=conda_create_cmd,
        install_cmds=install_cmds,
        path_to_reqs=path_to_reqs,
        environment_setup_commit=environment_setup_commit,
        path_to_env_file=path_to_env_file
    )

    testbed_dir = f"{docker_dir}/{repo_name}/{version}"
    if not os.path.exists(testbed_dir):
        os.makedirs(testbed_dir)

    output_file = f"{testbed_dir}/Dockerfile"
    with open(output_file, 'w') as f:
        f.write(dockerfile_content)

    print(f"Dockerfile generated: {output_file}")

def build(
    swe_bench_tasks: str,
    namespace: str = "aorwall",
    docker_dir: str = "docker"
):
    task_instances = list(get_eval_refs(swe_bench_tasks).values())
    task_instances = [instance for instance in task_instances if instance["repo"] in SUPPORTED_REPOS]

    # Group repos by repo, then version
    task_instances_grouped = group_task_instances(task_instances)

    setup_refs = {}
    for repo, map_version_to_instances in task_instances_grouped.items():
        logger.info(f"Repo {repo}: {len(map_version_to_instances)} versions")

        # Determine instances to use for environment installation
        setup_refs[repo] = {}
        for version, instances in map_version_to_instances.items():
            logger.info(f"\tVersion {version}: {len(instances)} instances")
            # Use the first instance as set up for each version
            setup_refs[repo][version] = instances[0]

    # Create docker file per repo
    for repo in setup_refs.keys():
        repo_name = _repo_name(repo)

        deb_packages = None
        if repo in MAP_REPO_TO_DEB_PACKAGES:
            deb_packages = MAP_REPO_TO_DEB_PACKAGES[repo]

        generate_testbed_base_dockerfile(namespace, repo_name, deb_packages, docker_dir)

    for repo, version_to_setup_ref in setup_refs.items():
        repo_name = _repo_name(repo)

        # Create a Dockerfile per version of the repo
        for version, install in MAP_VERSION_TO_INSTALL[repo].items():
            # Skip if none of the task instances are for this version
            if version not in version_to_setup_ref:
                continue

            env_name = f"{repo_name}__{version}"

            test_bed_dir = f"{docker_dir}/{repo_name}/{version}"

            # Get setup reference instance
            setup_ref_instance = version_to_setup_ref[version]

            environment_setup_commit = setup_ref_instance.get('environment_setup_commit', setup_ref_instance['base_commit'])

            path_to_reqs = None
            path_to_env_file = None
            install_cmds = []

            testbed_dir = f"{docker_dir}/{repo_name}/{version}"
            if not os.path.exists(testbed_dir):
                os.makedirs(testbed_dir)

            # Create conda environment according to install instructinos
            pkgs = install["packages"] if "packages" in install else ""
            if pkgs == "requirements.txt":
                # Create environment
                conda_create_cmd = f"conda create -n {env_name} python={install['python']} -y"

                path_to_reqs = get_requirements(setup_ref_instance, save_path=test_bed_dir)
                install_cmds.append("pip install -r requirements.txt")

            elif pkgs == "environment.yml":
                if "no_use_env" in install and install["no_use_env"]:
                    # Create environment from yml
                    path_to_env_file = get_environment_yml(
                        setup_ref_instance, env_name,
                        save_path=test_bed_dir
                    )

                    # `conda create` based installation
                    conda_create_cmd = f"conda create -c conda-forge -n {env_name} python={install['python']} -y"

                    # Install dependencies
                    install_cmds.append(
                        f"conda env update -f environment.yml"
                    )
                else:
                    # Create environment from yml
                    path_to_env_file = get_environment_yml(
                        setup_ref_instance, env_name,
                        save_path=test_bed_dir,
                        python_version=install["python"]
                    )

                    conda_create_cmd = f"conda env create -f environment.yml"
            else:
                conda_create_cmd = f"conda create -n {env_name} python={install['python']} {pkgs} -y"

            # Install additional packages if specified
            if "pip_packages" in install:
                pip_packages = " ".join(install["pip_packages"])
                install_cmds.append(
                    f"pip install {pip_packages}"
                )


            if "install" in install:
                install_cmds.append(install["install"])

            image_name = repo.replace("/", "_")
            base_image = f"{namespace}/swe-bench-{image_name}:latest"

            generate_testbed_dockerfile(
                base_image=base_image,
                repo_name=repo_name,
                version=version,
                conda_create_cmd=conda_create_cmd,
                install_cmds=install_cmds,
                environment_setup_commit=environment_setup_commit,
                path_to_reqs=path_to_reqs,
                path_to_env_file=path_to_env_file,
                docker_dir=docker_dir)


def _repo_name(repo: str) -> str:
    return repo.replace("/", "__")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--swe_bench_tasks", type=str, help="Path to candidate task instances file", required=True)
    parser.add_argument("--namespace", type=str, help="Docker repository namespace", required=False, default="aorwall")
    parser.add_argument("--docker_dir", type=str, help="Path to docker directory", required=True)
    build(**vars(parser.parse_args()))
