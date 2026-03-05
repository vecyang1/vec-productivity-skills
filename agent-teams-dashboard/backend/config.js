const path = require('path');
const HOME = process.env.HOME || process.env.USERPROFILE;

module.exports = {
  port: process.env.PORT || 4747,
  teamsDir: path.join(HOME, '.claude', 'teams'),
  tasksDir: path.join(HOME, '.claude', 'tasks'),
  refreshInterval: 2000
};
