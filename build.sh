 #!/bin/bash
install -Dm755 app.sh  /app/bin/asteroid-shooter
install -Dm644 spaceshooter.py  /app/spaceshooter.py
install -Dm644 asteroid.png  /app/asteroid.png
install -Dm644 player1.png  /app/player1.png
install -Dm644 player2.png  /app/player2.png
install -Dm644 laser.wav  /app/laser.wav
install -Dm644 explosion.wav  /app/explosion.wav
install -Dm644 powerup.wav  /app/powerup.wav
install -Dm644 space_shooter_loop.wav  /app/space_shooter_loop.wav
install -Dm644 requirements.txt  /app/requirements.txt
install -Dm644 io.github.denzilferreira.asteroid_shooter.png  /app/share/icons/hicolor/512x512/apps/io.github.denzilferreira.asteroid_shooter.png
install -Dm644 io.github.denzilferreira.asteroid_shooter.desktop  /app/share/applications/io.github.denzilferreira.asteroid_shooter.desktop
install -Dm644 io.github.denzilferreira.asteroid_shooter.metainfo.xml  /app/share/metainfo/io.github.denzilferreira.asteroid_shooter.metainfo.xml