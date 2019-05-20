Installing gRSShopper
=====================

Debian 8
--------

Modules available in repositories:

  ```
  apt install libmime-types-perl libcgi-session-perl liblingua-en-inflect-perl libjson-perl libjson-xs-perl libnet-facebook-oauth2-perl libxml-opml-perl libnet-twitter-lite-perl libdigest-sha-perl libtext-vcard-perl libnet-oauth-perl libdbd-mysql-perl libgd-perl libapache2-mod-perl2 liblocal-lib-perl
  ```

Build remaining modules with `cpanm`:

  ```
  # cpanm MIME::Lite::TT::HTML
  # cpanm REST::Client
  # cpanm Email::Stuffer
  # cpanm Image::Resize
  # cpanm Digest::SHA1
  # cpanm JSON::Parse
  # cpanm Mastodon::Client
  ```


Ubuntu 14
---------

Ubuntu 16
---------

Ubuntu 18
---------


