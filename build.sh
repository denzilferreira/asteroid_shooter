 #!/bin/bash
install -Dm755 app.sh  /app/bin/asteroid-shooter
install -Dm755 spaceshooter/spaceshooter.py  /app/spaceshooter/spaceshooter.py
install -Dm644 spaceshooter/asteroid.png  /app/spaceshooter/asteroid.png
install -Dm644 spaceshooter/player1.png  /app/spaceshooter/player1.png
install -Dm644 spaceshooter/player2.png  /app/spaceshooter/player2.png
install -Dm644 spaceshooter/laser.wav  /app/spaceshooter/laser.wav
install -Dm644 spaceshooter/explosion.wav  /app/spaceshooter/explosion.wav
install -Dm644 spaceshooter/powerup.wav  /app/spaceshooter/powerup.wav
install -Dm644 spaceshooter/space_shooter_loop.wav  /app/spaceshooter/space_shooter_loop.wav
install -Dm644 io.github.denzilferreira.asteroid_shooter.png  /app/share/icons/hicolor/512x512/apps/io.github.denzilferreira.asteroid_shooter.png
install -Dm644 io.github.denzilferreira.asteroid_shooter.desktop  /app/share/applications/io.github.denzilferreira.asteroid_shooter.desktop
install -Dm644 io.github.denzilferreira.asteroid_shooter.metainfo.xml  /app/share/metainfo/io.github.denzilferreira.asteroid_shooter.metainfo.xml