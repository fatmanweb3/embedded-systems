
#!/bin/bash
while true
do
  temp=$(cat /sys/class/thermal/thermal_zone0/temp)
  echo "$(date): CPU Temp = $(echo "scale=1; $temp/1000" | bc)°C" >> /home/admin/templog.txt
  sleep 10
done
