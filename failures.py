"""
failures.py

Failure injection mechanisms for simulating different failure types.
"""

import random
import time
import logging

from models import Device, FailureType, TaskStatus, TaskResult

logger = logging.getLogger(__name__)


def simulate_task(device: Device) -> TaskResult:
    """
    Simulate executing a task on a device with failure injection.

    This function simulates various failure scenarios based on the device's
    failure_type configuration. It performs operations like gathering device
    facts, backing up config, and checking version.
    """
    operations = ["gather_facts", "backup_config", "check_version"]
    partial_results = []

    try:
        if device.failure_type == FailureType.TIMEOUT:
            # Simulate timeout by sleeping longer than timeout_seconds
            logger.debug(f"Simulating timeout for {device.name}")
            time.sleep(device.timeout_seconds + 2)
            return TaskResult(
                device=device,
                status=TaskStatus.TIMEOUT,
                attempts=1,
                error_message=f"Operation timed out after {device.timeout_seconds}s",
            )

        elif device.failure_type == FailureType.FLAKY:
            # Flaky devices have a random chance of failure
            if random.random() < device.failure_rate:
                logger.debug(f"Simulating flaky failure for {device.name}")
                return TaskResult(
                    device=device,
                    status=TaskStatus.FAILED,
                    attempts=1,
                    error_message="Connection failed - flaky device",
                )
            # Success case - simulate normal operation
            time.sleep(0.1 + random.random() * 0.5)
            return TaskResult(
                device=device,
                status=TaskStatus.SUCCESS,
                attempts=1,
                partial_results=operations,
            )

        elif device.failure_type == FailureType.PARTIAL:
            # Partial failure: some operations succeed, others fail
            logger.debug(f"Simulating partial failure for {device.name}")
            for operation in operations:
                if random.random() < 0.5:
                    partial_results.append(f"{operation}: success")
                else:
                    partial_results.append(f"{operation}: failed")
            time.sleep(0.2 + random.random() * 0.3)

            # If any operation failed, return partial status
            failed_count = sum(
                1 for r in partial_results if r.endswith(": failed")
            )
            if failed_count > 0:
                return TaskResult(
                    device=device,
                    status=TaskStatus.PARTIAL,
                    attempts=1,
                    partial_results=partial_results,
                    error_message=f"{failed_count} of {len(operations)} operations failed",
                )
            return TaskResult(
                device=device,
                status=TaskStatus.SUCCESS,
                attempts=1,
                partial_results=partial_results,
            )

        else:
            # No failure - normal successful operation
            time.sleep(0.1 + random.random() * 0.4)
            return TaskResult(
                device=device,
                status=TaskStatus.SUCCESS,
                attempts=1,
                partial_results=operations,
            )

    except Exception as e:
        logger.error(f"Unexpected error simulating task for {device.name}: {e}")
        return TaskResult(
            device=device,
            status=TaskStatus.FAILED,
            attempts=1,
            error_message=f"Unexpected error: {str(e)}",
        )
