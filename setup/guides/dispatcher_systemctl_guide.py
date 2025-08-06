sudo systemctl start dispatcher.service       # Start the service now
sudo systemctl stop dispatcher.service        # Stop the service
sudo systemctl restart dispatcher.service     # Stop then start (fresh run)
sudo systemctl reload dispatcher.service      # Reload config only (if supported)
sudo systemctl try-restart dispatcher.service # Restart only if running
sudo systemctl reload-or-restart dispatcher.service  # Reload if possible, else restart


sudo systemctl enable dispatcher.service      # Start on boot
sudo systemctl disable dispatcher.service     # Don’t start on boot
sudo systemctl is-enabled dispatcher.service  # Check if enabled
sudo systemctl mask dispatcher.service        # Block all manual/auto starts
sudo systemctl unmask dispatcher.service      # Allow starts again


systemctl status dispatcher.service                # See live status and last few logs

sudo journalctl -u dispatcher.service              # View full log history
sudo journalctl -u dispatcher.service -n 50        # Show last 50 log lines
sudo journalctl -u dispatcher.service -n 50 --no-pager  # No scrolling
sudo journalctl -u dispatcher.service -f           # Live log (tail -f style)


systemctl list-units --type=service                 # List all active services
systemctl list-unit-files                          # List all installed service files
systemctl list-unit-files | grep dispatcher        # Find just dispatcher.service