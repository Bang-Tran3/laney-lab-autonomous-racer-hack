'use client';

import { useEffect, useRef, useState } from 'react';
import { useGameStore } from '@/lib/stores/game-store';

const RADIUS = 70; // joystick radius in px

interface JoystickVisual {
  baseX: number;
  baseY: number;
  knobX: number;
  knobY: number;
}

function clamp(v: number, min: number, max: number) {
  return Math.max(min, Math.min(max, v));
}

/**
 * Virtual joystick for touchscreen input.
 * Appears where the user touches, disappears on lift.
 * X axis → steering, Y axis → throttle (up) / brake (down).
 * Writes to the unified store.input; gamepad takes priority if connected.
 */
export function TouchHandler() {
  const [joystick, setJoystick] = useState<JoystickVisual | null>(null);
  const activeTouchId = useRef<number | null>(null);

  useEffect(() => {
    function onTouchStart(e: TouchEvent) {
      // Ignore if gamepad already owns input, or if a touch is already tracked
      if (useGameStore.getState().activeInputDevice === 'gamepad') return;
      if (activeTouchId.current !== null) return;

      // Don't hijack taps on UI buttons / overlays
      const target = e.target as Element;
      if (target.closest('button, a, [role="button"]')) return;

      const touch = e.changedTouches[0];
      activeTouchId.current = touch.identifier;

      useGameStore.getState().setActiveInputDevice('touch');
      useGameStore.getState().setInput({ steer: 0, throttle: 0, brake: false });

      setJoystick({ baseX: touch.clientX, baseY: touch.clientY, knobX: touch.clientX, knobY: touch.clientY });
    }

    function onTouchMove(e: TouchEvent) {
      const touch = Array.from(e.changedTouches).find(t => t.identifier === activeTouchId.current);
      if (!touch) return;
      e.preventDefault();

      setJoystick(prev => {
        if (!prev) return prev;

        const dx = touch.clientX - prev.baseX;
        const dy = touch.clientY - prev.baseY;
        const dist = Math.sqrt(dx * dx + dy * dy);
        const scale = dist > RADIUS ? RADIUS / dist : 1;
        const cdx = dx * scale;
        const cdy = dy * scale;

        // X → steer: drag right = steer right (negative in car convention)
        const steer = clamp(-cdx / RADIUS, -1, 1);
        // Y → throttle (drag up) / brake (drag down)
        const throttle = cdy < 0 ? clamp(-cdy / RADIUS, 0, 1) : 0;
        const brake = cdy > RADIUS * 0.3;

        useGameStore.getState().setInput({ steer, throttle, brake });

        return { ...prev, knobX: prev.baseX + cdx, knobY: prev.baseY + cdy };
      });
    }

    function onTouchEnd(e: TouchEvent) {
      const touch = Array.from(e.changedTouches).find(t => t.identifier === activeTouchId.current);
      if (!touch) return;

      activeTouchId.current = null;
      useGameStore.getState().setActiveInputDevice('keyboard');
      useGameStore.getState().setInput({ steer: 0, throttle: 0, brake: false });
      setJoystick(null);
    }

    window.addEventListener('touchstart', onTouchStart, { passive: true });
    window.addEventListener('touchmove', onTouchMove, { passive: false });
    window.addEventListener('touchend', onTouchEnd);
    window.addEventListener('touchcancel', onTouchEnd);
    return () => {
      window.removeEventListener('touchstart', onTouchStart);
      window.removeEventListener('touchmove', onTouchMove);
      window.removeEventListener('touchend', onTouchEnd);
      window.removeEventListener('touchcancel', onTouchEnd);
    };
  }, []);

  if (!joystick) return null;

  const knobSize = RADIUS * 0.55;

  return (
    <div className="fixed inset-0 pointer-events-none z-50">
      {/* Base ring */}
      <div
        className="absolute rounded-full border-2 border-white/30 bg-white/10"
        style={{
          width: RADIUS * 2,
          height: RADIUS * 2,
          left: joystick.baseX - RADIUS,
          top: joystick.baseY - RADIUS,
        }}
      />
      {/* Knob */}
      <div
        className="absolute rounded-full bg-white/50"
        style={{
          width: knobSize,
          height: knobSize,
          left: joystick.knobX - knobSize / 2,
          top: joystick.knobY - knobSize / 2,
        }}
      />
    </div>
  );
}
