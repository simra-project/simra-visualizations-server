1. Install Python 3.8 + dev headers
2. Install PostgreSQL, create database and user simra, allow password access from local
3. Install PostGis
4. Install Mapnik https://github.com/mapnik/mapnik TAG v3.0.23
5. Install Mapnik Python Bindings https://github.com/mapnik/python-mapnik BRANCH 3.0.x
6. Install Tirex
7. Configure Tirex using README, (double check permissions!), start tirex-master und tirex-backend-manager
8. Import rides  
  * Install missing packages via `pip3 install psycopg2 postgis tqdm rdp geopy gpxpy`  
  * Execute `python3 import.py`  
8. Test Tirex: `tirex-batch --prio=25 map=simra_rides bbox=-180,-90,180,90 z=0-6` und `tirex-status`
9. Install apache2, apache2-dev
10. Install mod_tile https://github.com/openstreetmap/mod_tile
11. Sym link /var/lib/tirex/tiles to /var/lib/mod_tile, set up conf
12. Start apache2

