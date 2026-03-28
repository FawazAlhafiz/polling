# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Frontend Development
```bash
cd frontend
yarn install         # Install dependencies
yarn dev             # Start Vite dev server
yarn build           # Build for production (outputs to polling/public/frontend/ and copies index.html to polling/www/frontend.html)
yarn lint            # Run Biome linter with auto-fix
```

### Backend Development
```bash
# From bench root (typically ~/frappe-bench or ~/fawaz)
bench start          # Start Frappe development server
bench install-app polling   # Install app on a site
bench set-config developer_mode 1  # Enable developer mode

# Build frontend assets via bench
bench build --app polling

# Apply schema changes and run migration patches
bench migrate
```

### Running Tests
```bash
# From bench root
bench run-tests --app polling
bench run-tests --app polling --doctype "Poll"
bench run-tests --app polling --doctype "Poll Vote"
```

### Triggering Scheduled Tasks Manually
```bash
# Always specify --site; bare "bench execute" will fail with NameError
bench --site <site-name> execute polling.tasks.send_expiry_notifications
```

### Code Quality
```bash
# Install pre-commit hooks (run once)
cd /path/to/polling
pre-commit install

# Run manually
pre-commit run --all-files
```

## Architecture

### Frappe App Structure
This is a **Frappe Framework** app. The Python package lives at `polling/` (the inner directory). Key entry points:
- `polling/hooks.py` — app configuration, event hooks, website route rules; `scheduler_events` registers the hourly notification task
- `polling/tasks.py` — scheduled task functions (`send_expiry_notifications`)
- `polling/install.py` — `after_install` hook that creates the "Polling User" role
- `polling/permissions.py` — custom `has_permission` handler for `Poll Vote` (owner-based access control)
- `polling/patches.txt` — database migration patches; new patches go under `[post_model_sync]`

### DocTypes (Backend Data Model)
- **Poll** — core document. Fields: `title`, `description`, `start_date` (Datetime), `end_date` (Datetime), `status` (Active/Ended/Upcoming), `options` (child table), `targer_audience` (child table), `notify_before_expiry` (Check), `notify_hours_before` (Int, default 24), `expiry_notification_sent` (Check, hidden). Named `Poll-{MM}-{####}`. `poll.py` validates title with regex and resets `expiry_notification_sent` when `end_date` changes. `poll.js` auto-corrects `end_date` to `23:59:59` in the Desk form.
- **Poll Option** — child table of Poll; tracks `option_text` and `vote_count` (incremented on vote submission).
- **Poll Vote** — submittable document (Draft → Submitted). `before_submit` enforces: poll must be Active, within datetime range (`get_datetime(end_date) >= now_datetime()`), user not already voted. `on_submit` increments the corresponding `Poll Option.vote_count`. Ownership-based access enforced in both `poll_vote.py` and `permissions.py`.
- **Poll Result** — virtual DocType (no database table). Overrides `load_from_db` to compute results from Poll + Poll Option data on-the-fly. Used by the frontend to fetch results.
- **Poll Target** — child table for target audience (currently unused in vote validation — `user_is_in_target_audience` always returns `True`). See Issue #9.

### Scheduled Tasks
- `polling/tasks.py` — `send_expiry_notifications()` runs hourly. For each opted-in poll (`notify_before_expiry=1`, `expiry_notification_sent=0`) whose notification window is open (`end_date - notify_hours_before <= now < end_date`): emails the poll owner and all system users who haven't voted yet. Sets `expiry_notification_sent=1` after sending. Requires an outgoing email account configured in Frappe (Tools → Email Account).
- When Issue #9 (target audience filtering) is implemented, `_notify_non_voters()` in `tasks.py` should be updated to scope recipients to `poll.target_audience` when that child table is non-empty.

### Frontend (Vue 3 SPA)
Located in `frontend/src/`. Built with Vite, served at `/frontend/` via Frappe's web route (`website_route_rules` in `hooks.py`).

- **`router.js`** — Vue Router with history mode at `/frontend`. Auth guard redirects unauthenticated users to `/account/login`.
- **`data/session.js`** — reactive session state using `frappe-ui`'s `createResource`. Reads `user_id` from cookies.
- **`pages/Polls.vue`** — main listing page. Uses `createListResource` (frappe-ui) to fetch Poll list. Poll status (Active/Upcoming/Ended) is computed client-side from `start_date`/`end_date` using `new Date()` (handles Datetime strings). Voting flow: fetches full Poll doc → inserts a `Poll Vote` draft → submits it.
- **`pages/PollResults.vue`** — fetches `Poll Result` virtual doctype via `frappe.client.get`, displays vote distribution with progress bars.

### Key Patterns
- All API calls go through `frappe-ui`'s `createResource` / `createListResource`, which wraps Frappe's REST API (`frappe.client.get`, `frappe.client.insert`, `frappe.client.submit`).
- The frontend linter is **Biome** (not ESLint) — `yarn lint` runs `biome check --write .`.
- Python formatting uses **ruff** with tab indentation (`indent-style = "tab"`), line length 110.
- The built frontend HTML entry point (`polling/www/frontend.html`) is git-ignored — it is regenerated by `yarn build` via the `copy-html-entry` script.
- `start_date` and `end_date` are `Datetime` fields stored in UTC. Frappe handles timezone display. `end_date` defaults to `23:59:59` via `poll.js` so polls are available all day on the expiry date.
