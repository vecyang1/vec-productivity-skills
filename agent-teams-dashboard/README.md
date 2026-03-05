<img width="1526" height="1049" alt="image" src="https://github.com/user-attachments/assets/6b262edf-ce14-4916-a577-8101e90c6852" />


# Agent Teams Dashboard

Inspired by https://x.com/alterxyz4/status/2021892207574405386.
Real-time web dashboard for monitoring [Claude Code](https://docs.anthropic.com/en/docs/claude-code) Agent Teams.

![Node.js](https://img.shields.io/badge/Node.js-18+-green) ![License](https://img.shields.io/badge/license-MIT-blue)

## What it does

Watches `~/.claude/teams/` and `~/.claude/tasks/` directories and displays live updates via WebSocket:

- Team overview with member status and activity indicators
- Task board with progress tracking (pending / in-progress / completed)
- Inbox message viewer with protocol message parsing
- Member filtering — click a member to filter their messages and tasks
- Dark/light theme toggle
- Auto-reconnecting WebSocket for real-time file change detection

## Quick Start

```bash
# Clone and install
git clone <your-repo-url>
cd agent-teams-dashboard
npm install

# Start (opens browser automatically)
./start.sh

# Or manually
npm start
# → http://localhost:4747
```

## Configuration

| Env Variable | Default | Description |
|---|---|---|
| `PORT` | `4747` | Server port (HTTP + WebSocket) |

Port 4747 was chosen to avoid conflicts with common dev servers (3000, 5173, 8080).

## Architecture

```
├── backend/
│   ├── server.js      # Express + WebSocket + chokidar file watcher
│   └── config.js      # Port and directory configuration
├── public/
│   └── index.html     # Single-file frontend (vanilla JS, no build step)
├── start.sh           # Launcher script
└── package.json
```

Single-file frontend with zero build tooling. Backend uses Express for REST API, `ws` for WebSocket, and `chokidar` for file system watching.

## API Endpoints

| Method | Path | Description |
|---|---|---|
| GET | `/api/teams` | List all teams with activity status |
| GET | `/api/teams/:name` | Full team config |
| GET | `/api/teams/:name/inboxes` | Inbox messages for a team |
| GET | `/api/tasks/:teamName` | Tasks for a team |
| GET | `/api/overview` | Aggregated overview of all teams |

## Requirements

- Node.js 18+
- Active Claude Code Agent Teams (files in `~/.claude/teams/` and `~/.claude/tasks/`)

## License

MIT
