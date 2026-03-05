const express = require('express');
const http = require('http');
const { WebSocketServer } = require('ws');
const cors = require('cors');
const chokidar = require('chokidar');
const fs = require('fs');
const path = require('path');
const config = require('./config');

const app = express();
app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '..', 'public')));

// --- Helpers ---

function readJsonSafe(filePath) {
  try {
    return JSON.parse(fs.readFileSync(filePath, 'utf-8'));
  } catch {
    return null;
  }
}

function getFileMtime(filePath) {
  try {
    return fs.statSync(filePath).mtimeMs;
  } catch {
    return 0;
  }
}

// Returns the most recent mtime across all JSON files in a directory (recursive up to depth 2)
function getLatestMtime(dirPath) {
  let latest = 0;
  try {
    const entries = fs.readdirSync(dirPath, { withFileTypes: true });
    for (const entry of entries) {
      const full = path.join(dirPath, entry.name);
      if (entry.isFile() && entry.name.endsWith('.json')) {
        const mt = getFileMtime(full);
        if (mt > latest) latest = mt;
      } else if (entry.isDirectory()) {
        // one level deeper (e.g. inboxes/)
        try {
          const sub = fs.readdirSync(full).filter(f => f.endsWith('.json'));
          for (const sf of sub) {
            const mt = getFileMtime(path.join(full, sf));
            if (mt > latest) latest = mt;
          }
        } catch {}
      }
    }
  } catch {}
  return latest;
}

function getTeamActivity(teamName) {
  const teamDir = path.join(config.teamsDir, teamName);
  const taskDir = path.join(config.tasksDir, teamName);
  const teamMtime = getLatestMtime(teamDir);
  const taskMtime = getLatestMtime(taskDir);
  const lastActivity = Math.max(teamMtime, taskMtime);

  const now = Date.now();
  const ageMs = now - lastActivity;
  const ageHours = ageMs / (1000 * 60 * 60);

  let status;
  if (ageHours < 1) status = 'active';
  else if (ageHours < 24) status = 'recent';
  else status = 'stale';

  return { lastActivity, lastActivityISO: lastActivity ? new Date(lastActivity).toISOString() : null, ageHours: Math.round(ageHours * 10) / 10, status };
}

function getTeamNames() {
  try {
    return fs.readdirSync(config.teamsDir, { withFileTypes: true })
      .filter(d => d.isDirectory())
      .map(d => d.name);
  } catch {
    return [];
  }
}

function getTeamConfig(teamName) {
  return readJsonSafe(path.join(config.teamsDir, teamName, 'config.json'));
}

function getTeamInboxes(teamName) {
  const inboxDir = path.join(config.teamsDir, teamName, 'inboxes');
  try {
    const files = fs.readdirSync(inboxDir).filter(f => f.endsWith('.json'));
    const inboxes = {};
    for (const file of files) {
      const agentName = path.basename(file, '.json');
      const messages = readJsonSafe(path.join(inboxDir, file));
      if (messages) inboxes[agentName] = messages;
    }
    return inboxes;
  } catch {
    return {};
  }
}

function getTeamTasks(teamName) {
  const taskDir = path.join(config.tasksDir, teamName);
  try {
    const files = fs.readdirSync(taskDir).filter(f => f.endsWith('.json'));
    const tasks = [];
    for (const file of files) {
      const task = readJsonSafe(path.join(taskDir, file));
      if (task && task.id) tasks.push(task);
    }
    tasks.sort((a, b) => Number(a.id) - Number(b.id));
    return tasks;
  } catch {
    return [];
  }
}

// --- REST API ---

// GET /api/teams - list all teams with summary info
app.get('/api/teams', (req, res) => {
  const teams = getTeamNames().map(name => {
    const cfg = getTeamConfig(name);
    const activity = getTeamActivity(name);
    return {
      name,
      description: cfg?.description || '',
      createdAt: cfg?.createdAt || null,
      memberCount: cfg?.members?.length || 0,
      members: (cfg?.members || []).map(m => ({
        name: m.name,
        agentType: m.agentType,
        model: m.model,
        color: m.color || null,
        joinedAt: m.joinedAt || null
      })),
      ...activity
    };
  });
  // Sort: active first, then recent, then stale; within same status sort by lastActivity desc
  const order = { active: 0, recent: 1, stale: 2 };
  teams.sort((a, b) => (order[a.status] - order[b.status]) || (b.lastActivity - a.lastActivity));
  res.json(teams);
});

// GET /api/teams/:name - full team config
app.get('/api/teams/:name', (req, res) => {
  const cfg = getTeamConfig(req.params.name);
  if (!cfg) return res.status(404).json({ error: 'Team not found' });
  res.json(cfg);
});

// GET /api/teams/:name/inboxes - inbox messages for a team
app.get('/api/teams/:name/inboxes', (req, res) => {
  res.json(getTeamInboxes(req.params.name));
});

// GET /api/tasks/:teamName - tasks for a team
app.get('/api/tasks/:teamName', (req, res) => {
  res.json(getTeamTasks(req.params.teamName));
});

// GET /api/overview - aggregated overview of all teams
app.get('/api/overview', (req, res) => {
  const overview = getTeamNames().map(name => {
    const cfg = getTeamConfig(name);
    const tasks = getTeamTasks(name);
    const inboxes = getTeamInboxes(name);
    const totalMessages = Object.values(inboxes).reduce((s, msgs) => s + msgs.length, 0);
    const unreadMessages = Object.values(inboxes).reduce(
      (s, msgs) => s + msgs.filter(m => !m.read).length, 0
    );
    return {
      name,
      description: cfg?.description || '',
      memberCount: cfg?.members?.length || 0,
      taskCount: tasks.length,
      completedTasks: tasks.filter(t => t.status === 'completed').length,
      inProgressTasks: tasks.filter(t => t.status === 'in_progress').length,
      pendingTasks: tasks.filter(t => t.status === 'pending').length,
      totalMessages,
      unreadMessages
    };
  });
  res.json(overview);
});

// --- HTTP + WebSocket on same port ---

const server = http.createServer(app);
const wss = new WebSocketServer({ server });

const clients = new Set();

wss.on('connection', (ws) => {
  clients.add(ws);
  ws.send(JSON.stringify({ type: 'connected', timestamp: Date.now() }));
  ws.on('close', () => clients.delete(ws));
  ws.on('error', () => clients.delete(ws));
});

function broadcast(data) {
  const msg = JSON.stringify(data);
  for (const ws of clients) {
    if (ws.readyState === 1) ws.send(msg);
  }
}

// --- File Watcher ---

function parseChange(filePath) {
  if (filePath.startsWith(config.teamsDir)) {
    return { area: 'teams', file: path.relative(config.teamsDir, filePath) };
  }
  return { area: 'tasks', file: path.relative(config.tasksDir, filePath) };
}

function startWatcher() {
  const watchPaths = [config.teamsDir, config.tasksDir].filter(p => {
    try { fs.accessSync(p); return true; } catch { return false; }
  });

  if (watchPaths.length === 0) {
    console.log('Warning: No watch directories found.');
    return null;
  }

  const watcher = chokidar.watch(watchPaths, {
    persistent: true,
    ignoreInitial: true,
    depth: 4,
    awaitWriteFinish: { stabilityThreshold: 300, pollInterval: 100 }
  });

  const handler = (event) => (filePath) => {
    const parsed = parseChange(filePath);
    const parts = parsed.file.split(path.sep);
    console.log(`[${event}] ${parsed.area}/${parsed.file}`);
    broadcast({
      type: 'file_changed',
      event,
      area: parsed.area,
      teamName: parts[0] || null,
      file: parsed.file,
      timestamp: Date.now()
    });
  };

  watcher.on('change', handler('change'));
  watcher.on('add', handler('add'));
  watcher.on('unlink', handler('remove'));
  watcher.on('error', (err) => console.error('Watcher error:', err.message));

  console.log('Watching:', watchPaths.join(', '));
  return watcher;
}

// --- Start ---

server.listen(config.port, () => {
  console.log(`Teams Dashboard: http://localhost:${config.port}`);
  console.log(`WebSocket:       ws://localhost:${config.port}`);
  startWatcher();
});
