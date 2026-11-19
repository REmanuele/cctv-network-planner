#!/usr/bin/env python3
"""Estimate CCTV bandwidth, recording storage, and PoE power requirements."""

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

    def __post_init__(self) -> None:
        if isinstance(self.cameras, bool) or not isinstance(self.cameras, int) or self.cameras <= 0:
            raise ValueError("cameras must be a positive integer")
        for name in ("bitrate_kbps", "days", "hours_per_day", "poe_watts"):
            value = getattr(self, name)
            if not math.isfinite(value) or value <= 0:
                raise ValueError(f"{name} must be a finite number greater than zero")
        if self.hours_per_day > 24:
            raise ValueError("hours_per_day cannot exceed 24")
        if not math.isfinite(self.overhead_percent) or self.overhead_percent < 0:
            raise ValueError("overhead_percent must be a finite number >= 0")
        if not all(math.isfinite(value) for value in (
            self.total_bandwidth_mbps, self.storage_tb, self.poe_budget_watts
        )):
            raise ValueError("calculated values are too large")

    @property
    def total_bandwidth_mbps(self) -> float:
        return self.cameras * self.bitrate_kbps / 1000

    @property
    def storage_tb(self) -> float:
        seconds = self.days * self.hours_per_day * 3600
        megabits = self.total_bandwidth_mbps * seconds
        megabytes = megabits / 8
        return megabytes / 1_000_000

    @property
    def recommended_disk_tb(self) -> int:
        required = self.storage_tb
        for size in DISK_SIZES_TB:
            if size >= required:
                return size
        return math.ceil(required)

    @property
    def poe_budget_watts(self) -> float:
        return self.cameras * self.poe_watts * (1 + self.overhead_percent / 100)


def ask_float(prompt: str, default: float) -> float:
    value = input(f"{prompt} [{default}]: ").strip()
    return default if not value else float(value.replace(",", "."))


def ask_int(prompt: str, default: int) -> int:
    value = input(f"{prompt} [{default}]: ").strip()
    return default if not value else int(value)


def build_plan_from_args(args: argparse.Namespace) -> CCTVPlan:
    if args.interactive:
        return CCTVPlan(
            cameras=ask_int("Number of cameras", args.cameras if args.cameras is not None else 8),
            bitrate_kbps=ask_float("Bitrate per camera in kbps", args.bitrate_kbps if args.bitrate_kbps is not None else 4096),
            days=ask_float("Recording retention in days", args.days if args.days is not None else 15),
            hours_per_day=ask_float("Recording hours per day", args.hours_per_day if args.hours_per_day is not None else 24),
            poe_watts=ask_float("PoE consumption per camera in watts", args.poe_watts if args.poe_watts is not None else 8),
            overhead_percent=args.overhead_percent,
        )

    required = ("cameras", "bitrate_kbps", "days", "hours_per_day", "poe_watts")
    missing = [name for name in required if getattr(args, name) is None]
    if missing:
        raise ValueError(f"missing arguments: {', '.join(missing)}; use --interactive or supply all values")
    return CCTVPlan(
        cameras=args.cameras,
        bitrate_kbps=args.bitrate_kbps,
        days=args.days,
        hours_per_day=args.hours_per_day,
        poe_watts=args.poe_watts,
        overhead_percent=args.overhead_percent,
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
- This is an early planning estimate, not a final system specification.
- Allow for bitrate peaks, RAID, spare capacity, PoE switch limits and expansion.
- Suggested disk capacity is nominal; it may require multiple disks.
"""


def main() -> int:
    parser = argparse.ArgumentParser(description="Estimate CCTV bandwidth, storage, and PoE budget.")
    parser.add_argument("--interactive", "-i", action="store_true", help="Ask values interactively")
    parser.add_argument("--cameras", type=int, help="Number of cameras")
    parser.add_argument("--bitrate-kbps", type=float, help="Bitrate per camera (kbps)")
    parser.add_argument("--days", type=float, help="Retention days")
    parser.add_argument("--hours-per-day", type=float, help="Recording hours per day (0 < h <= 24)")
    parser.add_argument("--poe-watts", type=float, help="PoE consumption per camera (W)")
    parser.add_argument("--overhead-percent", type=float, default=20, help="PoE headroom percentage (default: 20)")
    args = parser.parse_args()
    if not args.interactive and all(getattr(args, key) is None for key in (
        "cameras", "bitrate_kbps", "days", "hours_per_day", "poe_watts"
    )):
        args.interactive = True
    try:
        plan = build_plan_from_args(args)
    except (ValueError, EOFError) as exc:
        parser.error(str(exc))
    print(render_report(plan))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
