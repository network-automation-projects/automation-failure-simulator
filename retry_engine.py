"""
retry_engine.py

Retry logic with exponential backoff for handling failures.
"""

import time
import logging

from models import Device, TaskResult, TaskStatus
from failures import simulate_task

logger = logging.getLogger(__name__)


def execute_with_retry(
    device: Device,
    max_attempts: int = 3,
    initial_delay: float = 1.0,
    backoff_multiplier: float = 2.0,
) -> TaskResult:
    """
    Execute a task on a device with retry logic and exponential backoff.

    Args:
        device: The device to execute the task on
        max_attempts: Maximum number of retry attempts
        initial_delay: Initial delay before first retry in seconds
        backoff_multiplier: Multiplier for exponential backoff

    Returns:
        TaskResult with the final status after all attempts
    """
    start_time = time.time()

    for attempt in range(1, max_attempts + 1):
        logger.debug(
            f"Attempt {attempt}/{max_attempts} for device {device.name}"
        )

        result = simulate_task(device)

        # Success cases - return immediately
        if result.status == TaskStatus.SUCCESS:
            result.attempts = attempt
            result.elapsed_time = time.time() - start_time
            logger.info(
                f"Success on attempt {attempt} for {device.name} "
                f"after {result.elapsed_time:.2f}s"
            )
            return result

        # For partial failures, we might want to retry or accept
        # For this simulator, we'll retry partial failures
        if result.status == TaskStatus.PARTIAL and attempt < max_attempts:
            logger.debug(
                f"Partial failure on attempt {attempt} for {device.name}, retrying..."
            )
        # Timeout failures can be retried
        elif result.status == TaskStatus.TIMEOUT and attempt < max_attempts:
            logger.debug(
                f"Timeout on attempt {attempt} for {device.name}, retrying..."
            )
        # Regular failures can be retried if we have attempts left
        elif result.status == TaskStatus.FAILED and attempt < max_attempts:
            logger.debug(
                f"Failure on attempt {attempt} for {device.name}, retrying..."
            )
        else:
            # Final attempt failed or no more attempts
            result.attempts = attempt
            result.elapsed_time = time.time() - start_time
            logger.warning(
                f"Failed after {attempt} attempts for {device.name} "
                f"after {result.elapsed_time:.2f}s"
            )
            return result

        # Calculate exponential backoff delay
        if attempt < max_attempts:
            delay = initial_delay * (backoff_multiplier ** (attempt - 1))
            logger.debug(
                f"Waiting {delay:.2f}s before retry {attempt + 1} "
                f"for {device.name}"
            )
            time.sleep(delay)

    # Should not reach here, but handle edge case
    result.attempts = max_attempts
    result.elapsed_time = time.time() - start_time
    return result
