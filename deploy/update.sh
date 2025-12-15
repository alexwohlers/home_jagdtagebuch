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
echo "[1/7] Saving local settings..."
cp $SETTINGS_FILE /tmp/settings_backup.py

# Reset and pull
echo "[2/7] Pulling latest changes from GitHub..."
git fetch origin
git reset --hard origin/main

# Restore settings
echo "[3/7] Restoring local settings..."
cp /tmp/settings_backup.py $SETTINGS_FILE

# Ensure subpath settings are present
if ! grep -q "FORCE_SCRIPT_NAME" $SETTINGS_FILE; then
    echo "[3b/7] Adding subpath routing settings..."
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
echo "[4/7] Installing dependencies..."
venv/bin/pip install -r requirements.txt -q

# Run migrations
echo "[5/7] Running migrations..."
venv/bin/python manage.py migrate --noinput

# Collect static files
echo "[6/7] Collecting static files..."
venv/bin/python manage.py collectstatic --noinput -v 0

# Fix permissions
echo "[7/7] Fixing permissions..."
chown -R www-data:www-data $APP_DIR

# Restart service
echo ""
echo "Restarting Jagdtagebuch service..."
systemctl restart jagdtagebuch

# Show status
echo ""
echo "=== Update complete! ==="
systemctl status jagdtagebuch --no-pager -l | head -15