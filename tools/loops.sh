#!/bin/bash
# Pasa los cuatro loops a WebP animados 16:10 para la grilla del README (assets/*.webp).
# Los del sandbox salen de los loops del portfolio; el del portfolio, de tools/grabar-portfolio.mjs.
# Correr: tools/loops.sh [nombre...]   (W, FPS y Q se pueden cambiar por variable de entorno)
set -e
cd "$(dirname "$0")/.."
P=../portfolio-2026/public/media/sandbox
W=${W:-720}; FPS=${FPS:-20}; Q=${Q:-68}
quiero=" $* "
loop() { # nombre entrada inicio duración recorte
  [ -n "$*" ] && [ "$quiero" != "  " ] && [[ "$quiero" != *" $1 "* ]] && return
  local tmp; tmp=$(mktemp -d)
  ffmpeg -y -v error -ss "$3" -t "$4" -i "$2" -vf "$5,scale=$W:-2:flags=lanczos,fps=$FPS" "$tmp/%05d.png"
  img2webp -loop 0 -lossy -q "$Q" -m 6 -mixed -d $((1000 / FPS)) "$tmp"/*.png -o "assets/$1.webp" >/dev/null 2>&1
  rm -rf "$tmp"
  echo "assets/$1.webp $(du -h "assets/$1.webp" | cut -f1)"
}
# el del portfolio arranca con la ventana de Kench (5.9 s en adelante) y sigue con la entrada: así el primer cuadro no es blanco
loop portfolio tools/out/portfolio.mp4 0 11.9 "split[a][b];[a]trim=5.9:11.9,setpts=PTS-STARTPTS[v];[b]trim=0.6:5.9,setpts=PTS-STARTPTS[e];[v][e]concat=n=2:v=1,crop=iw:iw*10/16:0:0"
loop ukiyo $P/ukiyo.mp4 0 13 "null"
loop kora $P/kora.mp4 0 8 "crop=iw:iw*10/16:0:(ih-iw*10/16)/2"
loop itapiru $P/lopez-itapiru.mp4 0 8 "crop=ih*16/10:ih"
