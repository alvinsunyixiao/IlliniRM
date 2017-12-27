mkdir mp4
for f in *.MOV; do ffmpeg -i "$f" -vcodec copy -acodec copy "mp4/${f%.MOV}.mp4" -hide_banner && rm "$f"; done
#需要下载好所有的 MOV，丢到全部 MOV 所在的文件夹里执行
