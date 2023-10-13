#!/bin/bash
# convient script to run the docs server. It automatically rebuilds and restarts when you change code. You just need to refresh your browser. 
WATCH_PATH="."
START_SERVER_CMD="make develop-docs-comprehensive"

while true; do
  $START_SERVER_CMD &
  SERVER_PID=$!
  
  echo "Server started with PID: $SERVER_PID"

  echo "Waiting for 15 seconds before starting to watch for file changes..."
  sleep 15
  
  if [[ "$OSTYPE" == "darwin"* ]]; then
    fswatch -1 --exclude 'docs/static/api-reference-docs' --exclude 'build/' --exclude '/docs/.docusaurus' --exclude 'changes.log' --exclude 'docs/node_modules/.cache/webpack' --exclude '.git/'  $WATCH_PATH | tee -a changes.log
  else
    echo "OS not supported"
    exit 1
  fi
  
  echo "Code changed. Attempting to kill server with PID: $SERVER_PID..."
  
  # Attempt to kill the npm process directly.
  pkill -f "npm"
  sleep 2
  
  if pgrep -f "npm" > /dev/null; then
    echo "WARNING: npm process is still running!"
     # If npm process is still running, try killing it harder
    pkill -9 -f "npm"
    sleep 2
    if pgrep -f "npm" > /dev/null; then
      echo "ERROR: Unable to kill the npm process. Exiting..."
      exit 1
    fi
  fi
  
  # Additional sleep to ensure port is released before restarting the server.
  echo "Waiting for an additional 5 seconds before restarting server..."
  sleep 5
  
  # Clear the log file to avoid reading old changes
  > changes.log

done
