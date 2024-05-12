import argparse
import json

from swebench import (
    get_eval_refs,
    get_model_eval_summary,
    get_model_report,
    get_instances,
)


def _generate_table(
    title: str, model_name_or_path: str, instances_ids: list[str], instances: dict
):
    table_md = f"""\n\n### {title}

| Instance ID | Repository | Testbed version |
| ----------- | ---------- | --------------- |
"""
    instances_ids.sort()
    for instance_id in instances_ids:
        table_md += f"| [{instance_id}](logs/{instance_id}.{model_name_or_path}.eval.log) "
        table_md += f"| {instances[instance_id]['repo']} "
        table_md += f"| {instances[instance_id]['version']} |\n"

    return table_md

def generate_report(
    swe_bench_tasks: str, predictions_path: str, log_dir: str, output_dir: str
):
    instances = get_eval_refs(swe_bench_tasks)

    predictions = get_instances(predictions_path)
    model_name_or_path = predictions[0]["model_name_or_path"]

    summary = get_model_eval_summary(
        predicts_path=predictions_path,
        eval_dir=log_dir,
        swe_bench_tasks=swe_bench_tasks,
    )

    with open(f"{output_dir}/summary.json", "w") as f:
        f.write(json.dumps(summary, indent=4))

    report_md = f"# Benchmark results"

    case_resolution = ""

    keys = ["Patch Apply Success", "Patch Apply Success + Failure"]

    for key in keys:
        if key not in summary:
            continue

        report_by_patch_status = summary[key]
        case_resolution += f"""\n\n## {key}

| Resolved | Count | Rate |
| -------- | ----- | ---- |
| Yes | {report_by_patch_status['case_resolution_counts'].get('RESOLVED_FULL', 0)} | {report_by_patch_status['case_resolution_rates'].get('RESOLVED_FULL', 0)}% |
| Partially | {report_by_patch_status['case_resolution_counts'].get('RESOLVED_PARTIAL', 0)} | {report_by_patch_status['case_resolution_rates'].get('RESOLVED_PARTIAL', 0)}% |
| No | {report_by_patch_status['case_resolution_counts'].get('RESOLVED_NO', 0)} | {report_by_patch_status['case_resolution_rates'].get('RESOLVED_NO', 0)}% |  
"""""

    print(case_resolution)
    report_md += case_resolution

    report = get_model_report(
        verbose=True,
        model=model_name_or_path,
        predictions_path=predictions_path,
        log_dir=log_dir,
        swe_bench_tasks=swe_bench_tasks,
    )

    with open(f"{output_dir}/report.json", "w") as f:
        f.write(json.dumps(report, indent=4))

    report_md += f"\n\n## Benchmark instances"

    generated = report["generated"]
    resolved = report["resolved"]
    applied = report["applied"]

    generated_not_applied = [item for item in generated if item not in applied]
    applied_not_resolved = [item for item in applied if item not in resolved]

    if generated_not_applied:
        report_md += _generate_table(
            "Generated but not applied",
            model_name_or_path,
            generated_not_applied,
            instances,
        )

    if applied_not_resolved:
        report_md += _generate_table(
            "Applied but not resolved",
            model_name_or_path,
            applied_not_resolved,
            instances,
        )

    if resolved:
        report_md += _generate_table(
            "Resolved", model_name_or_path, resolved, instances
        )

    with open(f"{output_dir}/README.md", "w") as f:
        f.write(report_md)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--predictions_path", type=str, help="Path to predictions file", required=True
    )
    parser.add_argument(
        "--log_dir", type=str, help="Path to log directory", required=True
    )
    parser.add_argument(
        "--swe_bench_tasks",
        type=str,
        help="Path to dataset file or HF datasets name",
        required=True,
    )
    parser.add_argument(
        "--output_dir", type=str, help="Path to output directory", required=True
    )
    args = parser.parse_args()
    generate_report(**vars(args))
