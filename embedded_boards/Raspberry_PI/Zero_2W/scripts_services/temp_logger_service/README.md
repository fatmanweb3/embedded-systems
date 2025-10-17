CPU Temperature Logger for Embedded Linux (Raspberry Pi) 🌡️
This repository provides a CPU Temperature Logger implemented using a Bash script and a systemd service on Linux (tested on Raspberry Pi). The script reads the CPU temperature from the kernel's thermal interface and logs it to a file at regular intervals.

🚀 Overview
The logger:

Reads CPU temperature from /sys/class/thermal/thermal_zone0/temp.
Logs timestamped temperature data to /home/admin/templog.txt.
Runs as a systemd service for continuous operation.
Designed for embedded Linux systems like Raspberry Pi.


📋 Prerequisites

Linux-based system (e.g., Raspberry Pi with Raspberry Pi OS).
User account with permissions to create files in /home/admin.
bash and bc installed (usually pre-installed on Raspberry Pi OS).
Root access to configure systemd services.


🛠️ Setup Instructions
1. Read CPU Temperature Manually
To verify the CPU temperature interface:
cat /sys/class/thermal/thermal_zone0/temp

Example output:
48500

This represents 48.5°C (divide by 1000).

2. Create the Temperature Logger Script
Create a new script file:
nano /home/admin/temp_logger.sh

Paste the following content:
#!/bin/bash

while true
do
  temp=$(cat /sys/class/thermal/thermal_zone0/temp)
  echo "$(date): CPU Temp = $(echo "scale=1; $temp/1000" | bc)°C" >> /home/admin/templog.txt
  sleep 10
done

Notes:

Ensure the shebang (#!/bin/bash) is the first line.
The script logs the temperature every 10 seconds to /home/admin/templog.txt.

Make the script executable:
chmod +x /home/admin/temp_logger.sh

Test the script manually:
/home/admin/temp_logger.sh
# Run for a few seconds, then stop with Ctrl+C
cat /home/admin/templog.txt


3. Create a Systemd Service
Create a systemd service file:
sudo nano /etc/systemd/system/temp_logger.service

Paste the following content:
[Unit]
Description=CPU Temperature Logger
After=network.target

[Service]
ExecStart=/home/admin/temp_logger.sh
Restart=always
User=admin
WorkingDirectory=/home/admin

[Install]
WantedBy=multi-user.target

Enable and start the service:
sudo systemctl daemon-reload
sudo systemctl enable temp_logger.service
sudo systemctl start temp_logger.service

Check the service status:
sudo systemctl status temp_logger.service


4. Fix Permissions (If Needed)
If the service fails with status=126 (non-executable script), ensure correct permissions:
sudo chmod +x /home/admin/temp_logger.sh
sudo chown admin:admin /home/admin/temp_logger.sh
sudo chmod 755 /home/admin

Reload and restart the service:
sudo systemctl daemon-reload
sudo systemctl restart temp_logger.service


5. Debugging Commands
If issues persist, use these commands to troubleshoot:
# Run script as the service user
sudo -u admin /home/admin/temp_logger.sh

# Check script file type and line endings
file /home/admin/temp_logger.sh

# Remove Windows-style carriage returns (if any)
sudo sed -i 's/\r$//' /home/admin/temp_logger.sh

# Verify permissions
ls -l /home/admin/temp_logger.sh
ls -ld /home/admin
namei -l /home/admin/temp_logger.sh

# View service logs
journalctl -u temp_logger.service -e

# Check log file output
tail /home/admin/templog.txt


6. Important Notes 📝

Use absolute paths: Always use full paths (e.g., /home/admin/templog.txt) in scripts and service files. Systemd does not expand ~ or $(whoami).
Shebang requirement: Ensure the script starts with a valid shebang (#!/bin/bash or #!/usr/bin/env bash).
Permissions: The admin user must have read/write access to /home/admin and execute permissions on temp_logger.sh.
Log file: The log file (/home/admin/templog.txt) will grow over time. Consider implementing log rotation for production use.
Security: If SELinux or AppArmor is enabled, additional configuration may be needed to allow script execution.


📊 Example Log Output
After running the service, /home/admin/templog.txt will contain entries like:
Fri Oct 17 21:00:00 IST 2025: CPU Temp = 48.5°C
Fri Oct 17 21:00:10 IST 2025: CPU Temp = 48.7°C


🔧 Troubleshooting

Service fails with status=126:
Ensure the script is executable (chmod +x /home/admin/temp_logger.sh).
Verify the shebang line is correct.


No log output:
Check if the admin user has write permissions to /home/admin.
Run the script manually to debug (sudo -u admin /home/admin/temp_logger.sh).


Service not starting:
Check logs with journalctl -u temp_logger.service -e.
Verify the User and WorkingDirectory in the service file match your setup.




📄 License
This project is licensed under the MIT License.

🙌 Contributing
Feel free to open issues or submit pull requests to improve this logger!