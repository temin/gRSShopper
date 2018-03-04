#!/usr/bin/env perl



#    gRSShopper 0.7  Harvester  0.6  -- gRSShopper harvester module
#    04 March 2018 - Stephen Downes

#    Copyright (C) <2011>  <Stephen Downes, National Research Council Canada>
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

#-------------------------------------------------------------------------------
#
#	    gRSShopper
#           Harvester
#
#-------------------------------------------------------------------------------


  use strict;

  print "Content-type: text/html; charset=utf-8\n\n";
  use CGI::Carp qw(warningsToBrowser fatalsToBrowser);
  our $DEBUG = 1;							# Toggle debug

# Forbid bots

	die "HTTP/1.1 403 Forbidden\n\n403 Forbidden\n" if ($ENV{'HTTP_USER_AGENT'} =~ /bot|slurp|spider/);

# Load gRSShopper

	use File::Basename;
	use CGI::Carp qw(fatalsToBrowser);
	my $dirname = dirname(__FILE__);
	require $dirname . "/grsshopper.pl";

# Load modules

	our ($query,$vars) = &load_modules("admin");
	$vars->{msg} = "Messages<p>";

# Load Site

	our ($Site,$dbh) = &get_site("admin");
	if ($vars->{context} eq "cron") { $Site->{context} = "cron"; }
	our $analyze = $vars->{analyze};
	$Site->{diag_level} = 1;
	if ($vars->{diag_level} && $vars->{analyze} eq "on") { $Site->{diag_level} = $vars->{diag_level}; }
  &diag(1,&harvester_stylsheet());
  &diag(1,"<h1><center>gRSShopper HARVESTER</h1>\n\n");

# Get Person  (still need to make this an object)

	our $Person = {}; bless $Person;
	&get_person($dbh,$query,$Person);
	my $person_id = $Person->{person_id};

# Initialize system variables

	my $options = {}; bless $options;
	our $cache = {}; bless $cache;

# Restrict to Admin

	if ($vars->{context} eq "cron") {
		$vars->{action} = $ARGV[2];
	} else {
		&admin_only();
	}


# Analyze Request --------------------------------------------------------------------

	my $format; my $action;
	# while (my($vx,$vy) = each %$vars) { print "$vx = $vy <br>"; }

	$action = $vars->{action} || "none";		# Determine Action
	if ($vars->{feed}) { $action = "harvest"; }
	if ($vars->{source} eq "queue") { $action = "queue"; }
	$vars->{format} ||= "html";			# Determine Output Format


	&diag(1,qq|<hr><div class ="main">Action: <b>$action</b>.\n\n|);
	if ($analyze eq "on") { &diag(1,"Analyzing only; no data will be saved. Analysis Level: $vars->{diag_level}<p>"); }
	&diag(1,qq|</div>|);

	# Don't keep big MP3s, they'll just fill up the hard drive
	&clean_podcast_directory($Site->{st_urlf}."files/podaudio",30);

	for ($action) {					# There is always an action

		/queue/ && do { &harvest_queue(); last; 		};
		/harvest/ && do { &harvest_feed($vars->{feed}); last; };
		/url/ && do { &harvest_url($vars->{url}); last; };
		/export/ && do { &export_opml($dbh,$query); last;	};
		/import/ && do { &import_opml($dbh,$query); last;	};
		/opmlopts/ && do { &opmlopts($dbh,$query); last;	};

		# If no $action Go to Home Page
		&diag(1,qq|<div class ="harvester warning">Harvester OK. For action use parameter ?action=<i>action</i><div>\n|);
		exit;
	}

	if ($dbh) { $dbh->disconnect; }		# Close Database and Exit
	exit;



# -------   Harvest Queue ------------------------------------------------------

# Harvests the next feed in the queue. Used by Cron

sub harvest_queue {

  #	my () = @_;
	&diag(2,qq|<div class="function">Harvest  Queue<div class="info">|);

	# Find next feedid in queue
	my $stmt = "SELECT feed_id FROM feed WHERE feed_link <>'' AND (feed_status = 'A' OR feed_status = 'Published') ORDER BY feed_lastharvest LIMIT 0,1";
	my $next = $dbh->selectrow_hashref($stmt);
	my $feedid = $next->{feed_id};

  # If found, Harvest Feed
	if ($next->{feed_id}) {
	  &diag(2,qq|Next in queue is feed number $feedid<br>\n\n|);
		&harvest_feed($feedid);
	} else {
    &diag(2,qq|<div class="harvestererror">Cannot find next feedid in queue</div>|);
		return;

	}

  # Done
	&diag(2,qq|</div></div>\n\n|);
	return $next->{feed_id};

}


# -------   Harvest Feed ------------------------------------------------------

# Harvests feed specified on input

sub harvest_feed {

	my ($feedid) = @_; 	my $now = time;
	&diag(2,qq|<div class="function">Harvest Feed<div class="info">|);
	&diag(2,qq|Feed ID: $feedid; \n\n|);

	# Get Feed Data (Return if not found)
	my $feedrecord = gRSShopper::Feed->new({dbh=>$dbh,id=>$feedid});
  &diag(2,qq|Feed Title: |.$feedrecord->{feed_title}.qq| <br>\n\n|);
	unless ($feedrecord) {
		&diag(2,qq|<div class="harvestererror">Could not find a record for feed number $feedid</div>|);
		return;
	}

	# Display Feed Record Data
	my $rep = "<b>Feed Record</b><br>";
	while (my($fx,$fy) = each %$feedrecord) { if ($fy) { $rep .= qq|$fx = $fy <br>\n|; } }
	&diag(4,qq|<div class="data">$rep</div>\n\n|);
  # &send_email("stephen\@downes.ca","stephen\@downes.ca","$feedrecord->{feed_title}",$rep);


  # Perform The Harvest, storing data into $feedrecord->{feedstring}
	$feedrecord->{crdate} = time;

	# Harvest Twitter
	if ($feedrecord->{feed_type} =~ /twitter/i) {
		require $Site->{cgif}."harvest/harvest_twitter.pl";
		&harvest_twitter($feedrecord);

	# Harvest Facebook
	} elsif ($feedrecord->{feed_type} =~ /facebook/i){
		require $Site->{cgif}."harvest/harvest_twitter.pl";
		&harvest_facebook($feedrecord);

	# Harvest URL
	} else {
		&get_url($feedrecord,$feedid);
	}

	# Update last harvest date
	if ($feedrecord->{feedstring}) {
	   unless ( $analyze eq "on") {
			 &diag(3,qq|<div class="detail">Feed $feedid lastharvest updated to $now</div>\n\n|);
	   	 unless ($analyze eq "on") { &db_update($dbh,"feed",{feed_lastharvest=>$now},$feedid); }
		 }
  } else {
		 &diag(2,qq|<div class="harvestererror">Could not retrieve data for $feedid</div>|);
	}

	# Process Data
	&harvest_process_data($feedrecord);

	&diag(2,qq|Havest feed done.\n\n|);
	&diag(2,qq|</div></div>\n\n|);

	return;
}



# -------   Harvest: Process Data ------------------------------------------------------

sub harvest_process_data {

	my ($feedrecord) = @_;
	&diag(2,qq|<div class="function">Harvest Process Data<div class="info">|);
	&diag(2,qq|Feed type:|.$feedrecord->{feed_type}."<br>");

	#&send_email("stephen\@downes.ca","stephen\@downes.ca","Processing Data",$feedrecord->{feedstring});

  # JSON
	if ($feedrecord->{feed_type} =~ /json|facebook/i) {
		&diag(1,"Feed is JSON<br>\n");
		require $Site->{cgif}."harvest/parse_json.pl";
		&parse_json($feedrecord);

	# VCALENDAR
	} elsif ($feedrecord->{feedstring} =~ /^BEGIN:VCALENDAR/) {
		require $Site->{cgif}."harvest/parse_vcal.pl";
		&diag(1,"Feed is vcalendar, ick<br>\n");
		return;

	# RSS / ATOM
	} elsif ($feedrecord->{feedstring} =~ /<rss|<feed/i) {
		require $Site->{cgif}."harvest/parse_feed.pl";
		&diag(1,"Harvesting RSS/Atom feed.<br>\n");
		&parse_feed($feedrecord);

	# Fail
	} else {
		&diag(1,"Harvest failed for some reason.<br>\n");
		&diag(1,qq|<div class="data"><form><textarea cols=80 rows=20>$feedrecord->{feedstring}</textarea></form></div>\n|);
		return;
	}

  require $Site->{cgif}."harvest/scraper.pl";
	&scrape_items($feedrecord);

	&clean_feed_input($feedrecord);

  require $Site->{cgif}."harvest/rules.pl";
  require $Site->{cgif}."harvest/save_feed.pl";
  &save_records($feedrecord);


	#&post_processing($feed);
	#&diag(9,"<form><textarea cols=140 rows=80>".$feed->{feedstring}."</textarea><form>");
#my $file = "/var/www/feeds/feeds.feedburner.com_wordpress_ACyV_format_xml";

#my $last = (stat($file))[9];


#$feed->{feedstring} = &get_file($file);
	&diag(2,qq|Process Data done.\n\n|);
	&diag(2,qq|</div></div>\n\n|);
	return;
}






#------------------------  Process CDATA
#
# Stores all instances of ![CDATA[]] in an array, Replaces with a numerical value which is the index of the awway
# Used in:
#  parse_feed.pl
#
#------------------------------------------------------------

sub process_cdata {


	my ($feed) = @_;
	&diag(8,qq|<div class="function">Process CDATA<div class="data">|);

	my $cdatacounter = 0;
	while ($feed->{feedstring} =~ s/<!\[CDATA\[(.*?)\]\]>/CDATA($cdatacounter)/ms) {
		$feed->{cdata}->[$cdatacounter] = "$1";
    &diag(8,qq|CDATA $cdatacounter: <form><textarea cols=80 rows=3>$1</textarea></form><br>|);
		$cdatacounter++;
	}
	&diag(8,qq|</div></div>|);

}


#------------------------- Replace CData -----------------------------------
#
#  Replaces CDATA extracted and stored by Process CDATA
#
# Used in:
#  save_feed.pl
#  scraper.pl
#------------------------------------------------------------


sub replace_cdata {

	my ($feedrecord,$record) = @_;
	&diag(3,qq|<div class="function">Replace CDATA<div class="info">|);
	&diag(3,"Replacing CDATA in $record->{type}<br>\n");


	while (my ($ix,$iy) = each %$record) {
    next if ($ix eq "feedstring");
		if ( $record->{$ix} =~ /CDATA\((.*?)\)/ ) {

			 &diag(3,qq|Replacing CDATA in $ix: <form><textarea cols=80 rows=3>|.$record->{$ix}.qq|</textarea></form><br>|);
		   $record->{$ix} =~ s/CDATA\((.*?)\)/$feedrecord->{cdata}->[$1]/msg;
		   &diag(3,qq|Replacement: <form><textarea cols=80 rows=3>|.$record->{$ix}.qq|</textarea></form><br>|);
	  }
	}

	&diag(3,qq|</div></div>|);
}







#------------------------  Process URL  --------------------
# Used in:
#  parse_feed.pl
#  tags.pl
#------------------------------------------------------------


sub process_url {

	my ($url) = @_;

	$url =~ s/utm=(.*?)$//;				# Wipe out utm parameters

	if ($url eq "http://www.cbc.ca/podcasting") { $url = $url . "#".$vars->{linecount}; }
	return $url;


}

#------------------------  Append to List  ------------------------------

# Some elements (eg. link_category) may consist of multiple items
# these are sorted as a string with ; as a delimiter for list items
# Does not add duplicate items
# Used in:
#  harvest.pl
#  save_feed.pl
#  tags.pl
#
#-----------------------------------------------------------------------

sub append_to_list {

	my ($list,$item) = @_;
	$item =~ s/\s*$//g;		# Nuke trailing white space
	my @listitems = split /;/,$list;
	foreach my $li (@listitems) { return if ($li eq $item); } # No duplicates
	if ($list) { $list .= ";"; }
	$list .= $item;
	return $list;


}



#------------------------  Clean Feed Input --------------------

sub clean_feed_input {
	my ($feedrecord) = @_;
	&diag(5,qq|<div class="function">Clean Feed Input<div class="info">|);
	my $feed = $feedrecord->{processed};
	unless ($feed->{items}) {
		&diag(0,"Feed has no items<br>\n");
		return;
	}
	my @items = @{$feed->{items}};

	foreach my $item (@items) {

		my $type = "link";



#	my $description = &replace_cdata($item->{$type."_description"});
#	my $content = &replace_cdata($item->{$type."_content"});
#	my $summary = &replace_cdata($item->{$type."_summary"});

	# Remove HTML, preserving some formatting


		&strip_html(\$item->{$type."_description"});
		&strip_html(\$item->{$type."_description"});
		&strip_html(\$item->{$type."_description"});
	}
	&diag(5,qq|</div></div>|);
}




#------------------------  Post Processing --------------------
#
#   Doesn't actually do anything, but if diag_level = 9
#   it prints out a nice version of the processed feed
#   as discovered by the harvester
#
#---------------------------------------------------------------

sub post_processing {

	my ($feedrecord) = @_;
	&diag(5,qq|<div class="function">Post Processing<div class="info">|);

	my $feed = $feedrecord->{processed};
	my @items = @{$feed->{items}};
	&diag(5,"<hr> POST PROCESS <hr>\n\n");

	# Feed elements
	while (my ($fx,$fy) = each %$feed) {
		next if &detect_object($fx);
		if ($fy) { &diag(9," -- $fx = $fy <br>\n"); }
	}

	# Feed authors
	while (my ($fx,$fy) = each %$feed) {
		if ($fx eq "authors") {
			foreach my $author (@$fy) {
				&diag(5,"Author: $author->{author_name}<br>\n");
				while (my ($ax,$ay) = each %$author) {
					if ($ay) { &diag(9," -- -- $ax = $ay <br>\n"); }
				}
			}
		}
	}

	# Feed media
	while (my ($fx,$fy) = each %$feed) {
		if ($fx eq "media") {
			foreach my $media (@$fy) {
				&diag(5,"Media: $media->{media_title}");
				while (my ($mx,$my) = each %$media) {
					if ($my) { &diag(9," -- -- $mx = $my <br>\n"); }
				}
			}
		}
	}


	# Feed Items

	while (my ($fx,$fy) = each %$feed) {
		if ($fx eq "items") {

			foreach my $item (@$fy) {
				&diag(3,qq|Item: <a href="$item->{link_link}">$item->{link_title}</a><br>\n|);

				# Item Elements
				while (my ($ix,$iy) = each %$item) {
					next unless ($ix =~ /link_/);

					next if ($ix =~ /description/ || $ix =~ /content/);
					&diag(9," -- $ix = $iy <br>\n");
				}

				# Feed Authors
				foreach my $author (@{$item->{authors}}) {
					&diag(5,"<br>-- AUTHOR: $author->{author_title} , $author->{author_name}<br>\n");
					while (my ($ax,$ay) = each %$author) {
						if ($ay) { &diag(9," -- -- $ax = $ay <br>\n"); }
					}
				}

				# Item Media
				foreach my $media (@{$item->{media}}) {
#					next unless (&is_url($feed,$media->{media_url}));			# punt gravatar
					&diag(5,"<br>-- MEDIA: $media->{media_title}<br>\n");
					while (my ($mx,$my) = each %$media) {
						if ($my) { &diag(9," -- -- $mx = $my <br>\n"); }
					}
				}


				# Item Links
				foreach my $link (@{$item->{links}}) {
#					next unless (&is_url($feed,$link->{link_link}));			# punt gravatar
					&diag(5,"<br>-- LINK: $link->{link_title}<br>\n");
					while (my ($lx,$ly) = each %$link) {
						if ($ly) { &diag(9," -- -- $lx = $ly <br>\n"); }
					}
				}
			}
		}
	}
	&diag(5,qq|</div></div>|);
}




sub clean_podcast_directory {

	my ($cleandir,$days) = @_;

	return if ($cleandir =~ /cgi/);


	use File::Find;
	&diag(5,qq|<div class="function">Clean Podcast Directory<div class="info">|);
	&diag(5,qq|Directory: : $cleandir <br>|);



	# purge backups older than AGE in days
	my @file_list;
	my @find_dirs       = ($cleandir);           # directories to search
	my $now             = time();                   # get current time
	my $seconds_per_day = 60*60*24;                 # seconds in a day
	my $AGE             = $days*$seconds_per_day;   # age in seconds
	find ( sub {
		my $file = $File::Find::name;
		if ( -f $file ) {
			push (@file_list, $file);
		}
	}, @find_dirs);

	for my $file (@file_list) {

		my @stats = stat($file);
		if ($now-$stats[9] > $AGE) {
			unlink $file;
		}
	}
	&diag(5,qq|Deleted podcast audio files older than $days days.\n\n|);
	&diag(5,qq|</div></div>\n\n|);

}

#  OPML Functions

	# ------------------------------------------------------------------------------
	#
	#                      OPML Functions
	#
	#---------------------------------------------------------------------------------
	#
	#
	# -------   Export OPML ------------------------------------------------------

sub export_opml {

	my ($dbh,$query) = @_;
	my $vars = $query->Vars;

						# Load OPML Module
	&error($dbh,"","",$vars->{error}) unless (&new_module_load($query,"XML::OPML"));

						# Create an OPML File Shell
	my $opml = new XML::OPML(version => "1.1");
	my $date = &rfc822_date(time);

						# Create the Head
	$opml->head(
						 title => $Site->{st_name}." OPML",
						 dateCreated => $date,
						 dateModified => $date,
						 ownerName => $Site->{st_pub},
						 ownerEmail => $Site->{em_from},
						 expansionState => '',
						 vertScrollState => '',
						 windowTop => '',
						 windowLeft => '',
						 windowBottom => '',
						 windowRight => '',
					 );

						# Insert Feeds
	my $stmt = "SELECT * FROM feed WHERE feed_status = 'A' AND feed_link <> ''";
	my $sth = $dbh->prepare($stmt);
	$sth->execute();
	while (my $feed_record = $sth->fetchrow_hashref()) {

		# XML::OPML doesn't properly escape yet
		$feed_record->{feed_description} =~ s/&/&amp;/mig;
		$feed_record->{feed_title} =~ s/&/&amp;/mig;
		$feed_record->{feed_description} =~ s/"/&quot;/mig;
		$feed_record->{feed_title} =~ s/"/&quot;/mig;
		$opml->add_outline(
						text => $feed_record->{feed_title},
						description => $feed_record->{feed_description},
									title => $feed_record->{feed_title},
									type => $feed_record->{feed_type},
									version => $feed_record->{feed_type},
									htmlUrl => $feed_record->{feed_html},
									xmlUrl => $feed_record->{feed_link},
							 );

	}

	my $filename = $Site->{st_urlf} . "feeds.xml";
	my $fileurl = $Site->{st_url} . "feeds.xml";
	$opml->save($filename);

	if ($vars->{format} eq "opml") {
		print $opml->as_string(); return $fileurl;
	} elsif ($vars->{internal} eq "import") {
			return $fileurl;
	} else {
  	my $output = qq|
				 <h2>Export OPML</h2>
				 Your OPML file has been created and saved to<br/>
				 <a href="$fileurl">$fileurl</a>\n|;
	  &admin_frame($dbh,$query,"Export OPML",$output);					# Print Output

	  return $fileurl;
  }

}

   # -------   OPML Opts -------------------------------------------------------

sub opmlopts {

						# Load OPML Module
	&error($dbh,"","",$vars->{error}) unless (&new_module_load($query,"XML::OPML"));

	my $output = qq|
		<h2>Import OPML</h2><p>An OPML file is a list of feeds used
		by an aggregator. You can import an OPML file and use this as
		a list of feeds to aggregate here.</p>
		<p>Please use caution as these actions cannot be undone. We
		recommend that you export your current OPML file and save it
		before importing any OPML file.</p>
		<p><a href="|.$Site->{st_cgi}.qq|harvest.cgi?action=export">Export
		OPML File</a></p>
		<form method="post" enctype="multipart/form-data" action="|.$Site->{st_cgi}.qq|harvest.cgi">
		<input type="hidden" name="action" value="import">
	  <ul>
		<li>Select an OPML file from your own computer to upload:<br>
	  <input type="file" name="OPMLfile" id="OPMLfile"></li>

		<li>Or enter the URL of the OPML file to be harvested and submit:<br>
		<input name="OPMLurl" type="text" size="60"></li>
	  </ul>

		<input type="submit" value="Upload OPML File"></form></p>
	|;
		  &admin_frame($dbh,$query,"Import OPML",$output);					# Print Output
}
  # -------   Import OPML ------------------------------------------------------

sub import_opml {

	my ($dbh,$query) = @_;
	my $vars = $query->Vars;

	if ($vars->{OPMLurl}) { &import_opml_url($dbh,$query); }
	elsif ($vars->{OPMLfile}) { &import_opml_file($dbh,$query); }
  else { &error($dbh,$query,"","No URL specified for import"); exit; }

}

sub import_opml_file {

	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	my $opml; my $file = &upload_file("OPMLfile");
	open (FH, $file->{fullfilename});
  while (<FH>) {  $opml .= $_;  }
	parse_input_opml($dbh,$query,$opml);

}


sub import_opml_url {

	my ($dbh,$query) = @_;
	my $vars = $query->Vars;

	unless ($vars->{OPMLurl})  { &error($dbh,$query,"","No URL specified for import"); 	}


						# Get OPML file from URL

	my $browser = LWP::UserAgent->new;
	my $page = $browser->get($vars->{url});
	&error($dbh,$query,"","Error: ", $page->status_line) unless $page->is_success;
	&error($dbh,$query,"","Error: ", "No content found in $vars->{url} ") unless $page->content;
	my $opml = $page->content;



	parse_input_opml($dbh,$query,$opml);

}

sub parse_input_opml {
						# Parse OPML file


  my ($dbh,$query,$opml) = @_;
	my $vars = $query->Vars;
  my $opmlcategory;



		# If ?append=no
		# Wipes out existing feeds
		# caution caution caution
	my $backupfile = "";
	if ($vars->{append} eq "no") {
		$vars->{internal} = "import";
		$backupfile = &export_opml($dbh,$query);
		$dbh->do('DELETE FROM feed WHERE feed_id > 0');
		$vars->{msg} .= qq|All existing feeds have been removed.
		 This list has been backed up (as OPML) at
		 <a href="$backupfile">$backupfile</a> .<br/><br/>\n|;
	}

  my $has_categories=0;
	while ($opml =~ m/<outline (.*?)>(.*?)<\/outline>/sig) {
		$has_categories++;
		my $opmlitem = $1;
		if ($opmlitem =~ m/xmlUrl/) { &save_opml($dbh,$query,$opmlitem,"none"); }
		else { if ($opmlitem =~ m/title="(.*?)"/) { $opmlcategory = $1; } else { $opmlcategory = "none"; } }
		$vars->{msg} .= "<p><b>".$opmlcategory."</b><br>";
		my $inneropml = $2;
		while ($inneropml =~ m/<outline (.*?)\/>/sig) {
			my $saveopml = $1;
			&save_opml($dbh,$query,$saveopml,$opmlcategory);
		}
		$vars->{msg} .= "</p>";
	}

  unless ($has_categories) {
		while ($opml =~ m/<outline (.*?)\/>/sig) {
			my $saveopml = $1;
			&save_opml($dbh,$query,$saveopml,"none");
		}

	}
	#while ($opml =~ /<outline (.*?)>/sig) {
		#my $opmlline = $1;
	#	my ($opmlitem,$stuff) = split />|\/>/,$opmlline;

#print $opmlitem,"<br>";

	  &admin_frame($dbh,$query,"Import OPML",$vars->{msg});					# Print Output


}


sub save_opml {

	my ($dbh,$query,$opml,$category) = @_;
	my $vars = $query->Vars;


						# Define Feed Vars
	my $feed = ();
	$opml =~ s/'/&apos;/g;   #'
	$opml =~ s/&amp;/&/g;

	if ($opml =~ m/title="(.*?)"/i) { $feed->{feed_title} = $1; }
	if ($opml =~ m/xmlUrl="(.*?)"/i) { $feed->{feed_link} = $1; }
	if ($opml =~ m/htmlUrl="(.*?)"/i) { $feed->{feed_html} = $1; }
	$feed->{feed_status} = $vars->{feed_status} || "A";
	$feed->{feed_category} = $category;
	$feed->{feed_crdate} = time;
	$feed->{feed_creator} = $Person->{person_id};

						# Add new feeds to DB from OPML

	$vars->{msg} .= "Listed: ",$feed->{feed_link},"<br>";
	unless ($feed->{feed_title}) { $vars->{msg} .= "Feed rejected; no title.<br/>"; return; }
	unless ($feed->{feed_link}) { $vars->{msg} .= "Feed rejected; no URL.<br/>"; return; }


  # Find Feed ID if it exists
  # Two serach URLs used because Wordpress is inconsistent with https
  my $search_url = $feed->{feed_link}; my $second_search_url = $search_url;
  if ($search_url =~ /https:/) { $second_search_url =~ s/https:/http:/i; }
  else  { $second_search_url =~ s/http:/https:/i; }
  $feed->{feed_id} = &db_locate($dbh,"feed",{feed_link=>$search_url});
  unless ($feed->{feed_id}) { $feed->{feed_id} = &db_locate($dbh,"feed",{feed_link=>$second_search_url});}
	if ($feed->{feed_id}) { $vars->{msg} .= "Feed already exists.<br/>"; return; }


	if (my $ff = &db_locate($dbh,"feed",{feed_title => $feed->{feed_title}})) {
			$vars->{msg} .= "Found feed titled ".$feed->{feed_title}." already existing.<br/>";
			unless ($analyze eq "on") { &db_update($dbh,"feed",{feed_link=>$feed->{feed_link}},$ff); }
			$vars->{msg} .= "Inserted new link into existing feed number $ff.";
			return; }

	my $feedid;
	if ($analyze eq "on") { $feedid = "[Not Inserted]"; }
	else { $feedid = &db_insert($dbh,$query,"feed",$feed); }
	if ($feedid) {
		$vars->{msg} .= "Inserted feed number $feedid: ".$feed->{feed_title} . "(". $feed->{feed_link} . ") Category: $category<br/>\n";
	} else { $vars->{msg} .= "Feed insert failed, don't know why.<br/>"; }

	return;

}


sub harvester_stylsheet {

  return qq|
		<style>
      .main { font: normal 1.2em Georgia, sans-serif;  color:#080808; margin-top: 1em; margin-bottom: 0.5em;}
			.function { margin-left:2em;font: normal 1.2em Georgia, sans-serif; color:green;  margin-top: 1em; margin-bottom: 0.5em;}
			.info	{ font: normal 0.8em Georgia, sans-serif; color:#080808; margin-top: 1em; margin-bottom: 0.5em;}
			.detail { font: normal 0.6em Georgia, sans-serif; color:#080808; margin-top: 1em; margin-bottom: 0.5em;}
			.data { font: normal 0.6em Georgia, sans-serif; color:#080808; padding:1em; border: solid darkgray 0.5px; margin-top: 1em; margin-bottom: 0.5em;}
			.harvestererror { font: italic 0.8em Georgia, sans-serif; color:red; margin-top: 1em; margin-bottom: 0.5em;}
			.warning { font: italic 0.8em Georgia, sans-serif; color:orange; margin-top: 1em; margin-bottom: 0.5em;}
    </style>
	|

}
