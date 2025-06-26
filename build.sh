 #!/bin/bash

for i in "$@"; do
  case $i in
    --prefix=*)
      PREFIX="${i#*=}"
      ;;
    *)
      echo "Unknown option: $i"
      exit 1
      ;;
  esac
done

install -Dm755 app.sh  $PREFIX/bin/asteroid-shooter
install -Dm644 spaceshooter.py  $PREFIX/spaceshooter.py
install -Dm644 asteroid.png  $PREFIX/asteroid.png
install -Dm644 player1.png  $PREFIX/player1.png
install -Dm644 player2.png  $PREFIX/player2.png
install -Dm644 laser.wav  $PREFIX/laser.wav
install -Dm644 explosion.wav  $PREFIX/explosion.wav
install -Dm644 powerup.wav  $PREFIX/powerup.wav
install -Dm644 space_shooter_loop.wav  $PREFIX/space_shooter_loop.wav
install -Dm644 io.github.denzilferreira.asteroid_shooter.png  $PREFIX/share/icons/hicolor/512x512/apps/io.github.denzilferreira.asteroid_shooter.png
install -Dm644 io.github.denzilferreira.asteroid_shooter.desktop  $PREFIX/share/applications/io.github.denzilferreira.asteroid_shooter.desktop
install -Dm644 io.github.denzilferreira.asteroid_shooter.metainfo.xml  $PREFIX/share/metainfo/io.github.denzilferreira.asteroid_shooter.metainfo.xml