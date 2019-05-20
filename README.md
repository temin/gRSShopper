gRSShopper
==========

This is a clone of [Stephen Downes'](https://www.downes.ca/) Personal Learning Environments (PLE) [gRSShopper](https://github.com/Downes/gRSShopper).

This clone contains few fixes and improvements that enabled me to install gRSShopper on [vanilla](https://en.wikipedia.org/wiki/Vanilla_software) Debian/Ubuntu server. Some fixes also originate from the comments Downes made in his [Installing gRSShopper on Reclaim](https://www.youtube.com/watch?v=T8PFEEQJ8kw) video.

Installation on Debian/Ubuntu
-------------------------------

### Ansible playbook

If you are familiar with Ansible you can use my [playbook](https://github.com/temin/ansible-grsshopper) to install gRSShopper.


### Installing software manualy

gRSShopper is a LAMP (P as Perl) application and the base packages to install are:

  ```
  # apt install apache2 libapache2-mod-perl2 mariadb-server python-mysqldb rsync cpanminus dh-make-perl
  ```

Optional: Install Git to get/manage gRSShopper files. You can do the same by downloading ZIP file from GitHub.

  ```
  # apt install git
  ```

gRSShopper requires the following modules to be installed:

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

NOTE: I was unable to build *Mastodon::Client* on Debian (8 & 9) and Ubuntu (16 & 18). As I will not be using Mastodon, I've created the [**no_mastodon**](https://github.com/temin/gRSShopper/tree/no_mastodon) branch with Mastodon code removed.

NOTE: Different Debian/Ubuntu versions have different Perl modules available in the repositories. The above lists of Perl module packages are valid for Debian 9. For other versions check [INSTALL_versions](./INSTALL_versions.md).


### Apache config

Add or change Apache virtual host configuration file (e.g. `/etc/apache2/sites-available/grsshopper.conf`):

```apache
  <VirtualHost *:80>

    ServerName grsshopper.example.org

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

Don't forget to enable the new site (if you created one):

  ```
  a2ensite grsshopper.conf
  ```

Enable Apache modules:

  ```
  a2enmod cgid rewrite
  ```

In the end, don't forget to restart Apache service `systemctl restart apache2`.

### gRSShopper code

Get gRSShopper code from GitHub:

  ```
  $ git clone https://github.com/temin/gRSShopper.git
  ```

Create website root folder:

  ```
  # mkdir /var/www/grsshopper
  ```

Synchronize the *cgi-bin* folder to the appropriate location:

  ```
  rsync -av /path/to/git_repo_clone/grsshopper/cgi-bin /var/www/grsshopper
  ```

Synchronize the *html* folder to the appropriate location:

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

Create *perl5* folder and allow user *www-data* to modify it:

  ```
  mkdir /var/www/perl5
  chown -R www-data:www-data /var/www/perl5
  ```

### Prepare MariaDB/MySQL database

Create database:

  ```mysql
  CREATE DATABASE grsshopper;
  ```

Create database user:

  ```mysql
  GRANT ALL PRIVILEGES ON grsshopper.* TO grsshopper@localhost IDENTIFIED BY 'secret_password';
  ```

Import database

  ```
  $ mysql -u grsshopper -p grsshopper < /path/to/git_repo_clone/grsshopper/cgi-bin/sql/gRSShopper-ple.sql
  ```

### Test installation

Open `https://grsshopper.example.org/cgi-bin/server_test.cgi` URL in browser to check if all the required modules are properly installed.

### Initialize gRSShopper

Open `https://grsshopper.example.org/cgi-bin/initialize.cgi` URL in browser and fill in the form. For explanation check [Installing gRSShopper on Reclaim](https://www.youtube.com/watch?v=T8PFEEQJ8kw?t=2366) video.


Remove `initialize.cgi` file from web server.

Edit `/var/www/grsshopper/assets/js/grsshopper_admin.js` file. Enter the correct URL on the first line.

### Set up Cron (once a minute):

  ```cron
  * * * * www-data /usr/bin/perl "/var/www/grsshopper/cgi-bin/admin.cgi grsshopper.example.org site_key /var/www/grsshopper/cgi-bin/data/multisite.txt" > /dev/null 2>&1
  ```

To open the PLE, navigate to https://grsshopper.example.org/cgi-bin/page.cgi?page=PLE&force=yes

(once you publish this page you can just go to https://grsshopper.example.org/ple.htm  )
