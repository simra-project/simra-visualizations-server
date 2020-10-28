#!/usr/bin/env bash

tirex-batch --prio=25 map=junctions-stoptimes    bbox=12.587585,52.060935,14.040527,52.855864 z=6-15
tirex-batch --prio=25 map=rides-density_all      bbox=12.587585,52.060935,14.040527,52.855864 z=6-15
tirex-batch --prio=25 map=rides-density_rushhour bbox=12.587585,52.060935,14.040527,52.855864 z=6-15
tirex-batch --prio=25 map=rides-density_weekend  bbox=12.587585,52.060935,14.040527,52.855864 z=6-15
tirex-batch --prio=25 map=rides-original         bbox=12.587585,52.060935,14.040527,52.855864 z=6-15
tirex-batch --prio=25 map=rides-quality-segments bbox=12.587585,52.060935,14.040527,52.855864 z=6-15
tirex-batch --prio=25 map=surface-quality        bbox=12.587585,52.060935,14.040527,52.855864 z=6-15