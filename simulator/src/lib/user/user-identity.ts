'use client';

const USER_ID_KEY = 'deepracer-user-id';

function randomSuffix() {
  return Math.random().toString(36).slice(2, 8);
}

export function getOrCreateUserId(): string {
  if (typeof window === 'undefined') return 'server';
  const existing = localStorage.getItem(USER_ID_KEY);
  if (existing && existing.trim()) return existing;

  const generated = `driver-${randomSuffix()}`;
  localStorage.setItem(USER_ID_KEY, generated);
  return generated;
}

export function getUserId(): string | null {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(USER_ID_KEY);
}

export function setUserId(value: string) {
  if (typeof window === 'undefined') return;
  localStorage.setItem(USER_ID_KEY, value);
}

