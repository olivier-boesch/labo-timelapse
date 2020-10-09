ffmpeg -y -i images/img_%05d.jpg -r 25  -vcodec libx264 -vf scale=1920:1080 timelapse.mp4

