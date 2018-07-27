gRSShopper

by Stephen Downes

gRSShopper is a tool that aggregates, organizes and distributes resources to support online learning



--------------------------------------------------
Installation - works for CPanel on Reclaim Hosting
--------------------------------------------------

In CPanel, Install Perl Modules:

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
- import grsshopper_personal.sql into database

Run http://www.downes.ca/cgi-bin/initialize.cgi?action=file
   and fill in the form
   
--------------------------------------------------------------------   
   Some help with the form (*** means 'pick whatever you want'):

   Site document directory:    ../     
   Site cgi directory is:      ./
   Admin Username			***********
   Admin Password			***********
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
   Administrator Username		**********
   Administrator Password		***********
	
   Click 'Multisite'
------------------------------------------------------------

Remove initialize.cgi

In ../public_html/assets/js/grsshopper_admin.js
   change www.downes.ca  to your new site URL (bit of a kludge here)

-----------

Set up Cron (once a minute)
/home/********/public_html/cgi-bin/admin.cgi www.downes.ca ^^^^^^^^ /home/******/public_html/cgi-bin/data/multisite.txt >/dev/null 2>&1 

where *********** is your directory
and ^^^^^^^^^^ is the site key entered in the form above

