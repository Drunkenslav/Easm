#!/bin/bash
# Run both backend and frontend locally

echo "🚀 Starting EASM Platform Locally"
echo "=================================="
echo ""

# Make scripts executable
chmod +x run-backend-local.sh run-frontend-local.sh

# Check if tmux is available
if command -v tmux &> /dev/null; then
    echo "Using tmux to run both services..."
    echo ""

    # Kill existing session if it exists
    tmux kill-session -t easm 2>/dev/null || true

    # Create new session
    tmux new-session -d -s easm

    # Split window
    tmux split-window -h

    # Run backend in left pane
    tmux select-pane -t 0
    tmux send-keys "cd $(pwd) && ./run-backend-local.sh" C-m

    # Run frontend in right pane
    tmux select-pane -t 1
    tmux send-keys "cd $(pwd) && sleep 5 && ./run-frontend-local.sh" C-m

    echo "✅ Services started in tmux session 'easm'"
    echo ""
    echo "To view:"
    echo "   tmux attach -t easm"
    echo ""
    echo "To stop:"
    echo "   tmux kill-session -t easm"
    echo ""
    echo "Services:"
    echo "   Backend:  http://localhost:8000"
    echo "   Frontend: http://localhost:5173"
    echo "   API Docs: http://localhost:8000/docs"
    echo ""
    echo "Login credentials:"
    echo "   Username: admin"
    echo "   Password: admin123"
    echo ""

    # Optionally attach
    read -p "Attach to tmux session now? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        tmux attach -t easm
    fi

else
    echo "⚠️  tmux not found. You need to run in separate terminals:"
    echo ""
    echo "Terminal 1:"
    echo "   ./run-backend-local.sh"
    echo ""
    echo "Terminal 2:"
    echo "   ./run-frontend-local.sh"
    echo ""
    echo "Or install tmux:"
    echo "   sudo apt-get install tmux"
fi
