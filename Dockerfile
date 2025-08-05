# Use Node.js 18
FROM node:18-alpine

# Set working directory
WORKDIR /app

# Copy all source code first
COPY . .

# Install dependencies
RUN npm install
RUN cd server && npm install
RUN cd client && npm install

# Build the client
RUN cd client && npm run build

# Expose port
EXPOSE 5000

# Set environment
ENV NODE_ENV=production
ENV PORT=5000

# Start the application
CMD ["npm", "run", "railway-start"] 