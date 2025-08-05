# Use Node.js 18
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy all source code first
COPY . .

# Set CI environment to avoid interactive prompts
ENV CI=true
ENV NODE_ENV=production

# Install dependencies
RUN npm install
RUN cd server && npm install
RUN cd client && npm install

# Build the client using build script
RUN cd client && chmod +x build.sh && ./build.sh

# Expose port
EXPOSE 5000

# Set environment
ENV NODE_ENV=production
ENV PORT=5000

# Start the application
CMD ["npm", "run", "railway-start"] 