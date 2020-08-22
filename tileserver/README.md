# Tirex user
create service user tirex (useradd -M tirex, usermod -L tirex)

# Mapnik
~~copy rides.xml to /usr/share/maps and ensure permissions~~
~~copy simra_rides.conf to /etc/tirex/renderer/mapnik/~~
remove /etc/tirex/renderer/mapnik
create symlink to mapnik_config directory: ln -s /var/simra/SimRa2/tileserver/mapnik_config /etc/tirex/renderer/mapnik
remove /etc/tirex/renderer/openseamap/ (all contents)

# Tirex tiles
create folders for each config, like /var/lib/tirex/tiles/simra_rides_density
set permissions: chown tirex:tirex -R /var/lib/tirex

# Services
copy service files to /etc/systemd/service/
create folder /var/run/tirex with permissions tirex:tirex
update /etc/tirex/renderer : plugindir should be /usr/local/lib/mapnik/input, fontdir=/usr/local/lib/mapnik/fonts
