#!/usr/bin/perl

#    gRSShopper 0.7  Page  0.7  -- gRSShopper submit form
#    11 October 2018 - Stephen Downes

#    Copyright (C) <2018>  <Stephen Downes, National Research Council Canada>
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
#
#-------------------------------------------------------------------------------
#
#	    gRSShopper
#           Submit Script
#
#-------------------------------------------------------------------------------



# Load CGI

	use CGI;
	use CGI::Carp qw(fatalsToBrowser);
	my $query = new CGI;
	my $vars = $query->Vars;
	my $page_dir = "../";


# Load gRSShopper

	use File::Basename;
      use local::lib; # sets up a local lib at ~/perl5
	my $dirname = dirname(__FILE__);
	require $dirname . "/grsshopper.pl";

# Load modules

	our ($query,$vars) = &load_modules("page");


# Load Site

	our ($Site,$dbh) = &get_site("page");
	if ($vars->{context} eq "cron") { $Site->{context} = "cron"; }

# Get Person  (still need to make this an object)

	our $Person = {}; bless $Person;
	&get_person($dbh,$query,$Person);
	my $person_id = $Person->{person_id};

# Initialize system variables

	my $options = {}; bless $options;
	our $cache = {}; bless $cache;


  my $action = $vars->{action};
  my $table = "feed";    # For now
  my $id = "new";  # This script creates records, but doesn't edit records




# Determine Output Format  ( assumes admin.cgi?format=$format )

if ($vars->{format}) { 	$format = $vars->{format};  }
if ($action eq "list") { $format = "list"; }
$format ||= "html";		# Default to HTML


unless ($table && $action) {				# Print Form

	print "Content-type: text/html; charset=utf-8\n\n";
  print qq|
     <form action="submit.cgi" method="post">
     <input type="hidden" name="table" value="feed">
     <input type="hidden" name="id" value="new">
     Please enter your blog or feed information below:<br>
     <input type=text size=80 name="title" placeholder="Feed or blog Title"><br>
     <input type=text size=80 name="url" placeholder="Feed or blog URL"><br>
     <input type=text size=80 name="author" placeholder="Your Name"><br>
     <input type="submit" name="action" value="Submit">
     </form>|;
	exit;
}





# Actions ------------------------------------------------------------------------------


if ($action) {						# Perform Action, or


	for ($action) {

		/Submit/ && do {
	   	print "Content-type: text/html; charset=utf-8\n\n";
			my $id = &form_update_submit_data($dbh,$query,$table,$id);
      if ($id) { print "Thank you, your $table has been submitted.<br>"}
      else { print "Sorry, I tried but I failed.<br>"}
      last;

    	};


							# Go to Home Page
		if ($dbh) { $dbh->disconnect; }			# Close Database and Exit
		print "Content-type: text/html; charset=utf-8\n";
		print "Location:".$Site->{st_url}."\n\n";
		exit;

	}
}



if ($dbh) { $dbh->disconnect; }			# Close Database and Exit
print "Content-type: text/html; charset=utf-8\n";
print "Location:".$Site->{st_url}."\n\n";

exit;



1;
