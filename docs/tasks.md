# Kanban Tasks — Claimable by Anyone

> **Updated:** Feb 22, 2026
> These tasks are **not group-specific**. Any contributor can claim one.
> Copy into ProjectMap kanban as needed.

---

## Priority Tier 1 — High Value, Low Coordination

### T01: API Health Indicator in Dashboard

**Description:** Add a small status badge to the dashboard header that pings the API `/health` endpoint and shows connected/disconnected state. Helps the whole team see at a glance if the backend is reachable.

**Acceptance Criteria:**
- Badge visible in dashboard header (green = connected, red = disconnected)
- Polls `/health` on page load and every 30s
- Gracefully handles API being unconfigured (`NEXT_PUBLIC_API_URL` not set)

**Skills:** React, fetch API
**Files:** `simulator/src/app/dashboard/page.tsx`

---

### T02: Last Sync Status Indicator in Simulator

**Description:** Show a small HUD chip or status line during driving that indicates: how many runs are queued locally (not yet uploaded), and when the last successful API sync happened. Students need to know their data is reaching the shared server.

**Acceptance Criteria:**
- Small status chip visible during driving (e.g., bottom-right or near minimap)
- Shows "N runs queued" count from IndexedDB
- Shows "Last sync: 2 min ago" or "Offline" if API unreachable
- Does not block or slow down driving

**Skills:** React, IndexedDB, fetch API
**Files:** New `simulator/src/components/hud/SyncStatus.tsx`, update `simulator/src/app/page.tsx`

---

### T03: Cloud Models Tab — Loading, Empty, and Error States

**Status:** IN PROGRESS — claimed by Jesse
**Description:** The Cloud Models dashboard tab needs better UX for edge cases: API loading spinner, empty state when no models or jobs exist, and clear error message when the API is down.

**Acceptance Criteria:**
- Loading: spinner or skeleton while fetching
- Empty: friendly message with call-to-action ("Start a training job to see models here")
- Error: red banner with error detail and retry button
- All three states visually polished, consistent with existing dashboard style

**Skills:** React, Tailwind CSS
**Files:** `simulator/src/app/dashboard/page.tsx` (CloudTab component)

---

### T04: Training Run Quality Checklist

**Description:** Write a document defining what makes a "good" training run vs an unusable one. Include examples like: stuck in place, constant off-track, low-speed wobbling, running for 20+ minutes unattended. This helps students self-evaluate and helps with data curation.

**Acceptance Criteria:**
- New doc: `docs/training-run-quality.md`
- Covers: good runs, marginal runs, bad runs with specific criteria
- Includes at least 3 concrete examples with expected frame counts / durations
- Linked from README.md under Project Docs

**Skills:** Writing, simulator experience
**Files:** New `docs/training-run-quality.md`, update `README.md`

---

### T05: New Contributor Onboarding Guide

**Description:** Write a step-by-step guide for someone joining the project for the first time. Cover: cloning the repo, installing deps, running the simulator locally, doing a test drive, verifying data capture, and where to find tasks.

**Acceptance Criteria:**
- New doc: `docs/contributor-onboarding.md`
- Covers: prerequisites, clone, install, run, test drive, find tasks
- Tested by at least one person who hasn't set up the project before
- Linked from README.md

**Skills:** Writing, following instructions
**Files:** New `docs/contributor-onboarding.md`, update `README.md`

---

## Priority Tier 2 — Solid Contributions

### T06: Document Simulator Data Collection Workflow

**Description:** Write a short guide explaining the full data flow: how to drive runs, where data is stored (localStorage + IndexedDB), how cloud sync works when API is configured, how to verify an upload succeeded, and how to export runs as zip files.

**Acceptance Criteria:**
- New doc: `docs/data-collection-workflow.md`
- Covers local storage, IndexedDB frame store, cloud sync, zip export
- Includes screenshots or diagrams
- Linked from README.md

**Skills:** Writing, simulator experience
**Files:** New `docs/data-collection-workflow.md`, update `README.md`

---

### T07: "How to Start a Training Job" Guide

**Description:** One-page instructions for students or instructors to trigger model training. Cover: navigate to Cloud Models tab, click "Start Training Job", monitor status, verify model appears, set model active.

**Acceptance Criteria:**
- New doc: `docs/how-to-train.md`
- Step-by-step with screenshots
- Includes expected outcomes (model version appears, status transitions)
- Linked from README.md

**Skills:** Writing, API/dashboard experience
**Files:** New `docs/how-to-train.md`, update `README.md`

---

### T08: Keyboard Shortcuts Help Overlay

**Description:** Add a help modal or overlay that shows all keyboard shortcuts: driving controls, throttle presets (1-5), brake (Space), pause (Esc), AI toggles. Triggered by pressing `?` or clicking a help icon.

**Acceptance Criteria:**
- Overlay appears on `?` keypress or help button click
- Lists all keyboard shortcuts grouped by category
- Dismissible with Esc or clicking outside
- Styled consistently with existing HUD

**Skills:** React, keyboard events
**Files:** New `simulator/src/components/hud/KeyboardHelp.tsx`, update `KeyboardHandler.tsx` and `page.tsx`

---

### T09: Run Notes Field in UI

**Description:** Add an optional text note field that can be attached to a run. Show it on the RunComplete screen and in the dashboard RunsTable. Include it in exported metadata and API uploads.

**Acceptance Criteria:**
- Text input on RunComplete screen (optional, can be skipped)
- Note saved in localStorage run metadata and included in API upload
- Note visible in RunsTable as a tooltip or expandable cell
- Note included in exported JSON/zip

**Skills:** React, state management
**Files:** `RunComplete.tsx`, `training-data.ts`, `RunsTable.tsx`, `api-client.ts`

---

### T10: Model/Job Table Sorting and Filtering in Dashboard

**Description:** Add sort (by date, status, version) and filter (by status) controls to the Models and Training Jobs tables in the Cloud Models dashboard tab.

**Acceptance Criteria:**
- Clickable column headers to sort models and jobs
- Status filter dropdown (all, ready, training, failed)
- Sort/filter state persists during tab session
- Works with empty data gracefully

**Skills:** React, array manipulation
**Files:** `simulator/src/app/dashboard/page.tsx` (CloudTab component)

---

### T11: "Copy Model Version" Button

**Description:** Small UX improvement — add a copy-to-clipboard button next to model version strings in the AI Model Panel and Cloud Models dashboard tab. Useful when sharing versions with teammates.

**Acceptance Criteria:**
- Clipboard icon button next to model version text
- Copies version string on click
- Brief visual feedback (checkmark or "Copied!" tooltip)
- Works in both AI panel and dashboard

**Skills:** React, Clipboard API
**Files:** `AiModelPanel.tsx`, `dashboard/page.tsx`

---

### T12: API Edge Case Tests

**Description:** Add pytest tests for API edge cases: finalize a run without uploading artifacts, request an invalid model version, upload to a non-existent run ID, list runs with bad query params.

**Acceptance Criteria:**
- New test file or additions to existing tests in `services/api/tests/`
- Covers at least 5 edge cases
- All tests pass
- Documents expected error responses

**Skills:** Python, pytest, FastAPI
**Files:** `services/api/tests/`

---

### T13: Simulator API Client Error Handling Tests

**Description:** Add Vitest (or Jest) tests for the simulator's API client. Mock API failures (network error, 500, timeout) and verify the fallback behavior (queues locally, shows error state, doesn't crash).

**Acceptance Criteria:**
- New test file: `simulator/src/lib/api/__tests__/api-client.test.ts`
- Mocks fetch with various failure modes
- Verifies graceful degradation
- At least 5 test cases

**Skills:** TypeScript, Vitest/Jest, mocking
**Files:** `simulator/src/lib/api/`

---

## Priority Tier 3 — Polish and Documentation

### T14: UI Copy Polish Pass

**Status:** IN PROGRESS — claimed by Jesse
**Description:** Review all simulator and dashboard text — labels, tooltips, status messages, button text — for clarity, consistency, and typos. Fix anything confusing or inconsistent.

**Acceptance Criteria:**
- PR with text-only changes (no logic changes)
- Consistent capitalization and terminology
- All tooltips/titles are helpful and accurate
- No placeholder or developer-facing text visible to students

**Skills:** Attention to detail, English
**Files:** Various `.tsx` files across `simulator/src/`

---

### T15: Capture Screenshots and GIFs for Docs

**Description:** Take screenshots and short GIF recordings of: simulator driving view, AI camera PIP, AI model panel, dashboard overview, Cloud Models tab, training job flow. Store in `docs/assets/` and reference from docs.

**Acceptance Criteria:**
- At least 6 screenshots/GIFs covering main features
- Stored in `docs/assets/` (new directory)
- Referenced from relevant docs (README, welcome guide, onboarding)
- Reasonable file sizes (compress GIFs)

**Skills:** Screen recording, image editing
**Files:** New `docs/assets/`, update various `.md` files

---

### T16: GitHub Issue and PR Templates

**Description:** Create standard issue templates (bug report, feature request) and a PR template with a checklist (description, testing, screenshots).

**Acceptance Criteria:**
- `.github/ISSUE_TEMPLATE/bug_report.md`
- `.github/ISSUE_TEMPLATE/feature_request.md`
- `.github/PULL_REQUEST_TEMPLATE.md`
- Templates are helpful and not overly bureaucratic

**Skills:** GitHub, markdown
**Files:** New `.github/` directory and template files

---

### T17: Known Issues Doc

**Description:** Create a living document tracking current known gaps, limitations, and workarounds. Examples: hardware adapter pending, obstacle sensing not implemented, sync requires manual API URL config.

**Acceptance Criteria:**
- New doc: `docs/known-issues.md`
- At least 5 known issues documented with status and workaround
- Linked from README.md
- Updated as issues are resolved

**Skills:** Writing, project awareness
**Files:** New `docs/known-issues.md`, update `README.md`

---

### T18: Seeded Demo Dataset Script Documentation

**Description:** Document how to generate or test a small known-good training run for development and testing. Cover: running the simulator headlessly or manually, verifying frames are captured, uploading to API, and triggering a training job with the test data.

**Acceptance Criteria:**
- Runbook in `docs/testing-with-demo-data.md` or `services/trainer/README.md`
- Step-by-step commands and expected outputs
- Can be followed by someone unfamiliar with the project

**Skills:** Writing, simulator + API experience
**Files:** New doc or update existing README

---

## Quick Reference

| ID | Title | Priority | Type | Est. Effort |
|----|-------|----------|------|-------------|
| T01 | API Health Indicator | Tier 1 | Code | Small |
| T02 | Last Sync Status Indicator | Tier 1 | Code | Small |
| T03 | Cloud Tab Loading/Error States | Tier 1 | Code | Small |
| T04 | Training Run Quality Checklist | Tier 1 | Doc | Small |
| T05 | Contributor Onboarding Guide | Tier 1 | Doc | Medium |
| T06 | Data Collection Workflow Doc | Tier 2 | Doc | Medium |
| T07 | How to Train Guide | Tier 2 | Doc | Medium |
| T08 | Keyboard Shortcuts Overlay | Tier 2 | Code | Small |
| T09 | Run Notes Field | Tier 2 | Code | Medium |
| T10 | Model/Job Sorting & Filtering | Tier 2 | Code | Medium |
| T11 | Copy Model Version Button | Tier 2 | Code | Tiny |
| T12 | API Edge Case Tests | Tier 2 | Code | Medium |
| T13 | Simulator API Client Tests | Tier 2 | Code | Medium |
| T14 | UI Copy Polish Pass | Tier 3 | Code | Small |
| T15 | Screenshots & GIFs for Docs | Tier 3 | Media | Medium |
| T16 | GitHub Issue/PR Templates | Tier 3 | Config | Small |
| T17 | Known Issues Doc | Tier 3 | Doc | Small |
| T18 | Demo Dataset Script Docs | Tier 3 | Doc | Medium |
