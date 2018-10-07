#/bin/bash

repository="https://github.com/Downes/gRSShopper"
repoFolder="./update/repofolder"
repoCGI="./update/repofolder/cgi-bin/*"
backup="./backup"
cp -R ../cgi-bin/* $backup
rm -R -f $repoFolder
git clone $repository $repoFolder
cp -R $repoCGI ../cgi-bin
echo "Updated CGI"
