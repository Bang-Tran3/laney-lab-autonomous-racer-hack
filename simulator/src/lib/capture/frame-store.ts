'use client';

import { openDB } from 'idb';
import JSZip from 'jszip';

const DB_NAME = 'deepracer-frame-capture';
const DB_VERSION = 1;
const RUNS_STORE = 'capture_runs';
const FRAMES_STORE = 'capture_frames';
const FRAMES_BY_RUN_INDEX = 'by-runId';

export interface IndexedCapturedFrame {
  id: string;
  runId: string;
  frameIdx: number;
  timestamp_ms: number;
  steering: number;
  throttle: number;
  speed: number;
  jpeg: Blob;
}

export interface IndexedRunCaptureMeta {
  runId: string;
  createdAt: string;
  trackId: string;
  driveMode: 'manual' | 'ai';
  durationMs: number;
  lapCount: number;
  bestLapMs: number | null;
  offTrackCount: number;
  frameCount: number;
  sourceFrameSize: { width: number; height: number };
}

async function getDb() {
  return openDB(DB_NAME, DB_VERSION, {
    upgrade(db) {
      if (!db.objectStoreNames.contains(RUNS_STORE)) {
        db.createObjectStore(RUNS_STORE, { keyPath: 'runId' });
      }
      if (!db.objectStoreNames.contains(FRAMES_STORE)) {
        const store = db.createObjectStore(FRAMES_STORE, { keyPath: 'id' });
        store.createIndex(FRAMES_BY_RUN_INDEX, 'runId');
      }
    },
  });
}

export async function saveRunCapture(meta: IndexedRunCaptureMeta, frames: Omit<IndexedCapturedFrame, 'id'>[]): Promise<void> {
  const db = await getDb();
  const tx = db.transaction([RUNS_STORE, FRAMES_STORE], 'readwrite');

  await tx.objectStore(RUNS_STORE).put(meta);

  const existing = await tx.objectStore(FRAMES_STORE).index(FRAMES_BY_RUN_INDEX).getAllKeys(meta.runId);
  for (const key of existing) {
    await tx.objectStore(FRAMES_STORE).delete(key);
  }

  for (const frame of frames) {
    await tx.objectStore(FRAMES_STORE).put({
      ...frame,
      id: `${frame.runId}:${frame.frameIdx}`,
    });
  }

  await tx.done;
}

export async function getRunCaptureMeta(runId: string): Promise<IndexedRunCaptureMeta | null> {
  const db = await getDb();
  return (await db.get(RUNS_STORE, runId)) ?? null;
}

export async function getRunFrames(runId: string): Promise<IndexedCapturedFrame[]> {
  const db = await getDb();
  const frames = await db.getAllFromIndex(FRAMES_STORE, FRAMES_BY_RUN_INDEX, runId);
  return frames.sort((a, b) => a.frameIdx - b.frameIdx);
}

export async function hasRunCapture(runId: string): Promise<boolean> {
  const meta = await getRunCaptureMeta(runId);
  return !!meta && meta.frameCount > 0;
}

function formatFrameName(frameIdx: number): string {
  return `${String(frameIdx).padStart(6, '0')}.jpg`;
}

function buildControlsCsv(frames: IndexedCapturedFrame[]): string {
  const header = 'frame_idx,timestamp_ms,steering,throttle,speed';
  const rows = frames.map((f) => [f.frameIdx, f.timestamp_ms, f.steering, f.throttle, f.speed].join(','));
  return [header, ...rows].join('\n');
}

async function toUint8Array(blob: Blob): Promise<Uint8Array> {
  if (typeof (blob as Blob & { arrayBuffer?: () => Promise<ArrayBuffer> }).arrayBuffer === 'function') {
    return new Uint8Array(await blob.arrayBuffer());
  }
  const buffer = await new Response(blob).arrayBuffer();
  return new Uint8Array(buffer);
}

function toArrayBufferForBlob(bytes: Uint8Array): ArrayBuffer {
  const copy = new Uint8Array(bytes.byteLength);
  copy.set(bytes);
  return copy.buffer as ArrayBuffer;
}

export async function exportRunControlsCsvBlob(runId: string): Promise<Blob> {
  const frames = await getRunFrames(runId);
  if (frames.length === 0) {
    throw new Error('No captured image frames found for this run.');
  }
  return new Blob([buildControlsCsv(frames)], { type: 'text/csv' });
}

export async function getRunCaptureFileBlobs(runId: string): Promise<{ framesZip: Blob; controlsCsv: Blob }> {
  const [framesZip, controlsCsv] = await Promise.all([
    exportRunCaptureZip(runId),
    exportRunControlsCsvBlob(runId),
  ]);
  return { framesZip, controlsCsv };
}

export async function exportRunCaptureZipBytes(runId: string): Promise<Uint8Array> {
  const [meta, frames] = await Promise.all([getRunCaptureMeta(runId), getRunFrames(runId)]);
  if (!meta || frames.length === 0) {
    throw new Error('No captured image frames found for this run.');
  }

  const zip = new JSZip();
  const framesDir = zip.folder('frames');
  if (!framesDir) {
    throw new Error('Failed to create zip frame directory.');
  }

  for (const frame of frames) {
    framesDir.file(formatFrameName(frame.frameIdx), await toUint8Array(frame.jpeg));
  }

  zip.file('controls.csv', buildControlsCsv(frames));
  zip.file('run.json', JSON.stringify(meta, null, 2));

  return zip.generateAsync({ type: 'uint8array', compression: 'DEFLATE', compressionOptions: { level: 6 } });
}

export async function exportRunCaptureZip(runId: string): Promise<Blob> {
  const bytes = await exportRunCaptureZipBytes(runId);
  const buffer = toArrayBufferForBlob(bytes);
  return new Blob([buffer], { type: 'application/zip' });
}

export async function exportAllRunCapturesZip(runIds: string[]): Promise<Blob> {
  const zip = new JSZip();
  const included: { runId: string; frameCount: number }[] = [];

  for (const runId of runIds) {
    const [meta, frames] = await Promise.all([getRunCaptureMeta(runId), getRunFrames(runId)]);
    if (!meta || frames.length === 0) continue;

    included.push({ runId, frameCount: frames.length });
    const root = zip.folder(runId);
    const framesDir = root?.folder('frames');
    if (!root || !framesDir) continue;

    for (const frame of frames) {
      framesDir.file(formatFrameName(frame.frameIdx), await toUint8Array(frame.jpeg));
    }

    root.file('controls.csv', buildControlsCsv(frames));
    root.file('run.json', JSON.stringify(meta, null, 2));
  }

  zip.file('manifest.json', JSON.stringify({ generatedAt: new Date().toISOString(), runs: included }, null, 2));
  const bytes = await zip.generateAsync({ type: 'uint8array', compression: 'DEFLATE', compressionOptions: { level: 6 } });
  const buffer = toArrayBufferForBlob(bytes);
  return new Blob([buffer], { type: 'application/zip' });
}

export function downloadBlob(blob: Blob, fileName: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  a.click();
  setTimeout(() => URL.revokeObjectURL(url), 1000);
}
