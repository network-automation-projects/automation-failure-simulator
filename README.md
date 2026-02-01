# Automation Failure Simulator

A Python tool that demonstrates resilient automation design by simulating real-world failure scenarios (timeouts, flaky devices, partial failures) and showing how to handle them gracefully with retry logic, exponential backoff, and failure isolation.

**All execution is in-memory—no real network connections are made, and all devices and IPs are synthetic.**

## Features

- **Failure Simulation**: Simulates timeout, flaky, and partial failure scenarios
- **Retry Logic**: Implements exponential backoff retry strategy
- **Failure Isolation**: One device failure doesn't stop processing of others
- **Concurrent Execution**: Processes multiple devices in parallel
- **Detailed Reporting**: Summarizes outcomes, retry attempts, and statistics

## Why This Matters in Real Automation

In real network and infrastructure automation, failures are not exceptional — they are expected. This simulator demonstrates how to design automation that continues operating under partial failure, retries safely, and reports outcomes clearly instead of failing fast or masking errors.

## Design Tradeoffs

- Uses threads instead of async for simplicity and clarity
- In-memory simulation avoids external dependencies
- Retry logic is centralized rather than per-device to keep behavior consistent
- Failure types are randomized rather than scripted to simulate unpredictability

## Installation

No external dependencies required - uses only Python standard library (3.9+).

```bash
# Clone or navigate to the directory
cd automation-failure-simulator

# Make simulator executable (optional)
chmod +x simulator.py
```

## Usage

### Basic Usage

Run with default settings (10 devices, 30% failure rate, 3 max retries):

```bash
python simulator.py
```

### Custom Configuration

```bash
python simulator.py \
  --devices 20 \
  --failure-rate 40 \
  --max-retries 5 \
  --timeout 3 \
  --initial-delay 2.0 \
  --backoff 2.0 \
  --max-workers 10
```

### Command-Line Options

- `--devices N`: Number of devices to simulate (default: 10)
- `--failure-rate F`: Percentage of devices that should fail, 0-100 (default: 30)
- `--max-retries N`: Maximum retry attempts per device (default: 3)
- `--timeout T`: Timeout in seconds (default: 5)
- `--initial-delay D`: Initial retry delay in seconds (default: 1.0)
- `--backoff B`: Exponential backoff multiplier (default: 2.0)
- `--max-workers N`: Maximum concurrent worker threads (default: 10)
- `--verbose, -v`: Enable verbose logging

## Example Scenarios

### Scenario 1: Flaky Network

Simulate a network with 30% flaky devices (high failure rate but succeeds after retries):

```bash
python simulator.py --devices 15 --failure-rate 30 --max-retries 5
```

### Scenario 2: Timeout Crisis

Simulate network congestion with timeout failures:

```bash
python simulator.py --devices 20 --failure-rate 20 --timeout 2
```

### Scenario 3: Mixed Failure Types

Default configuration with mix of timeout, flaky, and partial failures:

```bash
python simulator.py --devices 25 --failure-rate 35 --max-retries 4
```

## Example Output

```
=== Automation Failure Simulator Results ===

Total Devices: 10
Successful: 7 (70.0%)
Failed: 2
Timed Out: 1
Partial: 0
Total Time: 8.45s

Average Retries (successful): 1.7

Device Details:
  ✓ router1 (192.168.1.1) - Success on first try (0.23s)
  ✗ router2 (192.168.1.2) - Failed: Timeout after 3 attempts (5.12s)
  ✓ router3 (192.168.1.3) - Success after 2 retries (2.34s)
  ✓ router4 (192.168.1.4) - Success on first try (0.18s)
  ✓ router5 (192.168.1.5) - Success after 3 retries (4.67s)
  ✓ router6 (192.168.1.6) - Success on first try (0.31s)
  ✗ router7 (192.168.1.7) - Failed: Connection failed - flaky device after 3 attempts (3.89s)
  ✓ router8 (192.168.1.8) - Success on first try (0.21s)
  ✓ router9 (192.168.1.9) - Success after 2 retries (1.98s)
  ✓ router10 (192.168.1.10) - Success on first try (0.27s)
```

## Architecture

The simulator consists of several components:

1. **models.py**: Device and TaskResult data models
2. **failures.py**: Failure injection mechanisms (timeout, flaky, partial)
3. **retry_engine.py**: Retry logic with exponential backoff
4. **executor.py**: Concurrent execution with failure isolation
5. **reporter.py**: Outcome summarization and reporting
6. **simulator.py**: Main CLI entry point

## Failure Types

### Timeout
Device doesn't respond within the timeout period. Simulated by sleeping beyond the timeout limit.

### Flaky
Random failures that may succeed on retry. Configurable failure rate (0.0-1.0) determines probability of failure on each attempt.

### Partial Failure
Some operations succeed while others fail. Useful for testing scenarios where a device is partially operational (e.g., config backup works but version check fails).

### None (Healthy)
Device operates normally without failures. Used to simulate healthy devices in the fleet.

## Retry Strategy

The simulator implements exponential backoff:

- **Formula**: `delay = initial_delay * (backoff_multiplier ^ attempt)`
- **Example**: With `initial_delay=1.0` and `backoff_multiplier=2.0`:
  - Attempt 1: immediate
  - Attempt 2: wait 1.0s (1.0 * 2^0)
  - Attempt 3: wait 2.0s (1.0 * 2^1)
  - Attempt 4: wait 4.0s (1.0 * 2^2)

This prevents overwhelming a struggling device/system while giving transient issues time to resolve.

## Failure Isolation

Each device is processed independently using `ThreadPoolExecutor`:

- One device failure does not affect others
- All devices are processed concurrently (up to `max_workers`)
- Results are collected as they complete
- Unexpected exceptions are caught and reported per device

## Interview Value

This tool demonstrates understanding of:

1. **Distributed System Failure Modes**: Recognizes that failures are inevitable in distributed systems
2. **Retry Strategies**: Implements exponential backoff to handle transient failures
3. **Failure Isolation**: Designs systems where one failure doesn't cascade to others
4. **Graceful Degradation**: Continues processing healthy devices even when some fail
5. **Observability**: Provides detailed reporting to understand what succeeded/failed and why
6. **Testing Failure Scenarios**: Simulates failures before they happen in production

### Interview Talking Points

- **"How do you design automation so one failure doesn't break everything?"**
  - Use concurrent execution with failure isolation
  - Each device task is independent and wrapped in exception handling
  - Failed devices are reported but don't stop processing others

- **"What's your retry strategy?"**
  - Exponential backoff prevents overwhelming struggling devices
  - Configurable max attempts balances recovery chance vs. time spent
  - Different failure types may need different retry policies

- **"How do you handle flaky devices?"**
  - Random failure injection with configurable probability
  - Retries give transient issues opportunity to resolve
  - Track success rate and retry statistics to identify patterns

- **"What observability do you build in?"**
  - Per-device status, attempt counts, and timing
  - Summary statistics (success rate, average retries)
  - Clear error messages for troubleshooting

## Code Style

Follows project guidelines:
- Python 3.9+
- Type hints on public functions
- Clear, descriptive names
- Comprehensive error handling
- Logging for debugging and monitoring

## License

This is a demonstration/educational tool.
