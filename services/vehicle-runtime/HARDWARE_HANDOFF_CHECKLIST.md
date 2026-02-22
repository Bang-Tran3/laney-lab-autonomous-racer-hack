# Hardware Handoff Checklist (Stubbed for Classmate Bring-Up)

Use this file during racer unit bring-up. Fill in the blanks and commit updates as values become known.

Status: `stubbed` (software runtime is ready for hardware integration; values below are placeholders)

## 1. Actuator Interface (choose one)

- [ ] `serial` bridge (Arduino / ESP32 / RP2040)
- [ ] `pca9685` direct from SBC
- [ ] `ros` topic bridge
- [ ] Other: `________________`

Selected interface: `TBD`

## 2. Controller Connection Details

- Serial port path (if serial): `TBD` (example `COM7` / `/dev/ttyUSB0`)
- Baud rate: `TBD` (default software supports `115200`)
- Controller firmware repo/path: `TBD`
- Command protocol version: `serial-json-v1` (current runtime output)

## 3. Steering Mapping (normalized `[-1, 1]` -> hardware)

- Steering center (PWM us / angle / command units): `TBD`
- Steering full-left min: `TBD`
- Steering full-right max: `TBD`
- Inverted? `TBD` (`yes/no`)
- Deadband around center: `TBD`

Calibration notes:
- `TBD`

## 4. Throttle Mapping (normalized `[0, max_throttle]` -> hardware)

- Throttle neutral (stop) value: `TBD`
- Throttle min forward value: `TBD`
- Throttle max forward value: `TBD`
- Reverse enabled? `TBD` (`yes/no`)
- If reverse enabled: reverse min/max values: `TBD`

ESC/drive notes:
- `TBD`

## 5. Safety / Watchdog Expectations

- Controller watchdog timeout ms (no command received -> neutral/stop): `TBD`
- Boot behavior (neutral on boot?): `TBD`
- Loss-of-camera behavior expectation: `stop` (runtime already safe-stops)
- E-stop wiring available? `TBD`
- E-stop reset behavior: `TBD`

## 6. Camera / Mounting Notes

- Camera device used: `TBD`
- Mount position/angle: `TBD`
- Resolution stable at `160x120` path? `TBD`
- Exposure/white-balance lock available? `TBD`

## 7. Bring-Up Test Results (append)

### Test 1: Serial command visibility
- Date:
- Result:
- Notes:

### Test 2: Steering-only motion (wheels off ground)
- Date:
- Result:
- Notes:

### Test 3: Throttle neutral and low-speed crawl
- Date:
- Result:
- Notes:

### Test 4: E-stop and watchdog stop behavior
- Date:
- Result:
- Notes:

## 8. Integration Ready Definition

Mark this file `ready-for-adapter` when:
- interface selected
- mapping values filled
- watchdog behavior confirmed
- serial/transport tested end-to-end

