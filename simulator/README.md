# Deep Racer Simulator

Next.js + React Three Fiber simulator for collecting local training data from manual driving and exporting camera/controls datasets.

## What Works

- Manual driving (keyboard) and demo AI driving mode
- Chase-camera 3D simulator + HUD + minimap
- Telemetry capture (`steering`, `throttle`, `speed`, position) to local browser storage
- Forward-facing AI camera capture (`160x120`) at ~10 FPS
- AI camera PIP preview (top-right, toggleable)
- Run export as `.zip` (`frames/`, `controls.csv`, `run.json`)
- Dashboard exports for individual runs and all captured runs

## Local Setup

### Requirements
- Node.js `>=20.9.0`

### Install

```bash
npm install
```

### Run (dev)

```bash
npm run dev
```

Open `http://localhost:3000`.

### Build / checks

```bash
npm run lint
npm run build
```

## Controls

- `Arrow keys` or `WASD`: drive/steer
- `Space`: brake (manual) / pause-resume (AI mode)
- `Esc`: pause/resume (manual mode)
- `1-5`: snap throttle target presets

## Camera Capture + Export Workflow

1. Start a manual run (or demo AI run)
2. Drive laps while the AI camera preview records frames
3. End the run (`Run Complete` screen)
4. The simulator saves image frames to IndexedDB and telemetry metadata to localStorage
5. Click `Download Run (.zip)` to export a training-ready bundle

Zip contents:
- `frames/*.jpg` (numbered 160x120 JPEGs)
- `controls.csv` (`frame_idx,timestamp_ms,steering,throttle,speed`)
- `run.json` (track/run metadata)

## Dashboard

Visit `http://localhost:3000/dashboard` to:
- review runs and local stats
- export JSON/CSV telemetry summaries
- export per-run camera captures
- export `All Runs .zip` for every run with saved image frames

## Storage Notes

- Telemetry run metadata is stored in `localStorage`
- Camera frames are stored in IndexedDB (`deepracer-frame-capture`)
- Clearing site data in the browser removes both

## Current Scope / Next Steps

This simulator currently implements local capture/export only. Backend API uploads, shared class datasets, model training, and ONNX inference are planned but not implemented yet.
