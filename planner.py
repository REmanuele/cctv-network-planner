#!/usr/bin/env python3
"""CCTV Network Planner.

Estimate bandwidth, recording storage and PoE budget for CCTV systems.
"""

from __future__ import annotations

import argparse
import math
from dataclasses import dataclass


DISK_SIZES_TB = [1, 2, 4, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64]


@dataclass
class CCTVPlan:
    cameras: int
    bitrate_kbps: float
    days: float
    hours_per_day: float
    poe_watts: float
    overhead_percent: float = 20.0

    @property
    def total_bandwidth_mbps(self) -> float:
        return self.cameras * self.bitrate_kbps / 1000

    @property
    def storage_tb(self) -> float:
        seconds = self.days * self.hours_per_day * 3600
        megabits = self.total_bandwidth_mbps * seconds
        megabytes = megabits / 8
        terabytes = megabytes / 1_000_000
        return terabytes

    @property
    def recommended_disk_tb(self) -> int:
        required = self.storage_tb
        for size in DISK_SIZES_TB:
            if size >= required:
                return size
        return math.ceil(required)

    @property
    def poe_budget_watts(self) -> float:
        base = self.cameras * self.poe_watts
        return base * (1 + self.overhead_percent / 100)


def ask_float(prompt: str, default: float) -> float:
    value = input(f"{prompt} [{default}]: ").strip()
    return default if not value else float(value.replace(",", "."))


def ask_int(prompt: str, default: int) -> int:
    value = input(f"{prompt} [{default}]: ").strip()
    return default if not value else int(value)


def build_plan_from_args(args: argparse.Namespace) -> CCTVPlan:
    if args.interactive:
        return CCTVPlan(
            cameras=ask_int("Number of cameras", args.cameras or 8),
            bitrate_kbps=ask_float("Bitrate per camera in kbps", args.bitrate_kbps or 4096),
            days=ask_float("Recording retention in days", args.days or 15),
            hours_per_day=ask_float("Recording hours per day", args.hours_per_day or 24),
            poe_watts=ask_float("PoE consumption per camera in watts", args.poe_watts or 8),
        )

    missing = [name for name in ["cameras", "bitrate_kbps", "days", "hours_per_day", "poe_watts"] if getattr(args, name) is None]
    if missing:
        raise SystemExit(f"Missing arguments: {', '.join(missing)}. Use --interactive or provide all values.")

    return CCTVPlan(
        cameras=args.cameras,
        bitrate_kbps=args.bitrate_kbps,
        days=args.days,
        hours_per_day=args.hours_per_day,
        poe_watts=args.poe_watts,
    )


def render_report(plan: CCTVPlan) -> str:
    return f"""CCTV NETWORK PLAN
=================
Cameras: {plan.cameras}
Bitrate per camera: {plan.bitrate_kbps:.0f} kbps
Recording: {plan.hours_per_day:g} h/day for {plan.days:g} days
PoE per camera: {plan.poe_watts:g} W

Results
-------
Total bandwidth: {plan.total_bandwidth_mbps:.2f} Mbps
Estimated storage: {plan.storage_tb:.2f} TB
Recommended disk size: {plan.recommended_disk_tb} TB
Estimated PoE budget (+{plan.overhead_percent:.0f}% overhead): {plan.poe_budget_watts:.1f} W

Planning notes
--------------
- Use this as a first estimate for pre-sales analysis.
- Add margin for VBR peaks, motion, RAID, spare capacity and future expansion.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate CCTV bandwidth, storage and PoE budget.")
    parser.add_argument("--interactive", "-i", action="store_true", help="Ask values interactively.")
    parser.add_argument("--cameras", type=int, help="Number of cameras.")
    parser.add_argument("--bitrate-kbps", type=float, help="Bitrate per camera in kbps.")
    parser.add_argument("--days", type=float, help="Recording retention in days.")
    parser.add_argument("--hours-per-day", type=float, help="Recording hours per day.")
    parser.add_argument("--poe-watts", type=float, help="PoE consumption per camera in watts.")
    args = parser.parse_args()

    if not any(vars(args).values()):
        args.interactive = True

    plan = build_plan_from_args(args)
    print(render_report(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
