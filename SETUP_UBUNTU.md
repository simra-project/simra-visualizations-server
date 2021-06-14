- [Setup on Ubuntu Linux](#setup-on-ubuntu-linux)
  - [Setup Instructions](#setup-instructions)
    - [Python](#python)
    - [PostgreSQL Database](#postgresql-database)
    - [Setup mapnik and tirex](#setup-mapnik-and-tirex)
    - [Setup apache2](#setup-apache2)
    - [Setup mod_tile](#setup-mod_tile)
    - [Setup django](#setup-django)
    - [Graphhopper](#graphhopper)
    - [Initial database population](#initial-database-population)
    - [Run the importer](#run-the-importer)
    - [Rendering Map Tiles](#rendering-map-tiles)
  - [List of known issues](#list-of-known-issues)



# Setup on Ubuntu Linux

Latest update: 13.06.2021

This guide describes the project setup for Ubuntu 18.04.



## Setup Instructions

Make sure all your packages are up to date with `sudo apt update`.

### Python

Install Python 3.8 and python development headers: `sudo apt install python3.8 python3.8-dev`

`python3.8 --version` should return `Python 3.8.10` now.

Now, to install pip for python 3.8, first execute `sudo apt remove python-pip` to remove existing pip versions. Then check, whether pip is no longer installed (`pip --version`).

Now, change the `python` comand to point towards `python3.8` instead of python 2:

```
update-alternatives --remove python /usr/bin/python2
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
```

Next, install pip for Python 3.6 via `sudo apt install python3-pip` (`pip3 --version`) and then install pip for Python 3.8 by using pip: `python -m pip install pip`. Last, set your `~/.local/bin/` directory in the `PATH` variable. To do so, open `~./bashrc` (or your respective shell configuration file) and paste the following at the end of the file:

```
# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi
```

Now restart the terminal or execute `source ~/.bashrc` and check whether the installation was successful with `pip --version` which should return XYZ.

(Steps taken from [this](https://stackoverflow.com/questions/63207385/how-do-i-install-pip-for-python-3-8-on-ubuntu-without-changing-any-defaults) tutorial.)

### PostgreSQL Database

Install the database via `sudo apt install postgresql postgresql-contrib`. `psql --version`. should return `10.17`.

The following lines create a new database user `simra` and a database of the same name. To do so we use the default psql user `postgres` who has superadmin access to the entire PostgreSQL instance.

```
sudo -u postgres createuser simra
sudo -u postgres createdb simra
```

Next, enter the psql command line interface as the user `postgres` to allocate a password to the new `simra` user:

```
sudo -u postgres psql
psql=# alter user simra with encrypted password 'simra';
psql=# grant all privileges on database simra to simra;
```

The CLI should return `ALTER ROLE` and `GRANT` as visual feedback when both operations where successful. You can also check whether the database was created by typing `\list` into the psql CLI which will list all databases.

To quit the CLI, type `\q` and press enter.

(The steps above where taken from [this](https://medium.com/coding-blocks/creating-user-database-and-adding-access-on-postgresql-8bfcd2f4a91e) tutorial.)

Install postgis via `sudo apt install postgis`. Next, you need to log into the database as the `postgres` user and activate PostGIS by executing  `CREATE EXTENSION postgis;`. The `SELECT PostGIS_full_version();` should yield version 2.4.3.Log out again.

We recommend the tool pgAdmin4 for managing the PostgreSQL database because it allows for geo data visualization. It can be installed, following [this tutorial](https://www.pgadmin.org/download/pgadmin-4-apt/).

### Setup mapnik and tirex

Clone the mapnik repository via `git clone https://github.com/mapnik/mapnik` and enter the `mapnik/` directory.

```
# you might have to update your outdated clang
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo apt-get update -y

# https://askubuntu.com/questions/509218/how-to-install-clang
# Grab the key that LLVM use to GPG-sign binary distributions
wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -
sudo apt-add-repository "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-6.0 main"
sudo apt-get install -y gcc-6 g++-6 clang-6.0 lld-6.0
export CXX="clang++-6.0" && export CC="clang-6.0"


# Install mapnik
git clone https://github.com/mapnik/mapnik mapnik
cd mapnik
git checkout v3.0.x
git submodule update --init
sudo apt-get install zlib1g-dev clang make pkg-config curl
source bootstrap.sh
./configure CUSTOM_CXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" CXX=${CXX} CC=${CC}
make -j 3 # Uses 3 CPU cores
make test
sudo make install
```

- Install `python-mapnik`.
- Install Tirex.
- `sudo mkdir /var/lib/tirex/ /var/run/tirex/ /usr/lib/tirex/ /var/log/tirex/ /etx/tirex/`
- `chown tirex:tirex -R /var/lib/tirex/ /var/run/tirex/ /usr/lib/tirex/ /var/log/tirex/ /etx/tirex/`

(More information can be found [here](https://www.linuxbabe.com/ubuntu/openstreetmap-tile-server-ubuntu-18-04-osm).)

### Setup apache2

- `yay -S apache`
- Start apache

### Setup mod_tile

- `mkdir /usr/include/iniparser/`
- `sudo cp /usr/include/iniparser.h /usr/include/iniparser/`
- `sudo ln -s /var/lib/tirex/tiles /var/lib/mod_tile`

### Setup django

Now that the database is set up, we will create database models which will define the form of the database tables which will be filled later. For that, the project uses the django framework which can be installed with pip: `pip install django`.

Next, install all needed dependencies. To do so, execute `sudo apt install libgpgme-dev`.
Then, execute `pip install -r requirements.txt`.

Navigate into the `/api/` directory (if necessary, remove `/SimRaAPI/migrations/`) and run:

```
python manage.py makemigrations SimRaAPI
python manage.py migrate
```

### Graphhopper

This component is used to determine the shortest routes between two GPS coordinates as well as to map match the raw GPS data onto a map.

- Clone the project
- Copy the config file
- Start the graphhopper server by executing `./start.sh` inside the `/graphhopper/` directory.

### Initial database population

Now the PostgreSQL database gets filled with basic map data, retrieved by the OSM service. To do so, we use the tool [Imposm](https://imposm.org/docs/imposm3/latest/).

Fill the database with street segments of the OSM street network: `sudo ./imposm-0.10.0-linux-x86-64/imposm import -mapping mapping.yml -read "berlin-latest.osm.pbf" -overwritecache -write -connection postgis://simra:simra@localhost/simra`. This creates the schema `import` with the table `osm_ways` which is used in the next step by the `create_legs.py` script.

### Run the importer

Next, the existing map data is separated into legs which represent single street segments of the street network. To do that, execute `python3 importer/importer/create_legs.py`.

Execute `python3 importer/importer/import.py`. This will import the CSV data into the database.

Attention, depending on the amount of data which is imported, this process can take a while.

### Rendering Map Tiles

Now that everything is set up, the data in the database can be rendered into PNG images which are used by the Tirex tile server.

Attention, depending on the amount of data which is imported, this process can take a while.

## List of known issues

The directory `/var/run/tirex/` is deleted on every shutdown of the machine. Thus, `sudo mkdir /var/run/tirex/` and `chown tirex:tirex -R /var/run/tirex/` have to be repeated. You can provide a shell script to do so in your autostart directory.
