"""
reporter.py

Outcome summarization and reporting for automation results.
"""

from typing import List

from models import TaskResult, TaskStatus


def generate_report(results: List[TaskResult], total_time: float) -> str:
    """
    Generate a formatted report summarizing automation execution results.

    Args:
        results: List of TaskResult objects
        total_time: Total execution time in seconds

    Returns:
        Formatted report string
    """
    total_devices = len(results)
    successful = sum(1 for r in results if r.status == TaskStatus.SUCCESS)
    failed = sum(1 for r in results if r.status == TaskStatus.FAILED)
    timed_out = sum(1 for r in results if r.status == TaskStatus.TIMEOUT)
    partial = sum(1 for r in results if r.status == TaskStatus.PARTIAL)

    success_rate = (successful / total_devices * 100) if total_devices > 0 else 0

    # Calculate average retries for successful devices
    successful_results = [r for r in results if r.status == TaskStatus.SUCCESS]
    avg_retries = (
        sum(r.attempts for r in successful_results) / len(successful_results)
        if successful_results
        else 0
    )

    # Build report
    report_lines = [
        "=== Automation Failure Simulator Results ===",
        "",
        f"Total Devices: {total_devices}",
        f"Successful: {successful} ({success_rate:.1f}%)",
        f"Failed: {failed}",
        f"Timed Out: {timed_out}",
        f"Partial: {partial}",
        f"Total Time: {total_time:.2f}s",
        "",
    ]

    if successful > 0:
        report_lines.append(f"Average Retries (successful): {avg_retries:.1f}")

    report_lines.extend(["", "Device Details:"])

    # Add per-device details
    for result in results:
        status_symbol = "✓" if result.status == TaskStatus.SUCCESS else "✗"
        device_info = f"{status_symbol} {result.device.name} ({result.device.ip})"

        if result.status == TaskStatus.SUCCESS:
            if result.attempts == 1:
                status_msg = f"Success on first try ({result.elapsed_time:.2f}s)"
            else:
                status_msg = (
                    f"Success after {result.attempts} retries "
                    f"({result.elapsed_time:.2f}s)"
                )
        elif result.status == TaskStatus.TIMEOUT:
            status_msg = (
                f"Failed: Timeout after {result.attempts} attempts "
                f"({result.elapsed_time:.2f}s)"
            )
        elif result.status == TaskStatus.PARTIAL:
            status_msg = (
                f"Partial failure: {result.error_message} "
                f"({result.elapsed_time:.2f}s)"
            )
        else:
            error_msg = result.error_message or "Unknown error"
            status_msg = (
                f"Failed: {error_msg} after {result.attempts} attempts "
                f"({result.elapsed_time:.2f}s)"
            )

        report_lines.append(f"  {device_info} - {status_msg}")

    return "\n".join(report_lines)
