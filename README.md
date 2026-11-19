# CCTV Network Planner

Python 3.10+ CLI tool to estimate **total camera bitrate**, **recording storage**, and **PoE power budget** for an IP CCTV installation. A preliminary planning aid, **not an NVR design certificate**.

## Quick start

No third-party dependencies. Use interactive mode:

```sh
python3 planner.py
```

Or pass all inputs explicitly:

```sh
python3 planner.py --cameras 8 --bitrate-kbps 4096 --days 15 --hours-per-day 24 --poe-watts 8
```

The example above estimates **32.77 Mbps**, **5.31 TB** before storage overhead, a suggested nominal **6 TB** disk capacity, and **76.8 W** PoE with 20% power headroom.

Use `--overhead-percent 30` to change the PoE headroom. All quantities must be finite and positive, except overhead which can be zero; hours per day cannot exceed 24. Invalid arguments exit with a helpful error rather than a traceback.

## How estimates are calculated

- Aggregate Mbps = camera count × per-camera bitrate (kbps) / 1000.
- Recording TB (decimal) = aggregate Mbps × days × hours/day × 3600 / 8,000,000.
- PoE budget = camera count × per-camera Watts × (1 + headroom/100).
- Suggested disk size is the first nominal size in a simple lookup table that fits the estimate; above the table it rounds up to whole TB. **This is not a claim that a single disk of that capacity exists or is appropriate.**

## Tests

```sh
python3 -m unittest -v test_planner.py
```

Covers the documented 8-camera scenario, zero/negative/non-finite values, bounds, overflow, and CLI behavior. Tests are offline and use the Python standard library.

## Limitations

Assumes the configured bitrate remains constant over the specified recording hours. Real storage needs vary with codec, VBR/CBR, recorded scene, audio, motion/event recording, filesystem overhead, RAID/redundancy, and manufacturer behavior. Check NVR ingest limits, switch uplinks, per-port PoE limits, and actual equipment specifications before purchasing or deploying hardware.

No customer names, network topology, real IP addresses, or sensitive workplace material are required.
