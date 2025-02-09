#!/usr/bin/env bash

# Uninstalling cany conflictin packages
echo "Uninstalling any conflictin packages.."
for pkg in docker.io docker-doc docker-compose docker-compose-v2 podman-docker containerd runc; do sudo apt-get remove $pkg; done
echo "Conflictin packages successfully uninstalled"


# Adding Docker's official GPG key
echo "Adding Docker's official GPG key..."
sudo apt-get update -y
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "Docker's official GPG key successfully added"


# Adding the repository to Apt sources
echo "Adding the repository to Apt sources"
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update -y
echo "Repository successfully added to APT Sources"


# Installing latest version
echo "Installing latest version.."
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
echo "Latest version successfully installed.."


# Verifying installation
echo "Verifying installation"
 sudo docker run hello-world


# install certbot plugin
sudo apt-get update && \
    apt-get install -y certbot python3-certbot-nginx 