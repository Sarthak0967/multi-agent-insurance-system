#!/bin/bash
set -e

echo '========================================'
echo ' Installing Docker on Ubuntu...'
echo '========================================'

# Update system
sudo apt-get update -y
sudo apt-get install -y ca-certificates curl gnupg lsb-release git

# Install Docker
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=\ signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \ stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt-get update -y
sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Add ubuntu user to docker group
sudo usermod -aG docker ubuntu
sudo systemctl enable docker
sudo systemctl start docker

echo 'Docker installed successfully!'
docker --version

echo '========================================'
echo ' Uploading project files...'
echo '========================================'
mkdir -p /home/ubuntu/insurance-app

echo '========================================'
echo ' Creating .env file...'
echo '========================================'
cat > /home/ubuntu/insurance-app/.env << 'ENVEOF'
GOOGLE_API_KEY=AIzaSyDqBLH3Mbj06g11UZqZ_y7VWuk0jcba84A
ENVEOF

echo 'Setup complete! Ready for file upload.'