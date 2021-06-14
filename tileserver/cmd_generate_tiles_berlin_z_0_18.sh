#!/usr/bin/env bash

tirex-batch --prio=25 map=incident-combined             bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=relative-speed                bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=rides-density_all             bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=rides-density_rushhourmorning bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=rides-density_rushhourevening bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=rides-density_weekend         bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=rides-original                bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=stoptimes                     bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=surface-quality-aggregated    bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=surface-quality-single        bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
tirex-batch --prio=25 map=popularity-combined           bbox=12.587585,52.060935,14.040527,52.855864 z=0-18
