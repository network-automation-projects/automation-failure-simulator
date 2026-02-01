#!/usr/bin/env python3
"""
simulator.py

Main entry point for the Automation Failure Simulator.

Demonstrates resilient automation design by simulating failures and
showing how retry logic, exponential backoff, and failure isolation
prevent one failure from breaking everything.
"""

import argparse
import logging
import random
import time
from typing import List

from models import Device, FailureType
from executor import execute_tasks_concurrently
from reporter import generate_report

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def generate_devices(
    count: int,
    failure_rate: float,
    timeout_seconds: int = 5,
) -> List[Device]:
    """
    Generate a list of devices with random failure profiles.

    Args:
        count: Number of devices to generate
        failure_rate: Percentage (0-100) of devices that should have failures
        timeout_seconds: Timeout value for devices

    Returns:
        List of Device objects
    """
    devices = []
    failure_count = int(count * (failure_rate / 100.0))

    failure_types = [
        FailureType.TIMEOUT,
        FailureType.FLAKY,
        FailureType.PARTIAL,
    ]

    for i in range(count):
        ip = f"192.168.1.{i + 1}"
        name = f"router{i + 1}"

        if i < failure_count:
            # Assign random failure type
            failure_type = random.choice(failure_types)
            if failure_type == FailureType.FLAKY:
                # Flaky devices have 60-90% failure rate
                failure_probability = 0.6 + random.random() * 0.3
                device = Device(
                    name=name,
                    ip=ip,
                    failure_type=failure_type,
                    failure_rate=failure_probability,
                    timeout_seconds=timeout_seconds,
                )
            else:
                device = Device(
                    name=name,
                    ip=ip,
                    failure_type=failure_type,
                    failure_rate=0.0,
                    timeout_seconds=timeout_seconds,
                )
        else:
            # No failure - healthy device
            device = Device(
                name=name,
                ip=ip,
                failure_type=FailureType.NONE,
                failure_rate=0.0,
                timeout_seconds=timeout_seconds,
            )

        devices.append(device)

    return devices


def main():
    """Main entry point for the automation failure simulator."""
    parser = argparse.ArgumentParser(
        description="Automation Failure Simulator - Demonstrates resilient "
        "automation design with failure simulation, retries, and isolation"
    )
    parser.add_argument(
        "--devices",
        type=int,
        default=10,
        help="Number of devices to simulate (default: 10)",
    )
    parser.add_argument(
        "--failure-rate",
        type=float,
        default=30.0,
        help="Percentage of devices that should fail (0-100, default: 30)",
    )
    parser.add_argument(
        "--max-retries",
        type=int,
        default=3,
        help="Maximum retry attempts per device (default: 3)",
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=5,
        help="Timeout in seconds (default: 5)",
    )
    parser.add_argument(
        "--initial-delay",
        type=float,
        default=1.0,
        help="Initial retry delay in seconds (default: 1.0)",
    )
    parser.add_argument(
        "--backoff",
        type=float,
        default=2.0,
        help="Exponential backoff multiplier (default: 2.0)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=10,
        help="Maximum concurrent worker threads (default: 10)",
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Enable verbose logging",
    )

    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    logger.info("Starting Automation Failure Simulator")
    logger.info(
        f"Configuration: {args.devices} devices, "
        f"{args.failure_rate}% failure rate, "
        f"{args.max_retries} max retries"
    )

    # Generate devices with failure profiles
    devices = generate_devices(
        count=args.devices,
        failure_rate=args.failure_rate,
        timeout_seconds=args.timeout,
    )

    # Execute tasks concurrently
    start_time = time.time()
    results = execute_tasks_concurrently(
        devices=devices,
        max_workers=args.max_workers,
        max_attempts=args.max_retries,
        initial_delay=args.initial_delay,
        backoff_multiplier=args.backoff,
    )
    total_time = time.time() - start_time

    # Generate and print report
    report = generate_report(results, total_time)
    print(report)


if __name__ == "__main__":
    main()
