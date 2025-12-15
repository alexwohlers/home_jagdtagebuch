#!/bin/bash
# Initial setup script for Jagdtagebuch on Strato server
# Run this once to set up the application

set -e

APP_DIR="/var/www/jagdtagebuch"
REPO_URL="https://github.com/alexwohlers/home_jagdtagebuch.git"

echo "=== Jagdtagebuch Setup ==="

# Clone repository
if [ ! -d "$APP_DIR" ]; then
    echo "Cloning repository..."
    sudo git clone $REPO_URL $APP_DIR
    sudo chown -R www-data:www-data $APP_DIR
else
    echo "Directory exists, pulling latest..."
    cd $APP_DIR
    sudo -u www-data git pull
fi

cd $APP_DIR

# Create virtual environment
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    sudo -u www-data python3 -m venv venv
fi

# Install dependencies
echo "Installing dependencies..."
sudo -u www-data venv/bin/pip install --upgrade pip
sudo -u www-data venv/bin/pip install -r requirements.txt

# Run migrations
echo "Running migrations..."
sudo -u www-data venv/bin/python manage.py migrate

# Collect static files
echo "Collecting static files..."
sudo -u www-data venv/bin/python manage.py collectstatic --noinput

# Install systemd service
echo "Installing systemd service..."
sudo cp deploy/jagdtagebuch.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable jagdtagebuch
sudo systemctl start jagdtagebuch

# Remind about nginx
echo ""
echo "=== Setup complete! ==="
echo ""
echo "Next steps:"
echo "1. Add the nginx configuration from deploy/nginx.conf to your nginx site config"
echo "2. Test nginx config: sudo nginx -t"
echo "3. Reload nginx: sudo systemctl reload nginx"
echo ""
echo "Create a superuser:"
echo "cd $APP_DIR && sudo -u www-data venv/bin/python manage.py createsuperuser"
echo ""
echo "Check service status:"
echo "sudo systemctl status jagdtagebuch"