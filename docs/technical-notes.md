# Technical Notes

This project is inspired by real pre-sales technical analysis for CCTV systems.

## Main planning variables

- Number of cameras
- Resolution
- FPS
- Codec
- Bitrate
- Recording hours per day
- Retention days
- PoE consumption
- NVR incoming bandwidth
- Switch uplink capacity

## Important considerations

The storage result is an estimate. Real systems depend on:

- H.264/H.265 compression;
- CBR or VBR configuration;
- scene complexity;
- motion recording;
- redundancy;
- manufacturer-specific recording behavior.

## Practical use

The tool is useful during an early design phase to understand whether a proposed CCTV system is compatible with basic network, storage and power constraints.
