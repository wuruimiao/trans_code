#!/bin/bash

name=$1
# 在云上，失败：不重试，删除原文件
# true/false
on_yun=$2

# 视频已是hevc编码
encoding=$(ffprobe -v error -select_streams v:0 -show_entries stream=codec_name -of default=noprint_wrappers=1:nokey=1 "$name")

if [ "$encoding" == "hevc" ]; then
  # echo "Video $name is already encoded in H.265 (HEVC), do nothing."
  exit 0
fi

new_name="${name%.*}_h265.mp4"

echo "start $name to $new_name"
if [ "$on_yun" == "false" ]; then
  ffmpeg -hide_banner -hwaccel cuda -i "$name" -c:v hevc_nvenc -y "$new_name"
else
  ffmpeg -hide_banner -hwaccel auto -i "$name" -c:v libx265 -y "$new_name"
fi

ret=$?

# 硬件加速失败，非云上重试
if [ $ret -ne 0 ] && [ "$on_yun" == "false" ]; then
  echo "Hardware acceleration failed, retrying without it... $name"
  ffmpeg -hide_banner -i "$name" -c:v libx265 -y "$new_name"
  ret=$?
fi

if [ $ret -eq 0 ]; then
  # 转码成功
  echo "Verifying $new_name for errors..."
  ffprobe_output=$(ffprobe -v error -read_intervals "%+#1" -show_entries frame=pkt_size -of csv=p=0 "$new_name" 2>&1)
  # 检测失败
  if [[ $ffprobe_output == *"error"* ]]; then
    echo "Error: Detected issues in the newly encoded video $new_name. Deleting the file."
    if [ -f "$new_name" ]; then
      rm "$new_name"
    fi
    exit 1
  fi

  # 检测成功，替换文件
  echo "done $name to $new_name"
  if [ -f "$new_name" ]; then
    rm -f "$name"
    name="${name%.*}.mp4"
    mv "$new_name" "$name"
  fi
else
  # 转码失败，删除转码视频
  echo "Error: ffmpeg command failed."
  rm -f "$new_name"
  # 云上删除原文件
  if [ "$on_yun" == "true" ]; then
    rm -r "$name"
  fi
fi
