# Serial Bridge Protocol (`serial-json-v1`)

This is the current protocol emitted by `services/vehicle-runtime` when:

- `VEHICLE_ACTUATOR_BACKEND=serial`

The controller (Arduino/ESP32/etc.) should read UTF-8 lines, parse JSON, and apply hardware outputs.

## Messages Sent by Runtime

### Control command

```json
{"type":"control","steering":0.12,"throttle":0.30}
```

- `steering`: normalized float in `[-1, 1]`
- `throttle`: normalized float in `[0, max_throttle]` after runtime safety clamp

### Stop command

```json
{"type":"stop"}
```

Controller should immediately drive throttle to neutral and optionally center steering.

## Expected Controller Behavior (stub for classmate)

- [ ] Parse newline-delimited JSON reliably
- [ ] Apply steering mapping from `hardware-profile.stub.json`
- [ ] Apply throttle mapping from `hardware-profile.stub.json`
- [ ] Implement controller-side watchdog timeout (no command received -> stop)
- [ ] Optional ACK/telemetry line back to host (future)

## Future Protocol Extensions (not implemented yet)

- `{"type":"estop","enabled":true}`
- `{"type":"telemetry","battery_v":7.2,"estop":false}`
- `{"type":"heartbeat","ts_ms":12345}`

