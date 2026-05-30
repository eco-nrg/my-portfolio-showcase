#!/bin/bash

GREEN='\e[32m'
RED='\e[31m'
RESET='\e[0m'

# Define the default list of server aliases
DEFAULT_ALIASES=("eco-pi_1" "eco-pi_2" "eco-pi_3" "eco-pi_4" "eco-pi_5" "eco-pi_6")

REMOTE_ALIASES=()

# Parse command-line arguments
while [[ $# -gt 0 ]]; do
  key="$1"

  case $key in
    --systemd)
      if [ "$2" = "all" ]; then
        RESTART_ALL=true
      else
        SYSTEMD_SERVICES=($2)
      fi
      shift
      shift
      ;;
    --alias)
      if [ "$2" = "all" ]; then
        REMOTE_ALIASES=("${DEFAULT_ALIASES[@]}")
      else
        REMOTE_ALIASES=($2)
      fi
      shift
      shift
      ;;
    *)
      # Handle any other flags or arguments here
      shift
      ;;
  esac
done

# Define the remote service names (common for all servers)
REMOTE_SERVICES=("app.service" "app-ui.service" "telegraf.service")

# Define the path to your Git repository (where all services reside)
GIT_REPO_DIRECTORY="/home/raspi/python/station/"

# Function to check and display logs for inactive services on a specified server
check_service_health() {
  server_alias="$1"
  service_name="$2"

  # Combine SSH commands and use a single connection
  ssh -A -t "$server_alias" "
    sudo systemctl restart $service_name
    sleep 5  # Add a delay to allow the service to fully start
    check_health=\$(sudo systemctl is-active $service_name)
    if [ \"\$check_health\" = \"active\" ]; then
      echo -e \"Service $service_name is ${GREEN}active${RESET} on $server_alias.\"
    else
      echo -e \"Service $service_name is ${RED}not active${RESET} on $server_alias. Displaying journal logs:\"
      sudo journalctl -f -u $service_name
    fi
  "
}

# Execute actions for each specified server alias
for SERVER_ALIAS in "${REMOTE_ALIASES[@]}"; do
  # Combine SSH commands and use a single connection
  ssh -A -t "$SERVER_ALIAS" "
    cd $GIT_REPO_DIRECTORY && git checkout dev_v2 && git pull origin dev_v2
  "

  if [ "$RESTART_ALL" = true ]; then
    # Restart all relevant services and check their health
    for SERVICE in "${REMOTE_SERVICES[@]}"; do
      check_service_health "$SERVER_ALIAS" "$SERVICE"
    done
  else
    # Restart the specified systemd services and check their health
    for SERVICE in "${SYSTEMD_SERVICES[@]}"; do
      check_service_health "$SERVER_ALIAS" "$SERVICE"
    done
  fi
done
