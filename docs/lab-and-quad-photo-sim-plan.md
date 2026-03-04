# Lab & Quad Photo-Sim Plan

## Goal

Build photo-based simulator environments (lab + quad) that better match what the physical racer sees, while keeping a controlled route/waypoint workflow that fits the current training pipeline.

This is a **sim-to-real visual bridge** plan, not a full free-roam navigation plan.

## Recommended Approach (Scope)

Start with:
- **Photoreal route environments**
- **Defined drivable paths**
- **Existing vision -> steering model pipeline**

Do **not** start with:
- full open-world/free-roam navigation
- perfect 3D digital twin before testing

## Phase 1: Capture Preparation (Before Taking Photos)

### 1. Define a repeatable real-world route
- Choose one **lab route** and one **quad route**
- Mark:
  - start point
  - direction of travel
  - path width
  - turns/checkpoints
- Use tape/cones/chalk so the route is repeatable for physical tests

### 2. Record physical dimensions (scale)
- Measure and write down:
  - room/hallway width
  - desk/table sizes
  - aisle widths
  - turn radii (approx)
  - quad path widths / curb offsets
- Include a few photos with a **known-size object** (meter stick, tape measure, marker board)

### 3. Match camera perspective to the racer
- Take photos/video from approximately the **same height** as the racer camera
- Match approximate **camera tilt angle** and forward orientation
- Prefer “driving viewpoint” shots over human eye-level shots

### 4. Plan lighting conditions
- Capture one “baseline” set in stable lighting
- If possible, also capture:
  - brighter version
  - dimmer version
  - mixed shadow/sun version (quad)

### 5. Privacy and cleanup
- Avoid faces and identifying info (whiteboards, names, screens)
- If unavoidable, plan to blur/crop before using assets

## Phase 2: Photo Capture Plan (Lab First)

### Lab capture passes (recommended)
- **Pass A: Route centerline**
  - Walk the marked route slowly, frequent overlapping photos
- **Pass B: Left offset**
  - Same route, offset slightly left
- **Pass C: Right offset**
  - Same route, offset slightly right
- **Pass D: Static environment coverage**
  - Corners, tables, chairs, walls, floor textures, doorways

### Quad capture passes (recommended)
- **Pass A: Route centerline**
- **Pass B: Left/right offsets**
- **Pass C: Surface detail**
  - pavement, edges, curbs, grass transitions
- **Pass D: Landmark coverage**
  - walls, railings, building edges, signs (if allowed)

### Capture quality rules
- High overlap (roughly **60-80%**)
- Avoid motion blur
- Keep camera exposure stable if possible
- Take extra shots at turns and cluttered areas

## Phase 3: Build Simulator Environment (Practical v1)

### Start with a simplified 3D environment + photo textures
Use:
- simple room/quad geometry
- photo textures/planes
- existing table/chair/cone props
- existing waypoint routes

Why:
- Fastest way to test sim-to-real improvement
- Works with the current browser simulator
- Easier than full photogrammetry integration

### Build order (recommended)
1. **Lab route environment** (first)
2. Train/test model on lab variants
3. **Quad route environment** (second)
4. Compare performance across indoor/outdoor visuals

## Phase 4: Simulator-to-Hardware Parity Improvements

Prioritize these before over-investing in graphics detail:

### Camera parity
- Match approximate racer camera:
  - height
  - FOV
  - tilt angle
- Keep model input path at current `160x120` unless changed intentionally

### Visual variation (domain randomization)
Add small variation on top of the photo-based environment:
- brightness/contrast shifts
- small obstacle movement
- minor camera noise/blur
- slight color temperature shifts

This improves generalization to real lab/quad conditions.

## Phase 5: Validation Plan

### Compare these setups
1. Synthetic classroom tracks only
2. Photo-based lab route environment
3. Photo-based lab + randomization

### Track key outcomes
- lap completion rate
- off-track count
- steering smoothness
- recovery behavior after drift
- transfer performance on physical racer (same route)

## What Not To Do Yet

- Do not treat the lab/quad as a full free-roam navigation problem yet
- Do not wait for a perfect photogrammetry pipeline before testing
- Do not rely on one single layout or one lighting condition

## Immediate Next Steps (Actionable)

1. Create a **shot list** for the lab route
2. Mark the physical lab route (tape/cones)
3. Capture one baseline lab photo set
4. Build one photo-based lab environment in the simulator
5. Collect new runs + retrain + compare against current classroom variants

## Handoff Notes (for Team)

This plan is compatible with the current stack:
- route-based waypoint driving in simulator
- shared runs API
- trainer ONNX export
- browser ONNX inference
- physical runtime foundation with safety overrides

It is intentionally staged so hardware bring-up and environment realism work can proceed in parallel.

