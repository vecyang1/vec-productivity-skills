# Agent Teams Dashboard

Real-time web dashboard for monitoring Claude Code Agent Teams. Displays teams, members, inbox messages, and tasks with live updates.

## When to Use This Skill

Use this skill when you want to:
- Monitor active Agent Teams in real-time
- View inbox messages between agents
- Track task progress across teams
- Debug Agent Teams communication
- Visualize team structure and member activity
- Observe the file-based messaging system in action

## Quick Start

```bash
/teams-dashboard
```

This will:
1. Start the backend server on http://localhost:3000
2. Start the WebSocket server for real-time updates
3. Open your browser to the dashboard
4. Begin monitoring ~/.claude/teams/ and ~/.claude/tasks/

## What It Monitors

### Teams Directory (`~/.claude/teams/`)
- **config.json** - Team configuration, members, lead agent
- **inboxes/*.json** - Message queues for each agent
- File changes trigger real-time dashboard updates

### Tasks Directory (`~/.claude/tasks/`)
- **{task-id}.json** - Individual task files
- Task status, ownership, dependencies
- Real-time task progress tracking

## Dashboard Features

### Active Teams Section
- Lists all active teams
- Shows team members with colors and models
- Displays lead agent information
- Member count and join timestamps

### Tasks Section
- All tasks across all teams
- Status badges (pending/in_progress/completed)
- Task ownership and dependencies
- Sorted by task ID

### Inbox Messages Section
- Real-time message feed
- Distinguishes between:
  - **DM messages** - Regular agent-to-agent communication
  - **Protocol messages** - System messages (idle_notification, shutdown_request, etc.)
- Shows sender, recipient, timestamp
- Displays read status
- Color-coded by message type

### Real-Time Updates
- WebSocket connection for instant updates
- File watcher monitors both directories
- Visual indicator when updates are detected
- Auto-refresh every 5 seconds as backup

## Architecture

### Backend (`backend/server.js`)
- **Express server** - REST API on port 3000
- **WebSocket server** - Real-time updates on same port
- **Chokidar watcher** - Monitors file system changes
- **API endpoints**:
  - `GET /api/teams` - List all teams
  - `GET /api/teams/:name` - Get team config
  - `GET /api/teams/:name/inboxes` - Get inbox messages
  - `GET /api/tasks/:teamName` - Get team tasks
  - `GET /api/overview` - Aggregated stats

### Frontend (`public/index.html`)
- **Vanilla JS** - No framework dependencies
- **Lucide icons** - Professional SVG icons (no emojis)
- **Dark mode** - Modern, clean UI
- **Responsive design** - Works on all screen sizes
- **WebSocket client** - Real-time updates

### Configuration (`backend/config.js`)
- Port: 3000 (configurable via PORT env var)
- Teams directory: `~/.claude/teams`
- Tasks directory: `~/.claude/tasks`
- Refresh interval: 2000ms

## Manual Usage

### Start the server manually:
```bash
cd ~/.gemini/antigravity/skills/teams-dashboard
npm start
```

### Stop the server:
```bash
# Press Ctrl+C in the terminal
# Or kill the process:
lsof -ti:3000 | xargs kill -9
```

### Access the dashboard:
```
http://localhost:3000
```

## Use Cases

### 1. Monitor Active Teams
Watch your Agent Teams work in real-time. See when agents send messages, complete tasks, and go idle.

### 2. Debug Communication Issues
Inspect the inbox messages to understand:
- Message delivery timing
- Protocol message flow (idle_notification, shutdown_request, etc.)
- Message read status
- Agent-to-agent communication patterns

### 3. Track Task Progress
Monitor task status across all teams:
- Which tasks are blocked
- Who owns which tasks
- Task completion rate
- Dependency chains

### 4. Understand the File-Based System
See firsthand how Claude Code's Agent Teams use JSON files for communication:
- Watch inbox files update in real-time
- Observe task file changes
- Understand the message queue pattern

### 5. Meta-Monitoring
Use this dashboard to monitor the very team that built it! Create a team, watch them work, and see their messages appear in the dashboard.

## Technical Details

### Message Types

**DM (Direct Message)**
```json
{
  "from": "agent-name",
  "text": "Plain text message",
  "summary": "Brief summary",
  "timestamp": "2026-02-14T12:30:00.000Z",
  "color": "blue",
  "read": true
}
```

**Protocol Message**
```json
{
  "from": "agent-name",
  "text": "{\"type\":\"idle_notification\",\"from\":\"agent-name\",\"idleReason\":\"available\"}",
  "timestamp": "2026-02-14T12:30:00.000Z",
  "color": "blue",
  "read": true
}
```

### Task Structure
```json
{
  "id": "1",
  "subject": "Task title",
  "description": "Detailed description",
  "status": "in_progress",
  "owner": "agent-name",
  "blocks": [],
  "blockedBy": []
}
```

### Team Config
```json
{
  "name": "team-name",
  "description": "Team description",
  "leadAgentId": "team-lead@team-name",
  "members": [
    {
      "name": "agent-name",
      "agentType": "general-purpose",
      "model": "claude-sonnet-4-5",
      "color": "blue",
      "backendType": "in-process"
    }
  ]
}
```

## Troubleshooting

### Port already in use
```bash
# Kill existing process on port 3000
lsof -ti:3000 | xargs kill -9
```

### No teams showing up
- Check if `~/.claude/teams/` directory exists
- Verify you have active Agent Teams running
- Check browser console for API errors

### WebSocket not connecting
- Ensure server is running on port 3000
- Check firewall settings
- Look for WebSocket errors in browser console

### Dashboard not updating
- Check if file watcher is running (see server logs)
- Verify WebSocket connection status (top right indicator)
- Try manual refresh (F5)

## Dependencies

- **express** ^4.21.0 - Web server
- **ws** ^8.18.0 - WebSocket server
- **chokidar** ^4.0.0 - File system watcher
- **cors** ^2.8.5 - CORS middleware

## File Structure

```
teams-dashboard/
├── backend/
│   ├── server.js       # Main server with API and WebSocket
│   └── config.js       # Configuration
├── public/
│   └── index.html      # Dashboard UI
├── package.json        # Dependencies and scripts
├── start.sh           # Launcher script
└── SKILL.md           # This file
```

## Related Documentation

- [Claude Code Agent Teams](https://github.com/anthropics/claude-code/blob/main/docs/agent-teams.md)
- [Agent Teams Architecture](~/.claude/skills/claude-code-agent-teams/SKILL.md)
- [File-Based Communication](https://x.com/alterxyz4/status/1889999999999999999) - Jerome's analysis

## Credits

Built by an Agent Team to monitor Agent Teams (meta!). Demonstrates the file-based messaging system described in Jerome's reverse engineering analysis.

## Version

1.0.0 - Initial release (2026-02-14)
