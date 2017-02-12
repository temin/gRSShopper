#!/bin/bash
# Bash script written by Saad Ismail - me@saadismail.net
# Modified by Stephen Downes - stephen@downes.ca

# If /root/.my.cnf exists then it won't ask for root password
if [ -f /root/.my.cnf ]; then
	echo "Please enter the NAME of the new gRSShopper database! (example: grshopper1)"
	read dbname
	echo "Please enter the gRSShopper database CHARACTER SET! (example: latin1, utf8, ...)"
	read charset
	echo "Creating new gRSShopper database..."
	mysql -e "CREATE DATABASE ${dbname} /*\!40100 DEFAULT CHARACTER SET ${charset} */;"
	echo "Database successfully created!"
	echo "Showing existing databases..."
	mysql -e "show databases;"
	echo ""
	echo "Please enter the NAME of the new gRSShopper database user! (example: user1)"
	read username
	echo "Please enter the PASSWORD for the new gRSShopper database user!"
	read userpass
	echo "Creating new user..."
	mysql -e "CREATE USER ${username}@localhost IDENTIFIED BY '${userpass}';"
	echo "User successfully created!"
	echo ""
	echo "Granting ALL privileges on ${dbname} to ${username}!"
	mysql -e "GRANT ALL PRIVILEGES ON ${dbname}.* TO '${username}'@'localhost';"
	mysql -e "FLUSH PRIVILEGES;"
	echo "Making database tables..."
      for sql_file in `ls /var/www/gRSShopper/cgi-bin/sql`; do mysql -uUSER -pPASSWORD DATABASE < /var/www/gRSShopper/cgi-bin/sql/$sql_file ; done
	echo "Done."
	exit
	
# If /root/.my.cnf doesn't exist then it'll ask for root password	
else
	echo "Please enter root user MySQL password!"
	read rootpasswd
	echo "Please enter the NAME of the new gRSShopper database! (example: grshopper1)"
	read dbname
	echo "Please enter the gRSShopper database CHARACTER SET! (example: latin1, utf8, ...)"
	read charset
	echo "Creating new gRSShopper database..."
	mysql -uroot -p${rootpasswd} -e "CREATE DATABASE ${dbname} /*\!40100 DEFAULT CHARACTER SET ${charset} */;"
	echo "Database successfully created!"
	echo "Showing existing databases..."
	mysql -uroot -p${rootpasswd} -e "show databases;"
	echo ""
	echo "Please enter the NAME of the new gRSShopper database user! (example: user1)"
	read username
	echo "Please enter the PASSWORD for the new gRSShopper database user!"
	read userpass
	echo "Creating new user..."
	mysql -uroot -p${rootpasswd} -e "CREATE USER ${username}@localhost IDENTIFIED BY '${userpass}';"
	echo "User successfully created!"
	echo ""
	echo "Granting ALL privileges on ${dbname} to ${username}!"
	mysql -uroot -p${rootpasswd} -e "GRANT ALL PRIVILEGES ON ${dbname}.* TO '${username}'@'localhost';"
	mysql -uroot -p${rootpasswd} -e "FLUSH PRIVILEGES;"
	echo "Making database tables..."
      for sql_file in `ls /var/www/gRSShopper/cgi-bin/sql`; do mysql -uUSER -pPASSWORD DATABASE < /var/www/gRSShopper/cgi-bin/sql/$sql_file ; done
	echo "Done."
	exit
fi