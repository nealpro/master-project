#!/bin/bash

# Function to perform git restore and status
perform_git_restore() {
    echo "Restoring all changes..."
    git restore '*'
    echo "Current git status:"
    git status
}

# Function to perform git fetch and pull
perform_git_fetch_and_pull() {
    echo "Fetching from remote..."
    git fetch
    echo "Waiting for a small delay..."
    sleep 2 # Small delay of 2 seconds
    echo "Pulling changes..."
    git pull
}

# Ask the user if they want to restore all changes
read -p "Do you want to restore all? (y/n): " answer_restore

case $answer_restore in
    [Yy]* ) perform_git_restore;;
    [Nn]* ) echo "Restore skipped.";;
    * ) echo "Please answer y or n.";;
esac

# Ask the user if they want to fetch and pull
read -p "Do you want to fetch and pull? (y/n): " answer_fetch_pull

case $answer_fetch_pull in
    [Yy]* ) perform_git_fetch_and_pull;;
    [Nn]* ) echo "Fetch and pull skipped.";;
    * ) echo "Please answer y or n.";;
esac
