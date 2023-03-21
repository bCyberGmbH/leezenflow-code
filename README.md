# Warning! This is a work in progress version!

# Leezenflow_Matrix_Test

## Hinweise zur Ausgabe im Terminal
- Für eine gescheite Farbdarstellung sollte bei der Ausgabe darauf geachtet werden, dass der "true color mode" von dem benutzen Terminal unterstützt wird.
- Dies ist z.B. bei dem Standard Mac Terminal nicht der Fall, aber dafür z.B. bei iTerm2 oder dem Standard Terminal von VS Code.

## Ausführung

- Standardmäßig wird als Ausgabe das LED-Panel angesteuert. Dies kann über die `--display` Option mit `led_panel` oder `terminal` angepasst werden
- Es ist auch möglich mehrere displays gleichzeitig anzusteuern. Dazu einfach zweimal den `--display` Parameter mit unterschiedlichen Optionen mitgeben.

## Verwendung mit Testdaten:
- Zum Starten der normalen Version bitte den Befehl `sudo python3 leezenflow.py --test 2 --animation 6 --distance 100 --bicycle-speed 20` ausführen

- Zum Starten der Version mit Gelbphase bitte den Befehl `sudo python3 leezenflow.py --test 2 --animation 7 --distance 100 --bicycle-speed 20 --bicycle-yellow-speed 25` ausführen



## Verwendung mit dem UDP Simulations Skript

- In einem Terminal `python3 traffic_light_udp_simulation.py` ausführen

- Und in einem zweiten Terminal:

- Zum Starten der normalen Version bitte den Befehl `sudo python3 leezenflow.py --receiver 2 --animation 6 --distance 100 --bicycle-speed 20` ausführen

- Zum Starten der Version mit Gelbphase bitte den Befehl `sudo python3 leezenflow.py --receiver 2 --animation 7 --distance 100 --bicycle-speed 20 --bicycle-yellow-speed 25` ausführen
