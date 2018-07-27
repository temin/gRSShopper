#!/usr/bin/perl

#    gRSShopper 0.7  Server Test  0.2  -- gRSShopper server test module
#    26 April 2017 - Stephen Downes


#    Copyright (C) <2008>  <Stephen Downes, National Research Council Canada>

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

##########################################################################
# Servertest.pl
##########################################################################

# -----------------------------------------------------
# Check that all of the required modules can be located



$|++;
my $missing = 0;
use local::lib; # sets up a local lib at ~/perl5


# ---------------------------------
# Let's see what our environment is
  if (!$ENV{'SERVER_SOFTWARE'}) {
    $newline = "\n";
  }
  else {
    print "Content-type: text/html\n\n";
    $newline = "<br>";
   }

print "gRSShopper web server environment test.".$newline.$newline;



# --------------------------------------
# Check for the required version of PERL
  eval "require 5.004";
  print "Checking PERL version...";
  if ($@) {
    print "$newline"."This program requires at least PERL version 5.004 or greater.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }
# -------------
# Check for CGI
  print "Checking for CGI. This module handles form input functions.";
  eval "use CGI";
  if ($@) {
    print "$newline"."The CGI module could not be located.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }





# -------------
# Check for CGI::Carp
  print "Checking for CGI::Carp. This module displays error messages.";
  eval "use CGI::Carp";
  if ($@) {
    print "$newline"."The CGI::Carp module could not be located.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

# -------------
# Check for CGI::Session
  print "Checking for CGI::Session. This module manages sessions.";
  eval "use CGI::Session";
  if ($@) {
    print "$newline"."The CGI::Session module could not be located.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }
# -------------

# Check for File::Basename;
  print "Checking for File::Basename;. This module locates the script directory name.";
  eval "use File::Basename;";
  if ($@) {
    print "$newline"."The File::Basename; module could not be located.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }






# -------------
# Check for DBI
  print "Checking for DBI. This module handles database functions.";
  eval "use DBI";
  if ($@) {
    print "$newline"."The DBI module could not be located.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }


# -------------
# Check for LWP
  print "Checking for LWP. This module connects to other web servers.";
  eval "use LWP";
  if ($@) {
    print "$newline"."The LWP module could not be located.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }


# -------------
# Check for LWP::UserAgent
  print "Checking for LWP::UserAgent. This module emulates a web browser.";
  eval "use LWP::UserAgent";
  if ($@) {
    print "$newline"."The LWP::UserAgent module could not be located.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

# -------------
# Check for LWP::Simple
  print "Checking for LWP::Simple. This module emulates a web browser.";
  eval "use LWP::Simple";
  if ($@) {
    print "$newline"."The LWP::Simple module could not be located.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

# -------------
# Check for File::Basename
  print "Checking for File::Basename. This analyzes file names and is used for file uploads.";
  eval "use File::Basename";
  if ($@) {
    print "$newline"."The File::Basename module could not be located. Some admin functions may not work.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

# -------------
# Check for File::stat
  print "Checking for File::stat. This examines files and is used for file uploads.";
  eval "use File::stat";
  if ($@) {
    print "$newline"."The File::stat module could not be located. Some admin functions may not work.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

  # -------------
  # Check for File::Find
    print "Checking for File::Find. This finds old files in order to remove them.";
    eval "use File::Find";
    if ($@) {
      print "$newline"."The File::Find module could not be located. Unable to find old files in order to remove them.$newline";
      $missing=1;
    } else {
  	print " OK$newline";
    }

    # -------------

# Check for MIME::Types
  print "Checking for MIME::Types. This determines the file type of uploaded files";
  eval "use MIME::Types";
  if ($@) {
    print "$newline"."The MIME::Types module could not be located. Admin will not work properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

  # -------------

# Check for MIME::Types
print "Checking for MIME::Lite::TT::HTML. This formats email messages";
eval "use MIME::Lite::TT::HTML";
if ($@) {
  print "$newline"."The MIME::Lite::TT::HTML module could not be located. Admin will not work properly.$newline";
  $missing=1;
} else {
print " OK$newline";
}




 # -------------
# Check for HTML::Entities
  print "Checking for HTML::Entities. This encodes and decodes strings with HTML entities.";
  eval "use HTML::Entities";
  if ($@) {
    print "$newline"."The HTML::Entities module could not be located. Some admin functions may not work.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

 # -------------
# Check for Scalar::Util 'blessed'
  print "Checking for Scalar::Util 'blessed'. This is a set of useful utilities.";
  eval "use Scalar::Util 'blessed'";
  if ($@) {
    print "$newline"."The Scalar::Util 'blessed' module could not be located. Some admin functions may not work.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

   # -------------
# Check for Text::ParseWords
  print "Checking for Text::ParseWords. This is used to extract lists of words from strings (ignoring delimiters insider quotes)";
  eval "use Text::ParseWords";
  if ($@) {
    print "$newline"."The Text::ParseWords module could not be located. Some admin functions may not work.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }




   # -------------
# Check for Lingua::EN::Inflect
  print "Checking for Lingua::EN::Inflect. This converts words into their plural form (English)";
  eval "use Lingua::EN::Inflect";
  if ($@) {
    print "$newline"."The Lingua::EN::Inflect module could not be located. Some functions may not work.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

   # -------------






# Check for Net::Twitter::Lite::WithAPIv1_1
  print "Checking for Net::Twitter::Lite::WithAPIv1_1. This connects to Twitter and executes the new Twitter API";
  eval "use Net::Twitter::Lite::WithAPIv1_1";
  if ($@) {
    print "$newline"."The Net::Twitter::Lite::WithAPIv1_1 module could not be located. Twitter functions will not work.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

   # -------------

# Check for Image::Resize
  print "Checking for Image::Resize. This contains a library opf image processing utilities";
  eval "use Image::Resize";
  if ($@) {
    print "$newline"."The Image::Resize module could not be located. Icons will not be created.$newline";
    $missing=1;
  } else {
	print " OK$newline";
	# &test_thumbnails();


  }

   # -------------

# Check for DateTime
  print "Checking for DateTime. This converts dates and times";
  eval "use DateTime";
  if ($@) {
    print "$newline"."The DateTime module could not be located. Many date functions will not work properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

   # -------------

# Check for DateTime::TimeZone
  print "Checking for DateTime::TimeZone. This manages time zone conversions";
  eval "use DateTime::TimeZone";
  if ($@) {
    print "$newline"."The DateTime::TimeZone module could not be located. Time zone conversions will not work properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }


   # -------------

# Check for Time::Local
  print "Checking for Time::Local. This manages local time";
  eval "use Time::Local";
  if ($@) {
    print "$newline"."The Time::Local module could not be located. Local time might not function properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }


   # -------------

# Check for Time::Local
  print "Checking for Digest::SHA1 qw/sha1 sha1_hex sha1_base64/. This excrypts passwords and access tokens";
  eval "use Digest::SHA1 qw/sha1 sha1_hex sha1_base64/";
  if ($@) {
    print "$newline"."The Digest::SHA1 qw/sha1 sha1_hex sha1_base64/ module could not be located. Passwords and access tokens will not work properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }


  # -------------

# Check for XML::OPML
 print "Checking for XML::OPML. This imports lists of RSS files (ie., OPML files)";
 eval "use XML::OPML";
 if ($@) {
   print "$newline"."The XML::OPML module could not be located. OPML Import will not work properly.$newline";
   $missing=1;
 } else {
 print " OK$newline";
 }


   # -------------

# Check for REST::Client
  print "Checking for REST::Client. This proivides API Access";
  eval "use REST::Client";
  if ($@) {
    print "$newline"."The REST::Client module could not be located. Passwords and access tokens will not work properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

   # -------------

# Check for JSON
  print "Checking for JSON. This creates and reads Javascript Onbject Notation";
  eval "use JSON";
  if ($@) {
    print "$newline"."The JSON module could not be located. Passwords and access tokens will not work properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

  # -------------

# Check for JSON::Parse
 print "Checking for JSON::Parse 'parse_json'. This parses Javascript Object Notation";
 eval "use JSON::Parse 'parse_json'";
 if ($@) {
   print "$newline"."The JSON::Parse 'parse_json' module could not be located. Passwords and access tokens will not work properly.$newline";
   $missing=1;
 } else {
 print " OK$newline";
 }

 # -------------

# Check for JSON::XS
print "Checking for JSON::XS. This works with Javascript Object Notation";
eval "use JSON::XS";
if ($@) {
  print "$newline"."The JSON::XS module could not be located. Passwords and access tokens will not work properly.$newline";
  $missing=1;
} else {
print " OK$newline";
}


   # -------------

# Check for Facebook
  print "Checking for Facebook::Graph. This interoperates with Facebook";
  eval "use Facebook::Graph";
  if ($@) {
    print "$newline"."The Facebook::Graph module could not be located. Passwords and access tokens will not work properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

   # -------------

  print "Checking for Net::Facebook::Oauth2. This provides Facebook authentication";
  eval "use Net::Facebook::Oauth2";
  if ($@) {
    print "$newline"."The Net::Facebook::Oauth2 module could not be located. Passwords and access tokens will not work properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }





   # -------------

# Check for URI::Escape
  print "Checking for URI::Escape. This creates escaped versions of URIs";
  eval "use URI::Escape";
  if ($@) {
    print "$newline"."The URI::Escape module could not be located. Passwords and access tokens will not work properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }


   # -------------

# Check for Email::Stuffer
  print "Checking for Email::Stuffer. This formats email messages";
  eval "use Email::Stuffer";
  if ($@) {
    print "$newline"."The Email::Stuffer module could not be located. Email will not send properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }

   # -------------


# Check for Email::Sender::Transport::SMTP
  print "Checking for Email::Sender::Transport::SMTP. This sends email messages";
  eval "use Email::Sender::Transport::SMTP";
  if ($@) {
    print "$newline"."The Email::Sender::Transport::SMTP module could not be located. Email will not send properly.$newline";
    $missing=1;
  } else {
	print " OK$newline";
  }




# -------------
# Provide CPAN help

if ($missing eq "1") {

	print qq|$newline You are missing at least one required Perl module.
		$newline$newline
		There are two ways to get your module. You can either use the 'cpan'
		command, or you can download the module and install it manually.
		We recommend you try the cpan command first. $newline $newline
		Note that either way you must have root (system administrator)
		access to install the module. If you do not have access, request
		that your administrator make the installation for you. $newline
		$newline To start CPAN, type: $newline $newline
		perl -MCPAN -e shell $newline $newline
		If this is the first time you've run CPAN, it's going to ask
		you a series of questions - in most cases the default answer
		is fine. Then, once you see the cpan> prompt, type 'install'
		and your module name. For example:$newline $newline
		cpan> install LWP::UserAgent$newline $newline
		For more information, please see:
		http://www.cpan.org/modules/INSTALL.html $newline
		http://www.rcbowen.com/imho/perl/modules.html $newline|;

}



exit;




sub send_email {

	my $Mailprog = "/usr/sbin/sendmail";


	my ($to,$from,$subj,$page,$Mailprog) = @_;


         open (MAIL,"|$Mailprog -t") or print "Can't find email program $Mailprog";




						# Set Line Lengths

		print "Test Email: <p><pre>";
		print "To: $to\nFrom: $from\nSubject: $subj\n$htmlstr\n\n$page"
			or print "Email format error: $!";
		print MAIL "To: $to\nFrom: $from\nSubject: $subj\n$htmlstr\n\n$page"
			or print "Email format error: $!";
		print "</pre>";



	close MAIL;

}

sub test_thumbnails {


print "Testing thumbnails<p>";
        # Create a thumbnail from 'test.jpg' as 'test_t.jpg'
        # using ImageMagick, Imager, GD or Image::Epeg.
        my $t = new Image::Thumbnail(
                module     => "Image::Magick",
                size       => 55,
                create     => 1,
                input      => "/var/www/cgi-bin/test.jpg",
                outputpath => "/var/www/cgi-bin/Riga001_t.jpg",
                CHAT => 1
        ) or print "Error: $!";

        print $t->{error};
        print $t->{warning};
                print $t->{module};
                        print $t->{thumb};

print "OK";
}
