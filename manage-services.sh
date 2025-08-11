#!/bin/bash

case "$1" in
  start)
    echo "Starting PostgreSQL..."
    brew services start postgresql@15
    echo "Starting Redis..."
    brew services start redis
    echo "All services started!"
    brew services list
    ;;
  stop)
    echo "Stopping services..."
    brew services stop postgresql@15
    brew services stop redis
    echo "All services stopped!"
    ;;
  status)
    echo "=== Service Status ==="
    brew services list
    ;;
  restart)
    brew services restart postgresql@15
    brew services restart redis
    echo "All services restarted!"
    ;;
  *)
    echo "Usage: $0 {start|stop|status|restart}"
    exit 1
    ;;
esac
