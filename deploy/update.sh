#!/bin/bash
# Update script for Jagdtagebuch
# Run this to pull latest changes and restart

set -e

APP_DIR="/var/www/jagdtagebuch"

echo "=== Updating Jagdtagebuch ==="

cd $APP_DIR

# Pull latest changes
echo "Pulling latest changes..."
sudo -u www-data git pull

# Install any new dependencies
echo "Installing dependencies..."
sudo -u www-data venv/bin/pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
sudo -u www-data venv/bin/python manage.py migrate

# Collect static files
echo "Collecting static files..."
sudo -u www-data venv/bin/python manage.py collectstatic --noinput

# Restart service
echo "Restarting service..."
sudo systemctl restart jagdtagebuch

echo ""
echo "=== Update complete! ==="
sudo systemctl status jagdtagebuch --no-pager