for f in *.MOV; do ffmpeg -i "$f" -vcodec copy -acodec copy "mp4/${f%.MOV}.mp4" -hide_banner && rm "$f"; done
