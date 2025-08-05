#!/usr/bin/env node

const { spawn, execSync } = require('child_process');
const path = require('path');
const fs = require('fs');

console.log('🚀 Starting Threads Bot Dashboard for Railway...');

// Build the client first
console.log('📦 Building React client...');
try {
  execSync('npm run build:client', { 
    cwd: __dirname, 
    stdio: 'inherit' 
  });
  console.log('✅ Client built successfully');
} catch (error) {
  console.error('❌ Failed to build client:', error);
  process.exit(1);
}

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