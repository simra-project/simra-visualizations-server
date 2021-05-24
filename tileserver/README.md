# Configuration
## Tirex user

Create a service user `tirex` via `useradd -M tirex`. `usermod -L tirex` locks the account, so password authentication is disabled. 

## Mapnik

Remove the initial mapnik directory via `sudo rmdir /etc/tirex/renderer/mapnik`.  
Create a symlink to the `mapnik_config` directory: `ln -s /var/simra/SimRa2/tileserver/mapnik_config /etc/tirex/renderer/mapnik`  
`rm -r /etc/tirex/renderer/openseamap/*` to delete all content from the `openseamap` directory.  

## Tirex tiles

Create the folders `/var/lib/tirex/` and `/var/lib/tirex/tiles/`. Then, create folders in `/var/lib/tirex/tiles/` for each config file in `/tileserver/mapnik_config/`, e.g. `/var/lib/tirex/tiles/simra_rides_density`.  
Now set permissions via `chown tirex:tirex -R /var/lib/tirex`.  

## Services

Create the folder `/etc/systemd/service/` and copy the service files `tirex-backend-manager.service` and `tirex-master.service` (inside `/tileserver/config/`) into it. (For Arch linux copy the service files into `/etc/systemd/system/`.)  

Then, create the folder `/var/run/tirex` with permissions: `sudo chown tirex:tirex -R /var/run/tirex`.  
Last, update `/etc/tirex/renderer/mapnik.conf`: `plugindir` should be `/usr/local/lib/mapnik/input` and `fontdir` should be `/usr/local/lib/mapnik/fonts`.  