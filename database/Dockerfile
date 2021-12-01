FROM postgis/postgis

COPY simra.sql.gz /docker-entrypoint-initdb.d/

RUN cd /docker-entrypoint-initdb.d/ && gunzip simra.sql.gz

COPY 20_init.sh /docker-entrypoint-initdb.d/

RUN cd /docker-entrypoint-initdb.d/ && rm 10_postgis.sh
