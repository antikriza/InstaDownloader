#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}=== Instagram Stories Bot Setup ===${NC}"
echo "This script will help you set up your environment securely."

# Create necessary directories
echo -e "\n${YELLOW}Creating necessary directories...${NC}"
mkdir -p logs
mkdir -p secrets
chmod 700 secrets # Restrict permissions for secrets directory

# Check if .env exists and create it if not
if [ ! -f .env ]; then
    echo -e "\n${YELLOW}Creating .env file...${NC}"
    cp .env.example .env 2>/dev/null || echo -e "${RED}Error: .env.example not found${NC}"
    
    # Ask for Telegram token
    echo -e "\n${YELLOW}Please enter your Telegram Bot Token:${NC}"
    read -r token
    if [ -n "$token" ]; then
        echo "Saving token to .env file..."
        sed -i "s/TELEGRAM_TOKEN=.*/TELEGRAM_TOKEN=$token/" .env
        
        # Also save to Docker secrets
        echo -e "\n${YELLOW}Saving token to Docker secrets...${NC}"
        echo "$token" > secrets/telegram_token.txt
        chmod 600 secrets/telegram_token.txt
    else
        echo -e "${RED}No token provided. You'll need to edit .env manually.${NC}"
    fi
else
    echo -e "\n${YELLOW}.env file already exists. Skipping creation.${NC}"
    echo "If you want to recreate it, delete the current .env file and run this script again."
fi

# Set proper permissions
echo -e "\n${YELLOW}Setting proper file permissions...${NC}"
chmod 600 .env # Only owner can read and write

# Check for Docker
echo -e "\n${YELLOW}Checking for Docker...${NC}"
if command -v docker >/dev/null 2>&1 && command -v docker-compose >/dev/null 2>&1; then
    echo -e "${GREEN}Docker and Docker Compose are installed.${NC}"
    
    # Ask to build and run
    echo -e "\n${YELLOW}Would you like to build and run the bot now? (y/n)${NC}"
    read -r answer
    if [[ "$answer" =~ ^[Yy]$ ]]; then
        echo -e "\n${YELLOW}Building and starting the bot...${NC}"
        docker-compose up -d
        echo -e "\n${GREEN}Bot started successfully!${NC}"
        echo "You can check the logs with: docker-compose logs -f"
    else
        echo -e "\n${YELLOW}Skipping build. To start the bot later, run:${NC}"
        echo "docker-compose up -d"
    fi
else
    echo -e "${RED}Docker and/or Docker Compose not found. Please install them first.${NC}"
    echo "Visit https://docs.docker.com/get-docker/ for installation instructions."
fi

echo -e "\n${GREEN}Setup completed successfully!${NC}"
echo -e "Remember: Never commit your .env file or secrets directory to version control."
echo -e "The .gitignore file has been configured to prevent this."

# Final security reminder
echo -e "\n${YELLOW}Security Reminder:${NC}"
echo "1. Keep your credentials secure"
echo "2. Regularly rotate your Telegram bot token"
echo "3. Check for security updates to dependencies"
echo "4. Review logs periodically for unusual activity"