#!/usr/bin/env node

const { spawn } = require('child_process');
const path = require('path');

console.log('🚀 Starting Threads Bot Dashboard...');

// Start the server
const server = spawn('npm', ['run', 'server'], {
  cwd: path.join(__dirname, 'server'),
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'production' }
});

// Start the client (in production, this will serve the built files)
const client = spawn('npm', ['start'], {
  cwd: path.join(__dirname, 'client'),
  stdio: 'inherit',
  env: { ...process.env, NODE_ENV: 'production' }
});

// Handle process termination
process.on('SIGINT', () => {
  console.log('🛑 Shutting down...');
  server.kill();
  client.kill();
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('🛑 Shutting down...');
  server.kill();
  client.kill();
  process.exit(0);
});

// Handle child process errors
server.on('error', (error) => {
  console.error('❌ Server error:', error);
});

client.on('error', (error) => {
  console.error('❌ Client error:', error);
}); 