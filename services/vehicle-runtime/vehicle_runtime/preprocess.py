from __future__ import annotations

import numpy as np
from PIL import Image


def frame_to_model_input_nchw(frame_rgb: np.ndarray, *, width: int = 160, height: int = 120) -> np.ndarray:
    if frame_rgb.ndim != 3 or frame_rgb.shape[2] != 3:
        raise ValueError("Expected RGB image array with shape [H, W, 3]")
    image = Image.fromarray(frame_rgb.astype(np.uint8), mode="RGB").resize((width, height))
    arr = np.asarray(image, dtype=np.float32) / 255.0
    chw = np.transpose(arr, (2, 0, 1))
    return np.expand_dims(chw, axis=0)

