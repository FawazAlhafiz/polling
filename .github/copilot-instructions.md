# Polling App - AI Coding Agent Instructions

A Frappe Framework app for creating and managing polls with Vue.js frontend. This guide helps AI agents contribute effectively to the polling application.

## Architecture Overview

### Full-Stack Structure
- **Backend**: Frappe Framework (Python) - DocTypes define data models and business logic
- **Frontend**: Vue 3 (Composition API) + Frappe UI + Tailwind CSS
- **Build**: Vite handles frontend development; Frappe manages backend asset serving
- **Authentication**: Built-in Frappe user system with CSRF tokens

### Key DocTypes (Backend Data Models)
- `Poll`: Main entity with title, description, start_date, end_date, status
- `PollOption`: Child table on Poll; each option has option_text, description
- `PollVote`: Tracks user votes (draft state initially, then submitted)
- `PollResult`: Computed results showing vote counts per option
- `PollTarget` & `PollResultOption`: Supporting structures for targeting and results

## Core Workflows

### Frontend Development
```bash
cd apps/polling/frontend
yarn dev           # Runs Vite dev server on port 8080 with Frappe proxy
yarn build         # Builds and outputs to ../polling/public/frontend
npm run copy-html-entry  # Copies index.html to www/frontend.html for Frappe routing
```

### Backend Development
```bash
bench start        # Starts Frappe server (port 8000) + other services
bench set-config developer_mode 1  # Enables dev mode for Python reloading
```

**Key Pattern**: Frontend at `/frontend` base path; proxies to Frappe backend. Production builds output to `polling/public/frontend/`.

## Frontend Patterns

### Data Fetching with Frappe UI Resources
Use `createResource` from frappe-ui for API calls. Examples in `frontend/src/pages/Polls.vue`:

```javascript
const pollsResource = createResource({
    url: 'frappe.client.get_list',
    params: { doctype: 'Poll', fields: ['name', 'title', 'description', 'start_date', 'end_date', 'status'], auto: true }
});
const pollsList = computed(() => pollsResource.list.data || []);
```

**Key**: Resources handle loading/error states; always provide fallback UI for loading, empty, and error states.

### State Management
Use Vue Composition API + `reactive()` for session state (see `src/data/session.js`). No Pinia store—keep logic localized to components.

### Styling Convention
- Use Tailwind CSS utility classes for component styling
- Leverage Frappe UI preset theme (colors, spacing) configured in `tailwind.config.js`
- Example: `class="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"`

### Authentication
Router guards in `router.js` check `userResource` promise before allowing navigation. Login redirects on auth failure. Session state stored in `src/data/session.js`.

## Backend Patterns

### DocType Structure
- All doctypes in `polling/polling/doctype/{doctype_name}/`
- Includes `.json` schema, `.py` class, `.js` (optional), `.html` (form layout)
- Minimal classes shown; most validation happens in hooks or frontend

### Validation Example (Poll.py)
```python
def validate(self):
    if self.title and not re.match(r'^[\w\- ]+$', self.title):
        throw(_("Title cannot contain special characters..."))
```

### API Endpoints
Frappe auto-exposes CRUD via `frappe.client.*` (get, get_list, insert, submit). Custom endpoints use `@frappe.whitelist()` decorator in `.py` files.

### Post-Install Setup
`polling/install.py` runs `after_install` hook to configure roles via `setup_roles.py`. Modify this for future initialization needs.

## Routing & URL Patterns

### Frontend Routes (Vue Router)
- `/` → redirects to `/polls`
- `/polls` → main Polls.vue listing
- `/polls/:id/results` → PollResults.vue with props
- `/account/login` → Login.vue

**Pattern**: Base path is `/frontend`; Frappe serves frontend HTML at `polling/www/frontend.html`.

### Website Route Rule
In `hooks.py`: `website_route_rules = [{'from_route': '/frontend/<path:app_path>', 'to_route': 'frontend'}]` maps all `/frontend/*` to Vue app.

## Common Development Tasks

### Adding a New Field to Poll
1. Edit `polling/doctype/poll/poll.json` (add field definition)
2. Create Python migration in `polling/patches/` if needed
3. Update Vue component to fetch/display new field
4. Test: `bench install-app polling` or use dev mode

### Adding a New API Endpoint
1. Create method in doctype `.py` file with `@frappe.whitelist()` decorator
2. Call via `createResource({ url: 'method_path' })` from frontend
3. Handle loading/error states in component

### Frontend Component Addition
Create `.vue` file in `frontend/src/pages/` or `components/`. Import in router or parent component. Use existing Polls.vue as template for Frappe UI integration.

## Build & Deployment

### Development Build
```bash
cd frontend && yarn dev
```
Vite watches files; changes reflect instantly (frontend assets only; Python changes require bench restart).

### Production Build
```bash
cd frontend && yarn build
# Auto-runs copy-html-entry script; outputs to polling/public/frontend/
bench restart  # Restart to serve compiled assets
```

**Key**: Vite base path is `/assets/polling/frontend/` for production asset URLs.

## Key Dependencies & Versions
- **Backend**: Frappe 15 (implicit; no version in pyproject.toml)
- **Frontend**: Vue 3.5+, frappe-ui 0.1.149+, Tailwind 3.4+, Vite 5.4+
- **Python**: 3.10+ (pyproject.toml requirement)

## Configuration Files
- `frontend/vite.config.js`: Frappe proxy, build paths, indexHtmlPath points to `polling/www/frontend.html`
- `frontend/tailwind.config.js`: Uses Frappe UI preset
- `polling/hooks.py`: App metadata, website routes, install hooks
- `pyproject.toml`: Ruff linting rules (110 char line length, specific ignore patterns)

## Common Pitfalls & Solutions

| Problem | Solution |
|---------|----------|
| Frontend changes not visible | Clear browser cache; vite should auto-rebuild. Check `vite.config.js` watch config. |
| Poll data not loading | Check network tab; verify Frappe backend running on 8000. CSRF token injected in `frontend.html`. |
| Build fails on `copy-html-entry` | Ensure `yarn build` completes first; `frontend.html` path in vite.config.js must exist. |
| Python import errors | Run `bench install-app polling` after adding new modules. |

## Testing Approach
No existing test suite visible. For new features: create manual test cases in development mode. Backend validation tested via Python scripts; frontend via component interaction testing in browser.
