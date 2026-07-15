# CCTV Network Planner

A simple Python tool to estimate **bandwidth**, **recording storage** and **PoE budget** for CCTV systems.

## Why I built it

During CCTV system design and pre-sales technical analysis, it is important to quickly estimate network bandwidth, recording retention and infrastructure requirements.

This tool converts basic camera parameters into practical planning values.

## Features

- Total bandwidth estimation
- Storage calculation based on bitrate and retention days
- Suggested disk size
- PoE budget estimation
- Interactive mode and command-line mode
- Example scenarios for small and medium systems

## Tech stack

- Python 3
- CCTV system design
- Networking
- Pre-sales technical analysis

## Usage

Interactive mode:

```bash
python3 planner.py
```

Command-line mode:

```bash
python3 planner.py --cameras 8 --bitrate-kbps 4096 --days 15 --hours-per-day 24 --poe-watts 8
```

Example output:

```text
CCTV NETWORK PLAN
Cameras: 8
Bitrate per camera: 4096 kbps
Total bandwidth: 32.77 Mbps
Estimated storage: 5.31 TB
Recommended disk size: 6 TB
Estimated PoE budget: 76.8 W
```

## Notes

The result is an estimate. Real systems depend on codec, scene complexity, motion recording, VBR/CBR configuration, redundancy and manufacturer-specific recording behavior.
