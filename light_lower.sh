#!/bin/bash
file_path="/sys/class/backlight/amdgpu_bl1/brightness"
increment=2

current_value=$(<"$file_path")
new_value=$((current_value - increment))

if [ "$new_value" -gt 255 ]; then
  new_value=255
elif [ "$new_value" -lt 0 ]; then
  new_value=0
fi

echo "$new_value" | sudo tee "$file_path"
