#!/bin/bash
# Update script for Jagdtagebuch
# Handles git conflicts with settings.py and performs full deployment

APP_DIR="/var/www/jagdtagebuch"
SETTINGS_FILE="$APP_DIR/jagdtagebuch/settings.py"

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track success/failure
declare -a RESULTS
ERRORS=0

# Function to log success
success() {
    echo -e "${GREEN}${NC} $1"
    RESULTS+=(" $1")
}

# Function to log failure
failure() {
    echo -e "${RED}${NC} $1"
    RESULTS+=(" $1")
    ((ERRORS++))
}

# Function to log info
info() {
    echo -e "${YELLOW}${NC} $1"
}

echo ""
echo ""
echo "       Jagdtagebuch Update Script         "
echo ""
echo ""

cd $APP_DIR

# Step 1: Save settings
info "[1/8] Saving local settings..."
if cp $SETTINGS_FILE /tmp/settings_backup.py 2>/dev/null; then
    success "Settings saved to /tmp/settings_backup.py"
else
    failure "Could not save settings"
fi

# Step 2: Git pull
info "[2/8] Pulling latest changes from GitHub..."
git fetch origin 2>&1
if git reset --hard origin/main 2>&1; then
    COMMIT=$(git log -1 --pretty=format:"%h - %s")
    success "Git pull complete: $COMMIT"
else
    failure "Git pull failed"
fi

# Step 3: Restore settings
info "[3/8] Restoring local settings..."
if cp /tmp/settings_backup.py $SETTINGS_FILE 2>/dev/null; then
    success "Settings restored"
else
    failure "Could not restore settings"
fi

# Step 4: Check subpath settings
info "[4/8] Checking subpath routing settings..."
if grep -q "FORCE_SCRIPT_NAME" $SETTINGS_FILE; then
    success "Subpath settings present"
else
    info "Adding subpath routing settings..."
    cat >> $SETTINGS_FILE << 'SETTINGS'

# Subpath routing settings for /jagdtagebuch/
FORCE_SCRIPT_NAME = '/jagdtagebuch'
CSRF_TRUSTED_ORIGINS = ['http://194.164.206.13', 'https://194.164.206.13']
SESSION_COOKIE_PATH = '/jagdtagebuch'
CSRF_COOKIE_PATH = '/jagdtagebuch'
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
SETTINGS
    success "Subpath settings added"
fi

# Step 5: Install dependencies
info "[5/8] Installing dependencies..."
if venv/bin/pip install -r requirements.txt -q 2>&1; then
    PKG_COUNT=$(venv/bin/pip list 2>/dev/null | wc -l)
    success "Dependencies installed ($PKG_COUNT packages)"
else
    failure "Dependency installation failed"
fi

# Step 6: Create migrations
info "[6/8] Creating migrations..."
MIGRATION_OUTPUT=$(venv/bin/python manage.py makemigrations --noinput 2>&1)
if echo "$MIGRATION_OUTPUT" | grep -q "No changes"; then
    success "No new migrations needed"
else
    success "Migrations created"
fi

# Step 7: Run migrations
info "[7/8] Running database migrations..."
MIGRATE_OUTPUT=$(venv/bin/python manage.py migrate --noinput 2>&1)
if echo "$MIGRATE_OUTPUT" | grep -q "No migrations to apply"; then
    success "Database up to date (no migrations to apply)"
else
    APPLIED=$(echo "$MIGRATE_OUTPUT" | grep "Applying" | wc -l)
    if [ "$APPLIED" -gt 0 ]; then
        success "Applied $APPLIED migration(s)"
    else
        success "Database migrated"
    fi
fi

# Step 8: Collect static files
info "[8/8] Collecting static files..."
STATIC_OUTPUT=$(venv/bin/python manage.py collectstatic --noinput 2>&1)
STATIC_COUNT=$(echo "$STATIC_OUTPUT" | grep -oP '\d+ static file' | grep -oP '\d+' || echo "0")
if [ "$STATIC_COUNT" = "0" ]; then
    success "Static files up to date"
else
    success "Collected $STATIC_COUNT static file(s)"
fi

# Fix permissions
info "Fixing permissions..."
chown -R www-data:www-data $APP_DIR
success "Permissions set (www-data)"

# Restart service
echo ""
info "Restarting Jagdtagebuch service..."
systemctl restart jagdtagebuch

# Wait for service to start
sleep 2

# Check service status
if systemctl is-active --quiet jagdtagebuch; then
    success "Service restarted successfully"
else
    failure "Service failed to start"
fi

# Print summary
echo ""
echo ""
echo "              ZUSAMMENFASSUNG             "
echo ""
echo ""

for result in "${RESULTS[@]}"; do
    echo "  $result"
done

echo ""
echo ""

if [ $ERRORS -eq 0 ]; then
    echo -e "${GREEN} Update erfolgreich abgeschlossen!${NC}"
    echo ""
    echo "   URL: http://194.164.206.13/jagdtagebuch/"
    echo "   Zeit: $(date '+%Y-%m-%d %H:%M:%S')"
    echo ""
else
    echo -e "${RED}  Update mit $ERRORS Fehler(n) abgeschlossen${NC}"
    echo ""
    echo "Letzte Log-Einträge:"
    journalctl -u jagdtagebuch -n 10 --no-pager
fi

echo ""