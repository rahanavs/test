Business & Technical Requirements: Infotainment Platform Health Checker (MVP)

Document Control

Project Name: Infotainment Platform Health Checker (MVP)

Target Audience: Platform Software Testing & QA Engineers (Automotive Infotainment / Android Automotive OS)

Training Duration: 16 Hours (Concept + Hands-on)

Training Objective: End-to-end integration of GitHub Copilot across the test lifecycle (Requirement Analysis  Test Design  Test Automation  Refactoring  Code Review  CI/CD  Cloud Test Artifact Deployment)

Technical Scope: Base OS / Android layer health verification via simulated JSON telemetry

Explicit Exclusions: CAN bus, UDS / On-Board Diagnostics, physical ECU wiring, hardware-in-the-loop (HIL) test racks, database systems

1. System Overview & Context

In automotive platform software testing, establishing whether a build or target image is sufficiently stable for test execution is a critical first step. Flaky physical connections or waiting for physical bench availability often causes bottlenecks.

This MVP defines a lightweight, standalone test automation utility built in Python using pytest. The system evaluates core health parameters of an Android-based infotainment platform (such as boot completion, ADB connectivity, network availability, critical daemons/services, and memory/CPU thresholds).

To ensure complete portability during the 16-hour training without relying on physical test benches, the platform state is read from a mock telemetry feed: test_data/platform_status.json.

2. Simulated Environment Schema

The test automation suite reads platform health metrics directly from a structured JSON document representing the vehicle infotainment state.

File: test_data/platform_status.json

{
  "boot_status": "SUCCESS",
  "adb_status": "CONNECTED",
  "network_status": "CONNECTED",
  "services": {
    "audio": "RUNNING",
    "media": "RUNNING",
    "connectivity": "RUNNING",
    "system_service": "RUNNING"
  },
  "resources": {
    "cpu": 65,
    "memory": 70,
    "storage": 45
  }
}


3. Functional Requirements (FR)

FR1 – Platform Boot State Verification

The framework must inspect the boot lifecycle indicator of the platform.

Criterion: If boot_status equals "SUCCESS", evaluate to PASS.

Failure Condition: If boot_status is "FAILED", empty, null, or the key is absent, evaluate to FAIL.

FR2 – Android Debug Bridge (ADB) Availability

The framework must verify that developer and test communication channels are operational.

Criterion: If adb_status equals "CONNECTED", evaluate to PASS.

Failure Condition: If adb_status equals "OFFLINE", "DISCONNECTED", or "UNAUTHORIZED", evaluate to FAIL.

FR3 – Network Connectivity Status

The framework must verify that internal network interfaces (Ethernet / Virtual CAN-IP gateway) are active.

Criterion: If network_status equals "CONNECTED", evaluate to PASS.

Failure Condition: Any other status value or missing field must evaluate to FAIL.

FR4 – Critical System Services Health

The framework must confirm that the baseline services required for platform operation are actively running.

Required Service Keys: audio, media, connectivity, system_service.

Criterion: Every required service must report "RUNNING".

Failure Condition: If any required service has a status of "STOPPED", "CRASHED", or is omitted from the payload, evaluate to FAIL.

FR5 – Resource Threshold Auditing

The framework must audit platform vitals to ensure testing is not performed on an overloaded platform.

Defined Thresholds:

CPU Usage: 

Memory Usage: 

Storage Availability: 

Failure Condition: If any resource violates its respective threshold, the resource check evaluates to FAIL.

FR6 – Consolidated Health Verdict

The framework must synthesize individual audit items into a single platform verdict.

Rule: Overall status is PASS if and only if FR1 through FR5 are all PASS.

Rule: If any mandatory item fails, the consolidated status must be FAIL.

4. Test Scenario Matrix

The test engineering team will develop automated test cases mapped directly to these functional requirements using pytest:

Test Case ID

Target Requirement

Test Scenario Description

Injected Mock Value

Expected Verdict

TC01

FR1

Normal boot sequence completed

boot_status = "SUCCESS"

PASS

TC02

FR1

Boot sequence interrupted or failed

boot_status = "FAILED"

FAIL

TC03

FR2

ADB connection established

adb_status = "CONNECTED"

PASS

TC04

FR2

ADB communication unavailable

adb_status = "OFFLINE"

FAIL

TC05

FR3

Platform network active

network_status = "CONNECTED"

PASS

TC06

FR3

Network connection severed

network_status = "DISCONNECTED"

FAIL

TC07

FR4

All core platform services running

All services reporting "RUNNING"

PASS

TC08

FR4

Audio service terminated unexpectedly

"audio": "STOPPED"

FAIL

TC09

FR5

Resource consumption within limits

CPU: 65%, Mem: 70%, Storage: 45%

PASS

TC10

FR5

High CPU load detected

CPU: 95%

FAIL

TC11

FR5

Critical memory exhaustion detected

Memory: 94%

FAIL

TC12

FR5

Storage capacity exhausted

Storage: 4%

FAIL

TC13

FR6

Complete platform health check pass

All inputs nominal

Overall: PASS

TC14

FR6

Cascading failure check

Boot: PASS, Services: FAIL

Overall: FAIL

5. Repository Architecture

Trainees will build out the following project layout during hands-on modules:

infotainment-platform-health-checker/
│
├── .github/
│   └── workflows/
│       └── test.yml                 # CI/CD pipeline automation
│
├── src/
│   ├── __init__.py
│   ├── platform_checker.py         # Handles FR1, FR2, FR3 logic
│   ├── service_checker.py          # Handles FR4 daemon checks
│   └── resource_checker.py         # Handles FR5 resource checks
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                 # Shared pytest fixtures & mock loaders
│   ├── test_boot.py                # Test suites for FR1 & FR2
│   ├── test_network.py             # Test suites for FR3
│   ├── test_services.py            # Test suites for FR4
│   └── test_resources.py           # Test suites for FR5 & FR6
│
├── test_data/
│   └── platform_status.json        # Base simulated telemetry file
│
├── requirements.txt                # pytest, pytest-html, boto3
└── README.md                       # Test instructions and documentation


6. 16-Hour Training Blueprint (Concept + Hands-on)

Day 1: Requirements Analysis, Framework Design & Automation (8 Hours)

Block 1: Requirement Decomposition with GitHub Copilot Chat (2h)

Topics: Context management (#file, #selection), prompt crafting, parsing automotive requirements.

Hands-on Task: Pass the functional requirements to Copilot Chat to extract missing edge cases (e.g., malformed JSON, partial payloads) and scaffold test case specifications.

Block 2: Implementation of Checker Modules (3h)

Topics: Inline code generation, type hinting, modular Python design.

Hands-on Task: Generate src/platform_checker.py, src/service_checker.py, and src/resource_checker.py using Copilot Inline prompts.

Block 3: Pytest Automation & Happy-Path Validation (3h)

Topics: Pytest fixtures, test hooks, assertions, parameterization.

Hands-on Task: Build conftest.py with mock data loading fixtures and write tests for nominal conditions (TC01, TC03, TC05, TC07, TC09, TC13).

Day 2: Advanced Mocking, Refactoring, CI/CD & Cloud Delivery (8 Hours)

Block 4: Simulating Failure States & JSON Mutations (2h)

Topics: Test-driven edge-case handling, negative testing without hardware.

Hands-on Task: Use Copilot to write parameterized tests simulating crashed services, disk-full states, and missing keys (TC02, TC04, TC06, TC08, TC10–TC12, TC14).

Block 5: Code Quality, Refactoring & Review (2h)

Topics: Slash commands (/explain, /fix), PEP 8 compliance, robust logging for automotive test diagnostics.

Hands-on Task: Run a Copilot-assisted code review on src/ and tests/, refactoring raw print statements to structured logging and adding docstrings.

Block 6: CI/CD Pipeline Automation with GitHub Actions (2h)

Topics: Workflow triggers, virtual runners, test execution automation, report bundling.

Hands-on Task: Use Copilot to write .github/workflows/test.yml that installs dependencies, executes pytest, and compiles HTML test reports (pytest-html).

Block 7: Cloud Test Report Publishing & Course Wrap-up (2h)

Topics: AWS S3 integration, credential management via GitHub Secrets, final demo.

Hands-on Task: Extend the GitHub Actions pipeline with an automated step to publish test run reports (report.html) into an AWS S3 bucket for team-wide visibility.