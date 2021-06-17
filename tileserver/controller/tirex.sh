#! /bin/sh

while [ -n "$1" ]; do # while loop starts

	case "$1" in

        -c) # Creates the /var/run/tirex directory the right way
            sudo mkdir /var/run/tirex
            sudo chown tirex:tirex /var/run/tirex
            echo "Created /var/run/tirex and made 'tirex' the owner."
            shift
            ;;
        
        -d) # Development reset
            sudo ./$0 -e maps
            sudo ./$0 -s tm
            shift
            ;;
        
        -h) # Prints help
            VAR1=`cat <<EOF
Usage: tirex.sh [OPTION] [PARAMETER]

Shell script to manage tirex-related services.

Known values for OPTION are:

  -c    Creates the directory /var/run/tirex and gives ownership to 'tirex' user.

  -d    Developer shortcut. Calls this script with '-e maps' and '-s all'.

  -h    Prints this help message.

  -e    Empties specified directories.

            Known values for PARAMETER for this command are:
              maps    All map tile meta data in /etc/lib/tirex/tiles map folders. -!For now only popularity maps are affected!-

  -s    Restarts specified services.

            Known values for PARAMETER for this command are:
              all     Restarts all of the services which can be restarted by this command at once.
              a2      Restarts the apache2 server.
              tm      Restarts tirex-master.
              tbm     Restarts tirex-backend-manager

  -t    Apply tirex related commands.

            Known values for PARAMETER for this command are:
              status  Display the extended tirex status.
\n
EOF
`
            echo "${VAR1}"
            shift
            ;;
        
        -e) # Empties the specified directory
            param=$2
            if [ $param = "maps" ]
            then
                sudo rm -r /var/lib/tirex/tiles/popularity-combined/*
                sudo rm -r /var/lib/tirex/tiles/popularity-original_avoided/*
                sudo rm -r /var/lib/tirex/tiles/popularity-original_chosen/*
                sudo rm -r /var/lib/tirex/tiles/popularity-score/*
                echo "Destroyed all map tiles files inside the popularity map folders."
            else
                echo "Unknown command option. Can't empty the directory. Use -h for available options."
            fi
            shift
            ;;

        -s) # Restarts a service
            param=$2
            if [ $param = "all" ]
            then
                sudo systemctl restart tirex-master
                sudo systemctl restart tirex-backend-manager
                sudo systemctl restart apache2
                echo "Restarted tirex-master, tirex-master-backend and apache2."
            elif [ $param = "tm" ]
            then
                sudo systemctl restart tirex-master
                echo "Restarted tirex-master."
            elif [ $param = "tbm" ]
            then
                sudo systemctl restart tirex-backend-manager
                echo "Restarted tirex-backend-manager."
            elif [ $param = "a2" ]
            then
                sudo systemctl restart apache2
                echo "Restarted apache2."
            else
                echo "Unknown command option. Can't restart. Use -h for available options."
            fi
            shift
            ;;

        -t) # Tirex related commands
            param=$2
            if [ $param = "status" ] # Display extensive tirex-status
            then
                tirex-status --once --extended
            else
                echo "Unknown command option. Use -h for available options."
            fi
            shift
            ;;

        *) echo "Option $1 not recognized. Type 'reload-tirex.sh -h' for available options.";;

	esac
    shift
done