create service user tirex (useradd -M tirex, usermod -L tirex)
copy rides.xml to /usr/share/maps and ensure permissions
copy simra_rides.conf to /etc/tirex/renderer/mapnik/
remove /etc/tirex/renderer/openseamap/ (all contents)
create folder /var/lib/tirex/tiles/simra_rides
set permissions: chown tirex:tirex -R /var/lib/tirex
copy service files to /etc/systemd/service/
create folder /var/run/tirex with permissions tirex:tirex
update /etc/tirex/renderer : plugindir should be /usr/local/lib/mapnik/input, fontdir=/usr/local/lib/mapnik/fonts
