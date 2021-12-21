#! /bin/sh

WELCOMETXT=`cat <<EOF
You started the setup for the SimRa visualization project. This script
is meant for Ubuntu 18.04 TLS.

ATTENTION: The following packages will be reinstalled during the
process:
* pip

It is recommended to use a newly setup Ubuntu server for this software.
Do not install it on your personal computer!

Most of the software will be installed in `/var/simra/`.
EOF
`
while true; do
  echo "${WELCOMETXT}"
  read -p "Do you want to continue? [y/n]" yn
  case $yn in
    [Yy]* ) break;;
    [Nn]* ) exit;;
    * ) echo "Please answer yes or no.";;
  esac
done

echo "# Creating working directory `/var/simra`"
sudo mkdir /var/simra
cd /var/simra

echo "# Updating packages"
sudo apt update
sudo apt upgrade



echo "# Installing python"
sudo apt install python3.8 python3.8-dev
echo "Setting python command to point towards python 3.8"
update-alternatives --remove python /usr/bin/python2
sudo update-alternatives --install /usr/bin/python python /usr/bin/python3.8 10
echo "Reinstalling pip"
sudo apt remove python-pip
sudo apt install python3-pip
python -m pip install pip
source ~/.bashrc
echo "Installing missing python packages"
pip install django rdp geopy gpxpy



echo "# Setting up PostgreSQL"
sudo apt install postgresql postgresql-contrib
echo "Creating database and user `simra`"
sudo -u postgres createuser simra
sudo -u postgres createdb simra
echo "Setting up PostGIS extension"
sudo apt install postgis



echo "# Setting up Mapnik"
echo "Updating clang"
sudo add-apt-repository -y ppa:ubuntu-toolchain-r/test
sudo apt-get update -y
wget -O - https://apt.llvm.org/llvm-snapshot.gpg.key | sudo apt-key add -
sudo apt-add-repository "deb http://apt.llvm.org/bionic/ llvm-toolchain-bionic-6.0 main"
sudo apt-get install -y gcc-6 g++-6 clang-6.0 lld-6.0
export CXX="clang++-6.0" && export CC="clang-6.0"
sudo apt-get install zlib1g-dev clang make pkg-config curl
echo "Installing mapnik"
git clone https://github.com/mapnik/mapnik && cd mapnik
git checkout v3.0.x
git submodule update --init
source bootstrap.sh
./configure CUSTOM_CXXFLAGS="-D_GLIBCXX_USE_CXX11_ABI=0" CXX=${CXX} CC=${CC}
echo "Starting Mapnik compilation. This may take a while!"
make
sudo make install
cd ..
echo "Installing python Mapnik bindings"
sudo apt install python-mapnik



echo "# Setting up Tirex"
echo "Creating tirex user"
sudo useradd -M tirex
sudo usermod -L tirex
echo "Installing tirex"
# Meet missing dependencies
sudo apt install devscripts
# Install Perl modules
sudo cpan IPC::ShareLite JSON GD LWP
sudo cpan CPAN # Updates to newer cpan
# Install, build and install Tirex
git clone git@github.com:openstreetmap/tirex.git
cd tirex
echo "Starting Tirex compilation. This may take a while!"
make
sudo make install
cd ..
echo "Setting up Tirex directory structure"
sudo mkdir /var/lib/tirex/ /var/run/tirex/ /var/log/tirex/
sudo chown tirex:tirex -R /var/run/tirex
chown tirex:tirex -R /var/lib/tirex/ /var/run/tirex/ /usr/lib/tirex/ /var/log/tirex/ /etx/tirex/
sudo rmdir /etc/tirex/renderer/mapnik
sudo ln -s /var/simra/simra-visualizations-server/tileserver/mapnik_config /etc/tirex/renderer/mapnik
sudo rm -r /etc/tirex/renderer/openseamap/*
echo "Setting up Tirex map directories"
sudo mkdir /var/lib/tirex/tiles
sudo mkdir incident-combined popularity-combined relative-speed-aggregated relative-speed-single rides-density_all rides-density_rushhourevening rides-density_rushhourmorning rides-density_weekend rides-original stoptimes surface-quality-aggregated surface-quality-single
sudo chown tirex:tirex -R /var/lib/tirex
echo "Copying service files into `/etc/systemd/system/`"
sudo cp /var/simra/simra-visualizations-server/tileserver/config/tirex-master.service /etc/systemd/system
sudo cp /var/simra/simra-visualizations-server/tileserver/config/tirex-backend-manager.service /etc/systemd/system



echo "# Setting up Apache 2 and mod_tile"
sudo apt install apache2 apache2-dev
sudo cp /var/simra/simra-visualizations-server/tileserver/config/simra-ubuntu.conf /etc/apache2/mods-available
sudo ln -s /etc/apache2/mods-available/simra-ubuntu.conf /etc/apache2/mods-enabled
sudo systemctl restart apache2
# mod_tile
sudo add-apt-repository -y ppa:osmadmins/ppa
sudo apt-get install -y libapache2-mod-tile
sudo ln -s /var/lib/tirex/tiles /var/lib/mod_tile



echo "# Django, Python and populating the database"
sudo apt install libgpgme-dev python-apt python3-testresources
sudo apt-get install libpq-dev python-dev pkg-config libcairo2-dev libpq5=10.17-0ubuntu0.18.04.1 libpq-dev python-dev
pip install psycopg2
pip install -r requirements.txt
cd api/
rm -r SimRaAPI/migrations/
cd ..
echo "Migrating the datamodel into the database"
python manage.py makemigrations SimRaAPI
python manage.py migrate



echo "# Setting up Graphhopper"
sudo apt install default-jdk
wget https://graphhopper.com/public/releases/graphhopper-web-3.0.jar -P ./graphhopper/
echo "Downloading pbf street data from geofabrik int `/var/simra/pbf`"
# Download street map data for DACH (Germany, Austria, Switzerland)
sudo mkdir /var/simra/pbf
sudo wget http://download.geofabrik.de/europe/dach-latest.osm.pbf -P /var/simra/pbf/



echo "# Separating the street data into legs"
python importer/importer/create_legs.py



VAR1=`cat <<EOF
-----------------------------------------------------------------------
The installation was finished, but there remain things to do:



Last, set your `~/.local/bin/` directory in the `PATH` variable. To do
so, open `~./bashrc` (or your respective shell configuration file) and
paste the following at the end of the file:

# set PATH so it includes user's private bin if it exists
if [ -d "$HOME/.local/bin" ] ; then
    PATH="$HOME/.local/bin:$PATH"
fi



Setup the database by entering the PostgreSQL CLI with `sudo -u postgres
psql`. Now execute the following commands:

psql=# alter user simra with encrypted password 'simra';
psql=# grant all privileges on database simra to simra;
psql=# alter role simra superuser;
psql=# CREATE EXTENSION postgis;
psql=# \q



If you have not done yet, install pgAdmin4, as it is a database tool
with geo data visualization.



Update `/etc/tirex/renderer/mapnik.conf`: `plugindir` should be
`/usr/local/lib/mapnik/input` and `fontdir` should be
`/usr/local/lib/mapnik/fonts`.



In your `mapnik_config/` directory change the `mapfile` variable to
point towards the map files inside `/var/simra-visualizations-server
/tileserver/mapnik_maps/`.


-----------------------------------------------------------------------
To start the application, do the following:

* Execute `python manage.py runserver` in the `api/` directory to start
  the Django server.
* Start the Tirex services via `sudo systemctl start tirex-master` and
  `sudo systemctl start tirex-backend-manager`
* Start the Graphhopper service. java -jar
  ./graphhopper/graphhopper-web-3.0.jar server ./graphhopper/config.yml
* Use the Imposm tool to fill the database: Navigate into the
  `osm importer` directory and execute
  `sudo ./imposm-0.10.0-linux-x86-64/imposm import -mapping mapping.yml
  -read "berlin-latest.osm.pbf" -overwritecache -write
  -connection postgis://simra:simra12345simra@localhost/simra`. This
  creates the schema `import` with the table `osm_ways` which is used in
  the next step by the `create_legs.py` script.
* Start the import process by executing
  `python importer/importer/import.py`
EOF
`
echo "${VAR1}"