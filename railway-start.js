#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting Threads Bot Dashboard for Railway...');

// Start the server (client is already built)
console.log('🖥️ Starting Express server...');
const server = spawn('npm', ['start'], {
  cwd: path.join(__dirname, 'server'),
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'production' }
});

// Start the server
console.log('🖥️ Starting Express server...');
const server = spawn('npm', ['start'], {
  cwd: path.join(__dirname, 'server'),
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'production' }
});

// Handle process termination
process.on('SIGINT', () => {
  console.log('🛑 Shutting down...');
  server.kill();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('🛑 Shutting down...');
  server.kill();
  process.exit(0);
});

// Handle server errors
server.on('error', (error) => {
  console.error('❌ Server error:', error);
  process.exit(1);
});

server.on('exit', (code) => {
  console.log(`🛑 Server exited with code ${code}`);
  process.exit(code);
}); 