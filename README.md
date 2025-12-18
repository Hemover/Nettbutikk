# Nettbutikk
Terminoppgave for høsten

Planlegging

Jeg skal lage en Nettbutikk som selger varer knyttet til nettverk som f.eks switcher, rutere, nettverkskabler, mesh-enheter osv.

Den skal være funksjonell som betyr at jeg skal bruke VS code for kodingen, html og css for design, javascript for funksjonalitet, Flask for hosting av webserver på rasberry pi, og mariaDB for lagring av kjøpshistorikk og varer. 

Jeg kan vise kompetanse i drift, utvikling og brukerstøtte via: utvikling viser jeg med programmeringen, drift viser jeg med hosting av webserver og kunnskapen om varene, og brukerstøtte viser jeg med den universelle utformingen av nettsiden og håndtering av tilbakemeldingen fra brukertestingen

Bilde av Figma:
<img width="955" height="718" alt="Skjermbilde 2025-11-11 110644" src="https://github.com/user-attachments/assets/952a43ff-bbf8-4c59-ace1-e99ef1fe4041" />



Sikkerhetstilltak: 

bruker git for backup, har en .gitignore for diverse som f.eks .env filer som inneholder ting som skal holdes privat som f.eks API key og database bruker. Jeg skal lage brukere med begrenset tilgang og oppdaterer programvaren. Sterke passord er også en selvfølge og passordet til brukere skal være hashed.


Brukerveiledning:
For å få dette prosjektet til å funke lokalt på maskinen din så må du bruke en terminal med linux/bash og gjøre følgende: 
Finn stedet i filene dine du vil ha prosjektet ditt i og klon nettbutikk-repository, da skal du ende opp med en README.md og Herman_nettbutikk, gå deretter inn på Herman_nettbutikk og følg disse neste stegene nøye, 

1. Lag en .env fil i Herman_nettbutikk og kopier inn dette:                                                                                                                  DB_HOST=localhost
DB_PORT=3306
DB_USER=db_user
DB_PASS=SlippMeg1nn!
DB_NAME=nettbutikk
API_KEY=super-hemmelig-nøkkel-123
2. Installer python med (linux/bash: sudo apt install python3-pip python3-venv)
3. Lag en .venv fil med kommandoen: (linux/bash:python3 -m venv .venv)
4. Aktiver .venv ved å skrive: source .venv/bin/activate
5. Installer deretter MariaDB på hele systemet: sudo apt install mariadb-server og libmariadb-dev build-essential
6. Last ned følgende pakker med pip install: flask flask-bcrypt python-dotenv mariadb flask_bcrypt
7. Logg inn på Mariadb, kopier alt i Database.sql og lim inn i mariadb-terminalen.
8. lag database-brukeren med følgende kommando: CREATE USER 'db_user'@'localhost' IDENTIFIED BY 'SlippMeg1nn!';
9. GRANT ALL PRIVILEGES on nettbutikk.* TO 'db_user'@'localhost';
10. FLUSH PRIVILEGES;
11. Kjør python scriptet og alt burde fungere.
