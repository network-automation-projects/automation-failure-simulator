"""
executor.py

Concurrent execution engine with failure isolation.
"""

import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from models import Device, TaskResult, TaskStatus
from retry_engine import execute_with_retry

logger = logging.getLogger(__name__)


def execute_tasks_concurrently(
    devices: List[Device],
    max_workers: int = 10,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_multiplier: float = 2.0,
) -> List[TaskResult]:
    """
    Execute tasks on multiple devices concurrently with failure isolation.

    Each device is processed independently - one failure does not affect
    others. Uses ThreadPoolExecutor for concurrent execution.

    Args:
        devices: List of devices to process
        max_workers: Maximum number of concurrent worker threads
        max_attempts: Maximum retry attempts per device
        initial_delay: Initial retry delay in seconds
        backoff_multiplier: Exponential backoff multiplier

    Returns:
        List of TaskResult objects, one per device
    """
    results = []

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all tasks
        future_to_device = {
            executor.submit(
                execute_with_retry,
                device,
                max_attempts,
                initial_delay,
                backoff_multiplier,
            ): device
            for device in devices
        }

        # Collect results as they complete
        for future in as_completed(future_to_device):
            device = future_to_device[future]
            try:
                result = future.result()
                results.append(result)
                logger.debug(
                    f"Completed {device.name}: {result.status.value}"
                )
            except Exception as e:
                # Handle unexpected exceptions during execution
                logger.error(
                    f"Unexpected exception processing {device.name}: {e}"
                )
                results.append(
                    TaskResult(
                        device=device,
                        status=TaskStatus.FAILED,
                        error_message=f"Execution exception: {str(e)}",
                    )
                )

    return results
