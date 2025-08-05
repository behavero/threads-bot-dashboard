#!/usr/bin/env node

const { execSync } = require('child_process');
const path = require('path');

console.log('🔨 Building Threads Bot Dashboard for Railway...');

try {
  // Install root dependencies
  console.log('📦 Installing root dependencies...');
  execSync('npm install', { cwd: __dirname, stdio: 'inherit' });
  
  // Install server dependencies
  console.log('📦 Installing server dependencies...');
  execSync('npm install', { cwd: path.join(__dirname, 'server'), stdio: 'inherit' });
  
  // Install client dependencies
  console.log('📦 Installing client dependencies...');
  execSync('npm install', { cwd: path.join(__dirname, 'client'), stdio: 'inherit' });
  
  // Build client
  console.log('📦 Building React client...');
  execSync('npm run build', { cwd: path.join(__dirname, 'client'), stdio: 'inherit' });
  
  console.log('✅ Build completed successfully!');
} catch (error) {
  console.error('❌ Build failed:', error);
  process.exit(1);
} 