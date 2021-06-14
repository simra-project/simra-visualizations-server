# Setup on Ubuntu Linux

Latest update: 13.06.2021

This guide describes the project setup for Ubuntu 18.04. The application was tested with VirtualBox and the Virtual Box Extension Package.

1. Install python 3.8 and development headers.
2. Install pip3.

## Setup of postgresql

- Install postgreSQL via `sudo pacman -S postgresql`. Check the version via `psql --version`. Should be `13.2`.
- Create the database `simra`.
- Create the database user `simra`.
- Allow local database access.
- Install postgis via `sudo pacman -S postgis`.
- Log into the postgresql database as a super user and execute `CREATE EXTENSION postgis;`. Log out again.

## Setup mapnik and tirex

- Install mapnik via `sudo pacman -S mapnik`.
- Install `pyhton-mapnik`.
- Install Tirex.
- `sudo mkdir /var/lib/tirex/ /var/run/tirex/ /usr/lib/tirex/ /var/log/tirex/ /etx/tirex/`
- `chown tirex:tirex -R /var/lib/tirex/ /var/run/tirex/ /usr/lib/tirex/ /var/log/tirex/ /etx/tirex/`

## Setup django

- `pip3 install django`

Inside the `/api/` directory run:

- `rmdir /SimRaAPI/migrations`
- `python3 manage.py makemigrations SimRaAPI`
- `python3 manage.py migrate`

## Setup apache2

- `yay -S apache`
- Start apache

## Setup mod_tile

- `mkdir /usr/include/iniparser/`
- `sudo cp /usr/include/iniparser.h /usr/include/iniparser/`
- `sudo ln -s /var/lib/tirex/tiles /var/lib/mod_tile`

## Graphhopper

- Clone the project
- Copy the config file
- Start the graphhopper server by executing `./start.sh` inside the `/graphhopper/` directory.

## Initial database population

Fill the database with street segments of the OSM street network: `sudo ./imposm-0.10.0-linux-x86-64/imposm import -mapping mapping.yml -read "berlin-latest.osm.pbf" -overwritecache -write -connection postgis://simra:simra@localhost/simra`. This creates the schema `import` with the table `osm_ways` which is used in the next step by the `create_legs.py` script.

## Run the importer

- Execute `python3 importer/importer/create_legs.py`. This populates the database with legs.
- Execute `python3 importer/importer/import.py`. This will import the CSV data into the database.

## List of known issues

The directory `/var/run/tirex/` is deleted on every shutdown of the machine. Thus, `sudo mkdir /var/run/tirex/` and `chown tirex:tirex -R /var/run/tirex/` have to be repeated. You can provide a shell script to do so in your autostart directory.
