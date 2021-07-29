# my.vay

In diesem Repository finden Sie den vollständigen Quelltext zur prototypischen Implementierung der Impfplattform my.vay. Diese wurde im Rahmen der Seminararbeit "Konzeption und prototypische Implementierung der Impfplattform my.vay" umgesetzt.

# Voraussetzungen

- [PostgreSQL](https://www.postgresql.org/download/)
- [Python 3](https://www.python.org/downloads/) 
- Alle Python-Bibliotheken aus <code>requirements.txt</code>


# Installation

1. Klonen des Repositories.
   ```
    $ git clone https://github.com/ValentinFFM/my.vay.git
    ```
2. Öffnen der Kommando-Zeile in dem Repository und installieren aller notwendigen Bibliotheken mit folgendem Befehl:
    ```
    $ pip install -r requirements.txt
    ```

# Starten der Plattform

1. Starten eines PostgreSQL-Servers
2. Verbinden des PostgreSQL-Servers mit der Applikation, indem Serveradresse sowie Login-Daten in der Variable <code>app.config['SQLALCHEMY_DATABASE_URI']</code> in der Datei <code>\_\_init__.py</code> angepasst werden.
3. Die letzten Zeilen in <code>models.py</code> zum erstmaligen Initiieren der Datenbank-Models aus dem Kommentar entfernen.
4. run.py starten
5. Die letzten Zeilen in <code>models.py</code> wieder auskommentieren.
6. run.py starten
7. Browser mit diesem [Link](http://0.0.0.0:3000/) öffnen oder auf manuell die URL: <code>0.0.0.0:3000</code> eingeben


# Entwickler-Team

- Valentin Müller
- Karen Pagnia
- Pia Schramm
- Tristan Schwarzer
