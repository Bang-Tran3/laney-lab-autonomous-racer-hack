'use client';

import { useEffect } from 'react';
import { flushRunSyncQueue } from '@/lib/api/run-sync-queue';

export function SyncQueueWorker() {
  useEffect(() => {
    void flushRunSyncQueue();

    const onOnline = () => {
      void flushRunSyncQueue();
    };
    window.addEventListener('online', onOnline);

    const timer = window.setInterval(() => {
      void flushRunSyncQueue();
    }, 30_000);

    return () => {
      window.removeEventListener('online', onOnline);
      window.clearInterval(timer);
    };
  }, []);

  return null;
}
