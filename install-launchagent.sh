#!/bin/bash
# Install F1-Deck LaunchAgent for auto-start

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LAUNCHAGENT_DIR="$HOME/Library/LaunchAgents"
PLIST_SOURCE="$SCRIPT_DIR/launchagents/com.f1deck.app.plist"
UI_PLIST_SOURCE="$SCRIPT_DIR/launchagents/com.f1deck.ui.plist"

if [ ! -f "$PLIST_SOURCE" ]; then
    echo "Error: com.f1deck.app.plist not found"
    exit 1
fi

echo "Installing F1-Deck LaunchAgent..."

mkdir -p "$LAUNCHAGENT_DIR"

echo "Copying plist files..."
cp "$PLIST_SOURCE" "$LAUNCHAGENT_DIR/"
cp "$UI_PLIST_SOURCE" "$LAUNCHAGENT_DIR/"

echo "Updating paths in plist..."
sed -i '' "s|/Users/dantaylor/Projects/f1-deck|$SCRIPT_DIR|g" "$LAUNCHAGENT_DIR/com.f1deck.app.plist"
sed -i '' "s|/Users/dantaylor/Projects/f1-deck|$SCRIPT_DIR|g" "$LAUNCHAGENT_DIR/com.f1deck.ui.plist"

echo "Loading LaunchAgent..."
launchctl load "$LAUNCHAGENT_DIR/com.f1deck.app.plist"

echo ""
echo "F1-Deck will start automatically on login."
echo ""
echo "Commands:"
echo "  launchctl list | grep f1deck     # Check status"
echo "  launchctl stop com.f1deck.app     # Stop"
echo "  launchctl start com.f1deck.app    # Start"
echo "  tail -f /tmp/f1-deck.log          # View logs"
echo ""
echo "To uninstall:"
echo "  launchctl unload $LAUNCHAGENT_DIR/com.f1deck.app.plist"
echo "  rm $LAUNCHAGENT_DIR/com.f1deck.app.plist"
echo "  rm $LAUNCHAGENT_DIR/com.f1deck.ui.plist"
