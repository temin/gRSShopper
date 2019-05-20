gRSShopper
==========

This is a clone of [Stephen Downes'](https://www.downes.ca/) Personal Learning Environments (PLE) [gRSShopper](https://github.com/Downes/gRSShopper).

This clone contains few fixes and improvements that enabled me to install gRSShopper on [vanilla](https://en.wikipedia.org/wiki/Vanilla_software) Debian/Ubuntu server. Some fixes also originate from the comments Downes made in his [Installing gRSShopper on Reclaim](https://www.youtube.com/watch?v=T8PFEEQJ8kw) video.

Installation - on Debian/Ubuntu
-------------------------------

### Installing software

gRSShopper is a LAMP (P as Perl) application and the base packages to install are:

  ```
  # apt install apache2 libapache2-mod-perl2 mariadb-server python-mysqldb rsync cpanminus dh-make-perl
  ```

Optional: Install Git to get/manage gRSShopper files. You can do the same by downloading ZIP file from GitHub.

  ```
  # apt install git
  ```

Additionaly you need to install following Perl modules:

       MIME::Types
       MIME::Lite::TT::HTML
       CGI::Session
       Lingua::EN::Inflect
       JSON
       JSON::Parse
       JSON::XS
       Net::Facebook::Oauth2
       XML::OPML
       REST::Client
       Net::Twitter::Lite::WithAPIv1_1
       Digest::SHA1
       Email::Stuffer
       vCard
       Net::OAuth
       Image::Resize
       DBD::mysql
       Mastodon::Client

First install the modules available in repositories:

  ```
  apt install libmime-types-perl libmime-lite-tt-html-perl libcgi-session-perl liblingua-en-inflect-perl libjson-perl libjson-xs-perl libnet-facebook-oauth2-perl libxml-opml-perl librest-client-perl libnet-twitter-lite-perl libdigest-sha-perl libemail-stuffer-perl libtext-vcard-perl libnet-oauth-perl libdbd-mysql-perl libgd-perl libapache2-mod-perl2 liblocal-lib-perl
  ```

Next build the remaining modules with `cpanm`:

  ```
  # cpanm Image::Resize
  # cpanm Digest::SHA1
  # cpanm JSON::Parse
  # cpanm Mastodon::Client
  ```

NOTE: I was unable to build *Mastodon::Client* on Debian (8 & 9) and Ubuntu (16 & 18). As I will not be using Mastodon, I've created the **no_mastodon** branch with Mastodon code removed from the gRSShopper code.

NOTE: Different Debian/Ubuntu versions have different Perl modules available in the repositories. The above lists of Perl module packages to install and build are valid for Debian 9. For other versions check [INSTALL_versions](./INSTALL_versions.md).


### Apache config

Add or change Apache virtual host configuration file:

```apache
  <VirtualHost *:80>

    ServerName example.org

    DocumentRoot /var/www/grsshopper

    ScriptAlias /cgi-bin/ /var/www/grsshopper/cgi-bin/
    <Directory "/var/www/grsshopper/cgi-bin">
            AllowOverride None
            Options +ExecCGI -MultiViews +SymLinksIfOwnerMatch
            Require all granted
    </Directory>

    ErrorLog ${APACHE_LOG_DIR}/grsshopper-error.log
    CustomLog ${APACHE_LOG_DIR}/grsshopper-access.log combined

  </VirtualHost>
```

Don't forget to enable the new site:

  ```
  a2ensite grsshopper.conf
  ```

Enable Apache modules:

  ```
  a2enmod cgid rewrite
  ```

### gRSShopper code

Get gRSShopper code from GitHub:

  ```
  $ git clone https://github.com/temin/gRSShopper.git
  ```

Create website root folder:

  ```
  # mkdir /var/www/grsshopper
  ```

Synchronize the *cgi-bin* folder to the appropriate locations:

  ```
  rsync -av /path/to/git_repo_clone/grsshopper/cgi-bin /var/www/grsshopper
  ```

Synchronize the *html* folder to the appropriate locations:

  ```
  rsync -av /path/to/git_repo_clone/grsshopper/html/ /var/www/grsshopper
  ```

Create *cgi-bin* data root folder:

  ```
  mkdir /var/www/grsshopper/cgi-bin/data
  ```

Change files permissions (might need a little bit of restricting):

  ```
  chown -R www-data:www-data /var/www/grsshopper
  ```

### Prepare MariaDB/MySQL database

Create database

  ```mysql
  CREATE DATABASE grsshopper;
  ```

Create database user

  ```mysql
  GRANT ALL PRIVILEGES ON grsshopper.* TO grsshopper@localhost IDENTIFIED BY 'secret_password';
  ```

Import database

  ```
  $ mysql -u grsshopper -p grsshopper < /path/to/git_repo_clone/grsshopper/cgi-bin/sql/gRSShopper-ple.sql
  ```

Changed nameserver over to ns1.reclaimhosting.com   :)

In FTP Client or File Manager
- load cgi-bin files into ../public_html/cgi-bin
- load html files into ../public_html    
- make cgi-bin/data folder

In CPanel
- changed permissions of scripts to 0755
- run https://www.downes.ca/cgi-bin/server_test.cgi
    This tests the cgi installation. On different hosts you may need to install additional Perl modules

In CPanel/MySQL Databases:
- Create database
- Create database user   
- Add user to database with all privileges  (keep this information, you will need it to fill in the form below)

In PHPMyAdmin
- import grsshopper-ple.sql into database

Run http://www.downes.ca/cgi-bin/initialize.cgi
   and fill in the form

--------------------------------------------------------------------   

Some help with the form (*** means 'pick whatever you want'):

   Site document directory:    ../     

   Site cgi directory is:      ./



   Database Name			database name, from above

   Database Location			localhost

   Database Username	database user name, from above

   Database Password	database user password, from above

   Language				en

   Site Document Directory		/home/*******/public_html                 (needs to be full filename and directory)

   Site CGI Directory		/home/*******/public_html/cgi-bin


   Site Name				********

   Site Tag				  **********

  Site Email Address		*********

  Site Time Zone			America/Toronto

   License				CC-by-NC

   Site Key				**********                                             (take note of this, you need it to run cron)


   Administrator Username		**********                                   (You will use these to log into your gRSShopper PLE)

   Administrator Password		***********

- Click 'Multisite'

------------------------------------------------------------

- Remove initialize.cgi

- In ../public_html/assets/js/grsshopper_admin.js
   -- change www.downes.ca  to your new site URL (bit of a kludge here)

-----------

- Set up Cron (once a minute)
/home/********/public_html/cgi-bin/admin.cgi www.downes.ca ^^^^^^^^ /home/******/public_html/cgi-bin/data/multisite.txt >/dev/null 2>&1

-- where *********** is your directory
and ^^^^^^^^^^ is the site key entered in the form above

- To open the PLE, navigate to https://yourservername/cgi-bin/page.cgi?page=PLE&force=yes

(once you publish this page you can just go to https://yourservername/ple.htm  )
