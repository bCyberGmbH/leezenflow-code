# Leezenflow_Matrix_Test

## Hinweise zur Test Matrix
- Code noch in der Testphase
- Ich habe zum testen iTerm2 benutzt, da das standard Terminal nicht genügend Farben darstellen kann.
- Nach Ergänzung der Logik, die nur die veränderten Reihen neu zeichnet, kann nun scheinbar auch die normale VS-Code Bash Konsole benutzt werden.
- Im Prinzip ist grundsätzlich erstmal alles so geblieben wie es war (habe den Code von der [animation_original] () kopiert) und nur die Logik für die eigene Matrix ergänzt in der neuen Animation [animation_manu] ().

## Umbau der Animation
- Zusätzlich wurde erstmal provisorisch eingebaut, dass die LeezenFlow-Ampel wie gewünscht 10 Sekunden früher auf die andere Phase umspringt.
- Momentan ist es noch so, dass die LF-Ampel nun ca. 10 Sekunden früher (wenn die Werte danach noch anfangen herumzuspringen natürlich dementsprechend später) auf die andere Phase umspringt. Also z.B.: von rot auf grün, obwohl die Echte-Ampel noch weitere 10 Sekunden lang rot ist. Dabei bleibt die Ampel dann aber erstmal die restliche Zeit lang, also bis die Echte-Ampel umspringt, auf voll grün und fängt erst an abzulaufen, wenn die Grünphase der Echten-Ampel tatsächlich angefangen hat.
- Dies sollte in Zukunft noch durch weitere Angaben erweitert werden wie z.B. ein Array mit den letzten 10 Zeiten der jeweiligen Echten-Ampelphase, um daraus dann den Mittelwert zu berechnen und damit dann die Animation etwas abzurunden. Z.B.: könnte man dann bei einem Mittelwert von 45 Sekunden Grün, beim Umschalten der LF-Ampel 45 + 10 Sekunden für die Grünphase einplanen. Obwohl dabei dann trotzdem noch abweichungen entstehen könnten wenn die Rotphase länger als erwartet dauern sollte. Da müssten wir nochmal überlegen, wie wir das "abzurunden" um ein wieder hochspringenspringen der Ampel zu verhindern.
- Die ersten umsetzungen der zusätzlichen Variablen wurde bereits eingebaut, also füllen des Arrays der letzten 10 Phasen + Mittelwert bilden, wird aber momentan noch nicht benutzt.
- Die Parameter für Abstand von LF-Ampel zu Echter-Ampel und Durchschnittsgeschwindigkeit wurden bereits hinzugefügt aber bisher auch noch nicht verwendet

## Ausführung
- Ich habe den Code bei mir auf einen Raspberry gepackt und von da aus ausgeführt und bearbeitet.
- Die Logik für das Fahrrad ist noch nicht wirklich ergänzt, weil dafür Funktionen aus dem Repo https://github.com/hzeller/rpi-rgb-led-matrix benutzt wurden. Z.B.: für die Räder folgende: https://github.com/hzeller/rpi-rgb-led-matrix/blob/f88355e46faafb9de7f1e59dd258ab36c7e7b097/lib/graphics.cc#L120
- Zu Testzwecken habe ich nur die Funktion DrawCircle kopiert und als `DrawCircleForTestMatrix` in python code umgebaut um zumindest die zwei Reifen zu zeichnen.
- Zum Starten bitte den Befehl `sudo python leezenflow.py --test 2 --animation 6` ausführen
