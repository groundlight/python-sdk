#!/bin/bash
# convient script to run the docs server. It automatically rebuilds and restarts when you change code. You just need to refresh your browser. 

check_dependencies() {
  if ! command -v fswatch &> /dev/null
  then
      # if homebrew is installed, install fswatch
      if command -v brew &> /dev/null
      then
          echo "Installing fswatch..."
          brew install fswatch
          # check that fswatch is installed
          if ! command -v fswatch &> /dev/null
          then
              echo "ERROR: fswatch failed to install.  Please install it manually."
              exit 1
          fi
      else
          echo "ERROR: fswatch is not installed. Please install it using your package manager or homebrew."
          exit 1
      fi
  fi
}

check_dependencies

cd "$(dirname "$0")"/..
# Only watch the python files, because the npm server will live reload the markdown docs.
WATCH_PATH="./src/"
START_SERVER_CMD="make develop-docs-comprehensive"
while true; do
  $START_SERVER_CMD &
  
  echo "Server started"

  echo "Waiting for 15 seconds before starting to watch for file changes..."
  sleep 15
  
  CHANGED_FILE=$(fswatch -1 --exclude 'docs/static/api-reference-docs' --exclude 'build/' --exclude '/docs/.docusaurus' --exclude 'docs/node_modules/.cache/webpack' --exclude '.git/'  $WATCH_PATH)
  echo "Detected changes in: $CHANGED_FILE"
  
echo "Code changed. Attempting to kill server on port 3000..."

# Send SIGTERM to the process listening on port 3000
lsof -ti:3000 | xargs kill

# Wait for a bit to give the process a chance to shut down gracefully
sleep 5

# Check if any process is still listening on port 3000
if lsof -ti:3000 > /dev/null; then
    echo "Process didn't shut down gracefully. Force killing..."
    lsof -ti:3000 | xargs kill -9
    sleep 2
    
    # Final check
    if lsof -ti:3000 > /dev/null; then
        echo "ERROR: Unable to kill the process running on port 3000. Exiting..."
        exit 1
    fi
fi

  
  # Additional sleep to ensure port is released before restarting the server.
  echo "Waiting for an additional 5 seconds before restarting server..."
  sleep 5

done
