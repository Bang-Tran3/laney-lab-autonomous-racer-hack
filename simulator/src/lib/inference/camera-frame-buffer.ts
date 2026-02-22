'use client';

export interface CameraFrameSnapshot {
  seq: number;
  width: number;
  height: number;
  rgba: Uint8ClampedArray;
  capturedAtMs: number;
  runTimestampMs: number;
}

let latestFrame: CameraFrameSnapshot | null = null;
let seqCounter = 0;

export function publishLatestCameraFrame(input: {
  width: number;
  height: number;
  rgba: Uint8ClampedArray;
  capturedAtMs: number;
  runTimestampMs: number;
}) {
  latestFrame = {
    seq: ++seqCounter,
    width: input.width,
    height: input.height,
    rgba: new Uint8ClampedArray(input.rgba),
    capturedAtMs: input.capturedAtMs,
    runTimestampMs: input.runTimestampMs,
  };
}

export function getLatestCameraFrame(): CameraFrameSnapshot | null {
  return latestFrame;
}

export function resetLatestCameraFrame() {
  latestFrame = null;
}
