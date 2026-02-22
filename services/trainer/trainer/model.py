from __future__ import annotations


def build_driving_model():
    try:
        import torch.nn as nn
    except Exception as exc:  # pragma: no cover - import guarded for environments without torch
        raise RuntimeError("PyTorch is required to build the driving model.") from exc

    class DrivingModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.conv = nn.Sequential(
                nn.Conv2d(3, 24, 5, stride=2), nn.ReLU(),
                nn.Conv2d(24, 36, 5, stride=2), nn.ReLU(),
                nn.Conv2d(36, 48, 5, stride=2), nn.ReLU(),
                nn.Conv2d(48, 64, 3), nn.ReLU(),
                nn.Conv2d(64, 64, 3), nn.ReLU(),
                # Input is fixed at 120x160; use fixed pooling for ONNX compatibility.
                nn.AvgPool2d(kernel_size=(4, 3), stride=(4, 3)),
            )
            self.fc = nn.Sequential(
                nn.Flatten(),
                nn.Linear(64 * 2 * 4, 100), nn.ReLU(), nn.Dropout(0.3),
                nn.Linear(100, 50), nn.ReLU(), nn.Dropout(0.3),
                nn.Linear(50, 10), nn.ReLU(),
                nn.Linear(10, 1), nn.Tanh(),
            )

        def forward(self, x):
            x = self.conv(x)
            return self.fc(x)

    return DrivingModel()
