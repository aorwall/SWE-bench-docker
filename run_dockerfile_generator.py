import argparse
from swebench_docker.dockerfile_generator import DockerfileGenerator


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
        "--predictions_path",
        type=str,
        help="Path to predictions file",
        required=False,
        default=None,
    )
    parser.add_argument(
        "--docker_dir", type=str, help="Path to docker directory", required=True
    )

    generator = DockerfileGenerator(**vars(parser.parse_args()))
    generator.generate()
