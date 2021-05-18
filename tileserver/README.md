# Configuration
## Tirex user

Create a service user `tirex` via `useradd -M tirex`. `usermod -L tirex` locks the account, so password authentication is disabled. 

## Mapnik

Remove the initial mapnik directory via `sudo rmdir /etc/tirex/renderer/mapnik`.  
Create a symlink to the `mapnik_config` directory: `ln -s /var/simra/SimRa2/tileserver/mapnik_config /etc/tirex/renderer/mapnik`  
`rm -r /etc/tirex/renderer/openseamap/*` to delete all content from the `openseamap` directory.  

## Tirex tiles

Create folders for each config file in `/tileserver/mapnik_config/`, e.g. `/var/lib/tirex/tiles/simra_rides_density`.  
Now set permissions via `chown tirex:tirex -R /var/lib/tirex`.  

## Services

Copy service files to `/etc/systemd/service/`.  
Create folder `/var/run/tirex` with `permissions tirex:tirex`.  
Update `/etc/tirex/renderer : plugindir` should be `/usr/local/lib/mapnik/input`, `fontdir=/usr/local/lib/mapnik/fonts`.  