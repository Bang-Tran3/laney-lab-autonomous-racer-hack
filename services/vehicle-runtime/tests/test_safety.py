from vehicle_runtime.safety import SafetyPolicy


def test_safety_clamps_and_scales_controls():
    policy = SafetyPolicy(max_throttle=0.4, steering_scale=1.5)
    cmd = policy.apply(steering=0.8, throttle=0.9, estop=False)
    assert cmd.steering == 1.0
    assert cmd.throttle == 0.4


def test_safety_estop_overrides_controls():
    policy = SafetyPolicy(max_throttle=0.4, steering_scale=1.0)
    cmd = policy.apply(steering=0.3, throttle=0.2, estop=True)
    assert cmd.steering == 0.0
    assert cmd.throttle == 0.0

