#!/bin/bash
# Update script for Jagdtagebuch
# Handles git conflicts with settings.py and performs full deployment

set -e

APP_DIR="/var/www/jagdtagebuch"
SETTINGS_FILE="$APP_DIR/jagdtagebuch/settings.py"

echo "=== Jagdtagebuch Update ==="
echo ""

cd $APP_DIR

# Save current settings
echo "[1/8] Saving local settings..."
cp $SETTINGS_FILE /tmp/settings_backup.py

# Reset and pull
echo "[2/8] Pulling latest changes from GitHub..."
git fetch origin
git reset --hard origin/main

# Restore settings
echo "[3/8] Restoring local settings..."
cp /tmp/settings_backup.py $SETTINGS_FILE

# Ensure subpath settings are present
if ! grep -q "FORCE_SCRIPT_NAME" $SETTINGS_FILE; then
    echo "[3b/8] Adding subpath routing settings..."
    cat >> $SETTINGS_FILE << 'SETTINGS'

# Subpath routing settings for /jagdtagebuch/
FORCE_SCRIPT_NAME = '/jagdtagebuch'
CSRF_TRUSTED_ORIGINS = ['http://194.164.206.13', 'https://194.164.206.13']
SESSION_COOKIE_PATH = '/jagdtagebuch'
CSRF_COOKIE_PATH = '/jagdtagebuch'
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SETTINGS
fi

# Install dependencies
echo "[4/8] Installing dependencies..."
venv/bin/pip install -r requirements.txt -q

# Create migrations if needed
echo "[5/8] Creating migrations..."
venv/bin/python manage.py makemigrations --noinput 2>/dev/null || true

# Run migrations
echo "[6/8] Running migrations..."
venv/bin/python manage.py migrate --noinput

# Collect static files
echo "[7/8] Collecting static files..."
venv/bin/python manage.py collectstatic --noinput -v 0

# Fix permissions
echo "[8/8] Fixing permissions..."
chown -R www-data:www-data $APP_DIR

# Restart service
echo ""
echo "Restarting Jagdtagebuch service..."
systemctl restart jagdtagebuch

# Wait for service to start
sleep 2

# Show status
echo ""
echo "=== Update complete! ==="
echo ""
systemctl status jagdtagebuch --no-pager -l | head -15

# Test if service is running
if systemctl is-active --quiet jagdtagebuch; then
    echo ""
    echo " Jagdtagebuch is running at http://194.164.206.13/jagdtagebuch/"
else
    echo ""
    echo " ERROR: Service failed to start!"
    journalctl -u jagdtagebuch -n 20 --no-pager
    exit 1
fi