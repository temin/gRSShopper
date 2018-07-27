#!/usr/bin/perl

# print "Content-type: text/html; charset=utf-8\n\n";

#    gRSShopper 0.3  Admin  0.41  -- gRSShopper administration module
#    29 July 2011 - Stephen Downes

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
#           Admin Functions 
#
#-------------------------------------------------------------------------------



 
# Forbid agents

if ($ENV{'HTTP_USER_AGENT'} =~ /bot|slurp|spider/) { 
  	print "Content-type: text/html; charset=utf-8\n";
	print "HTTP/1.1 403 Forbidden\n\n";
	print "403 Forbidden\n"; 
	exit; 
}


# Initialize gRSShopper Library

use FindBin qw($Bin);
require "$Bin/grsshopper.pl";
our ($query,$vars) = &load_modules("admin");			# Request Variables

our ($Site,$dbh) = &get_site("admin");				# Site
if ($vars->{context} eq "cron") { $Site->{context} = "cron"; }

our $Person = {}; bless $Person;				# Person  (still need to make this an object)
&get_person($dbh,$query,$Person);		
my $person_id = $Person->{person_id};



my $options = {}; bless $options;		# Initialize system variables
our $cache = {}; bless $cache;	





						# Restrict to Admin
if ($Site->{context} eq "cron") { &cron_tasks($dbh,$query,$ARGV); } else { &admin_only(); }






# Analyze Request --------------------------------------------------------------------

my $table = ""; 
my $id = "new";
my $format = ""; 
my $action = $vars->{action};			# Determine Action

						# Determine Request Table, ID number
foreach my $req ("author",
		"box",
		"chat",
		"cite",
		"event",
		"feed",
		"field",
		"file",
		"journal",
		"link",
		"lookup",
		"graph",
		"mapping",
		"media",
		"optlist",
		"post",
		"page",
		"person",
		"presentation",
		"publication",
		"project",
		"reference",
		"subscription",
		"task",
		"template",
		"thread",
		"topic",
		"view") {

	if ($vars->{$req}) { 
		$table = $req; 
		$id = $vars->{$req}; 
		last; 
	}
}






						# Direct DB and list requests
if ($vars->{db} || $vars->{table}) {
	$table = $vars->{table} || $vars->{db};
	if ($vars->{id}) {
		$id = $vars->{id};
	} else {
		unless ($action) { 
			$action = "list"; 
		}
	}
}


if ($vars->{format}) {				# Determine Output Format
	$format = $vars->{format};
	if ($format eq "edit") {	# temporary
		$action = "edit";
		$format = "html";
	}
} else {
	if ($action eq "list") {		# Format for Lists
		$format = "list";
	} else {					
		$format = "html";		# Default to HTML
	}
}


$vars->{id} ||= $id;



	

# Actions ------------------------------------------------------------------------------


unless ($table || $action) {				# Default to Admin Menu
	&admin_general($dbh,$query); 
}

#          $dbh->{RaiseError} = 1;
#my $crvotetable = qq|CREATE TABLE `vote` (
#  `vote_id` int(15) NOT NULL auto_increment,
#  `vote_post` int(15) default NULL,
#  `vote_person` int(15) default NULL,
#  `vote_value` int(15) default NULL,
#  `vote_creator` int(15) default NULL,
#  `vote_crdate` int(15) default NULL,
#  PRIMARY KEY  (`vote_id`)
#) ENGINE=MyISAM DEFAULT CHARSET=utf8 AUTO_INCREMENT=1 ;|;

#my $asth = $dbh -> prepare($crvotetable);
#	$asth -> execute();
# print "Content-type:text/html\n\n";
# print $@;

#my $t = time;
#print &tz_date($query,$t);

# my $eth = $dbh->prepare("TRUNCATE TABLE feed");
# $eth->execute();


#	my $alterstmt = "ALTER TABLE feed MODIFY feed_rules text";
#	my $asth = $dbh -> prepare($alterstmt);
#	$asth -> execute();

#type value verb

#	my $alterstmt = "ALTER TABLE config MODIFY config_noun varchar(255)";
#	my $asth = $dbh -> prepare($alterstmt);
#	$asth -> execute();


# my $sth = $dbh->prepare("TRUNCATE TABLE event");
# $sth->execute();

# my $eth = $dbh->prepare("DELETE FROM link WHERE link_author='8316'");
# $eth->execute();





if ($action) {					# Perform Action, or
	my $tt = ucfirst($action)." ".ucfirst($table);
	$Site->{header} =~ s/\Q[*page_title*]\E/$tt/g;

	for ($action) {
														# Main admin menu nav

		/general/ && do { &admin_general($dbh,$query); last;			};	# 	- General
		/harvester/ && do { &admin_harvester($dbh,$query); last;		};	# 	- Harvester
		/users/ && do { &admin_users($dbh,$query); last;			};	# 	- Users
		/newsletters/ && do { &admin_newsletters($dbh,$query); last;	};	#	- Newsletters
		/database/ && do { &admin_database($dbh,$query); last;		};	#	- Database
		/meetings/ && do { &admin_meetings($dbh,$query); last;		};	#	- Meetings
		/logs/ && do { &admin_logs($dbh,$query); last;		};	#	- Logs
		/permissions/ && do { &admin_permissions($dbh,$query); last;		};	#	- Permissions

		/config/ && do { &update_config($dbh,$query); last;			};	# Update config data
		/db_pack/ && do {&admin_db_pack($dbh,$query); last;		};		# Make a new pack


		/fixmesubs/ && do { &fixmesubs($dbh,$query,$table); last;		};
		/list/ && do { &list_records($dbh,$query,$table); last;		};
		/rollup/ && do { &news_rollup($dbh,$query); last;			};
		/rotate/ && do { &rotate_hit_counters($dbh,$query,"post"); last;			};
		/export_users/ && do { &export_user_list($dbh,$query); last;			};
		/import/ && do { &import($dbh,$query,$table); last;		};
		/remove_all/ && do { &delete_all_users($dbh,$query); last; };
		/send_nl/ && do { &send_nl($dbh,$query); last;	};		
		/autopost/ && do { &autopost($dbh,$query); last; };
		/postedit/ && do { &postedit($dbh,$query); last; };
		/edit/ && do { &edit_record($dbh,$query,$table,$id); last; 	};
		/eduser/ && do { &admin_users_edit($dbh,$query); last;			};
		/subs/ && do { &edit_subs($dbh,$query); last;			};
		/autosub/ && do { &autosubscribe_all($dbh,$query); last;   };
		/autounsub/ && do { &autounsubscribe_all($dbh,$query); last; };
		/update/ && do { $id = &update_record($dbh,$query,$table,$id);
			&edit_record($dbh,$query,$table,$id); last; 		};
		/Delete/ && do { &delete_record($dbh,$query,$table,$id); last;	};		
		/Spam/ && do { &delete_record($dbh,$query,$table,$id); last;	};		
		/publish/ && do { &publish_page($dbh,$query,$id,"verbose"); last; };
		/logview/ && do { &log_view($dbh,$query); last; };
		/logreset/ && do { &log_reset($dbh,$query); last; };
		/reindex_topics/ && do { &reindex_topics($dbh,$query,$id); last; };
		/refield/ && do { &refield($dbh,$query); last; };		
		/recache/ && do { &recache($dbh,$query); last; };
		/reindex/ && do { &reindex_matches($dbh,$query,$table,$id); };
		/approve/ && do { &approve_feed($dbh,$query); last;			};
		/retire/ && do { &retire_feed($dbh,$query); last;		};	
		/count/ && do { &count_feed($dbh,$query); last; };
		/showcolumns/ && do { &showcolumns($dbh,$query); last; };
		/addcolumn/ && do { &addcolumn($dbh,$query); last; };
		/removecolumnwarn/ && do { &removecolumnwarn($dbh,$query); last; };			
		/removecolumndo/ && do { &removecolumndo($dbh,$query); last; };		
		/stats/ && do { &calculate_stats($dbh,$query); last;  };
		/graph/ && do { &make_graph($dbh,$query); last;  };
		/sendmsg/ && do { &admin_users_send_message($dbh,$query); last; };
		/moderate_meeting/ && do { &moderate_meeting($dbh,$query); last;			};	# 	- General
		/test_rest/ && do { api_send_rest($dbh,$query); last; };		

	}


} else {					# Default Data Output

	&output_record($dbh,$query,$table,$id,$format);
}
						



if ($dbh) { $dbh->disconnect; }			# Close Database and Exit
exit;




#---------------------------------------------------------------------------------------------
#
#                 Functions
#
#---------------------------------------------------------------------------------------------




# -----------------------------------   Admin: Sorter   -----------------------------------------------
sub admin_sorter {

	my ($dbh,$query,$title) = @_;

	for ($title) {
		/Site Information/ 			&& do { &admin_general($dbh,$query); last;		};
		/Permissions/ 				&& do { &admin_permissions($dbh,$query); last;		};
		/Base URLs and Directories/ 		&& do { &admin_general($dbh,$query); last;		};
		/Media Directories/ 			&& do { &admin_general($dbh,$query); last;		};
		/Upload Directories/ 			&& do { &admin_general($dbh,$query); last;		};
		/Anonymous User/ 			&& do { &admin_users($dbh,$query); last;		};
		/Enable Registration/			&& do { &admin_users($dbh,$query); last;		};
		/Enable Harvester/			&& do { &admin_harvester($dbh,$query); last; 		};
		/Email Program and Addresses/ 	&& do { &admin_newsletters($dbh,$query); last;		};
		/Big Blue Button Configuration/ 	&& do { &admin_meetings($dbh,$query); last;		};
	}
	&admin_general($dbh,$query);
	exit;
}

# -----------------------------------   Admin: Frame   -----------------------------------------------

sub admin_frame {



	my ($dbh,$query,$title,$content) = @_;
	my $vars = $query->Vars;

	return unless (&is_viewable("admin","general")); 		# Permissions
	$title ||= "Admin Title"; $content ||= "Admin Content";
	print "Content-type: text/html; charset=utf-8\n\n";
	print $Site->{header};
	print &admin_navbar();
	print $content;
	print $Site->{footer};
	exit;

	
}

# -----------------------------------   Admin: Navbar   -----------------------------------------------

sub admin_navbar {

	my $content = qq|<ol id="toc">\n|;
	foreach my $link (qw|general harvester users newsletters database meetings logs permissions|) {
		$content .= qq|<li><a href="$Site->{st_cgi}admin.cgi?action=|.$link.qq|"><span>|.ucfirst($link).qq|</span></a></li>\n|;
	}
	$content .= qq|<li><a href="$Site->{st_cgi}page.cgi?action=viewer"><span>Viewer</span></a></li>\n|;  # Direct link to viewer
	$content .= "</ol>\n";
	return $content;
	
}

# -----------------------------------   Admin: Config Table   -----------------------------------------------

sub admin_configtable {

	my ($dbh,$query,$title,@vals) = @_;

	my $content = qq|

		<h3>$title</h3>
		<div class="adminpanel">
		<ul><form method="post" action="$Site->{st_cgi}admin.cgi">
		<input type="hidden" name="action" value="config">
		<input type="hidden" name="title" value="$title">
		<table cellspacing="0" cellpadding="2" border="0">
	|;
	foreach my $v (@vals) {
		my ($t,$v,$f) = split ":",$v;    # Title, variable name, format
		if ($f eq "yesno") {
			my $yesselected=""; my $noselected="";
			if ($Site->{$v} eq "yes") { $yesselected = qq| selected="selected"|; }
			else { $noselected = qq| selected="selected"|; }
			$content .= qq|<tr><td align="right">$t : </td><td>
			<select name="$v">
			<option value="yes" $yesselected >Yes</option>
			<option value="no" $noselected >No</option>
			</select>
			</td></tr>\n|;		
		} else {
			$content .= qq|<tr><td align="right">$t : </td><td>
			<input type="text" size="60" name="$v" value="$Site->{$v}"></td></tr>\n|;
		}
	}


	$content .= qq|<tr><td colspan="2"><input type="submit" class="button" value="Submit $title"></tr></td>|;
	$content .= "</table>\n</form></ul>
		</div>\n";
}

# -----------------------------------   Admin: General   -----------------------------------------------
#
#   Initialization and editing of general site configuration data
#   Expects and requires access to a 'config' table in the database
#   The config table in turn is used by init_site() in grsshopper.pl
#
# ------------------------------------------------------------------------------------------------------

sub admin_general {

	my ($dbh,$query) = @_;


	my $content = qq|<h2>General Information</h2><p>These values control site filenames and directories.
		Changing them can render gRSShopper inoperable. Exercise caution and do not make changes unless
		you are sure you know what the result will be.</p>|;
		

	$content .= &admin_configtable($dbh,$query,"Site Information",
		("Site Name:st_name","Site Tag:st_tag","Publisher:st_pub","Creator:st_crea","License:st_license","Time Zone:st_timezone","Reset Key:reset_key","Cron Key:cronkey"));

	$content .= &admin_configtable($dbh,$query,"Base URLs and Directories",
		("Base URL:st_url","Base Directory:st_urlf","CGI URL:st_cgi","CGI Directory:st_cgif","Login URL:st_login"));

	$content .= &admin_configtable($dbh,$query,"Media Directories",
		("Images:st_img","Photos:st_photo","Files:st_file"));

	$content .= &admin_configtable($dbh,$query,"Upload Directories",
		("Uploads:st_upload","Images:up_image","Documents:up_docs","Slides:up_slides","Audio:up_audio","Videos:up_video"));

		
	&admin_frame($dbh,$query,"Admin General",$content);					# Print Output
	exit;



}


# -----------------------------------   Admin: Meetings   -----------------------------------------------
#
#   Initialization and editing of general site configuration data
#   Expects and requires access to a 'config' table in the database
#   The config table in turn is used by init_site() in grsshopper.pl
#
# ------------------------------------------------------------------------------------------------------

sub admin_meetings {

	my ($dbh,$query) = @_;



	my $content = qq|<h2>Meetings</h2><p>This is the gRSShopper interface to Big Blue Button. If there is
		no instance of BBB available, this section will not be usable.</p>|;
		
	my $meeting_con = &bbb_get_meetings();
	my $meetingcount = 0;
			
	$Person->{person_name} ||= $Person->{person_title};
	$content .= qq|<h3>Current Live Meetings</h3>
		<form method="post" action="$Site->{st_cgi}page.cgi">
		<p>These are the live meetings currently running ion $Site->{st_name}. If you would
		like to enter the confreencing environment and join the meeting, please provide a 
		name and then select the meeting you would like to join.<br/><br/>
		
		Enter your name: <input size="40" type="text" name="username" value="$Person->{person_name}"></p>
		
		<input type="hidden" name="action" value="join_meeting">

		<ul><table cellpadding="5" cellspacing="0" border="0">|;
	
	while ($meeting_con =~ /<meeting>(.*?)<\/meeting>/g) {
		$meetingcount++; my $meeting = (); my @moderators;
		my $meet_data = $1; my $meeting_id; my $meeting_name; my $meeting_started;

		while ($meet_data =~ /<meetingName>(.*?)<\/meetingName>/g) { $meeting->{name} = $1; }	
		next if ($meeting->{name} eq "Administrator Meeting");
		
		while ($meet_data =~ /<meetingID>(.*?)<\/meetingID>/g) { $meeting->{id} = $1; }
		$meeting->{info} = &bbb_getMeetingInfo($meeting->{id});
		
		while ($meeting->{info} =~ /<participantCount>(.*?)<\/participantCount>/g) { $meeting->{count} = $1; }
		while ($meeting->{info} =~ /<attendee>(.*?)<\/attendee>/g) { 
			my $attendee = $1; my $a = ();
			while ($attendee =~ /<role>(.*?)<\/role>/g) { $a->{role} = $1; }
			while ($attendee =~ /<fullName>(.*?)<\/fullName>/g) { $a->{fn} = $1; }
			if ($a->{role} =~ /moderator/i) {			
				if ($meeting->{mods}) { $meeting->{mods} .= ", "; }
				$meeting->{mods} .= $a->{fn};	
			}
		}
			
		while ($meet_data =~ /<createTime>(.*?)<\/createTime>/g) { $meeting_started = $1; }	
		$content .= qq|<tr><td align="right"><b>$meeting->{name}</b> - $meeting->{count} participant(s)<br/>
				Moderator(s): $meeting->{mods} </td>
				<td valign="top">
				<input type="submit" name="meeting_id" 
				value="Join Meeting $meeting->{id}"></td></tr>|;	
 # $content .= qq|<form><textarea cols="50" rows="10">$meet_data\n\n$meet_info</textarea></form><p>|;	
	}
	$content .= "</table></ul></p></form>";
	if ($meetingcount ==0) {
		$content .= "<p><ul>There are currently no live meetings taking place.</ul></p>";
	}
	
			

		
	my $newid = time;	
	$content .= qq|<h3>Create and Join Meetings</h3>
		<form method="post" action="$Site->{st_cgi}admin.cgi">
		<input type="hidden" name="action" value="moderate_meeting">
		<ul><table cellpadding="2" cellspacing="0" border="0">
		<tr><td align="right">Meeting Name:</td><td><input type="text" name="meeting_name" size="40"></td></tr>
		<tr><td align="right">Meeting Ident:</td><td><input type="text" name="meeting_id" value="$newid" size="40"></td></tr>
		<tr><td align="right">Recording:</td>
		<td><select name="meeting_record"><option value="off">Recording Off</option>
		<option value="on">Recording On</option></select></td></tr>
		<tr><td align="right" colspan="2"><input type="submit" value="Create Meeting and Join It"></td></tr>
		</table></form></ul>|;
	
	
	$content .= qq|<h3><a href="$Site->{st_cgi}admin.cgi?action=moderate_meeting">Join Standing Administration Meeting</a></h3><p>|;

	$content .= &admin_configtable($dbh,$query,"Big Blue Button Configuration",
		("BBB Name:bbb_name","BBB URL:bbb_url","BBB Salt:bbb_salt","Admin Pwd:bbb_mp","Attendee Pwd:bbb_ap"));






	&admin_frame($dbh,$query,"Meetings",$content);					# Print Output
	exit;



}

# -----------------------------------   Admin: Logs   -----------------------------------------------
#
#   View Logs
#
# ------------------------------------------------------------------------------------------------------


sub admin_logs {
	
	my ($dbh,$query) = @_;

	return unless (&is_viewable("admin","logs")); 		# Permissions	
	
	my $content = qq|<h2>View Logs</h2><p>
		General Statistics - 
		[<a href="admin.cgi?action=logview&logfile=General Stats&format=table">Table</a>] 
		[<a href="admin.cgi?action=logview&logfile=General Stats&format=tsv">TSV</a>] 
		[<a href="admin.cgi?action=logview&logfile=General Stats&format=csv">CSV</a>]<br/>
		Cron Logs - [<a href="admin.cgi?action=logview&logfile=cronlog">Text File</a>]
		</p>|;
		



	&admin_frame($dbh,$query,"Admin General",$content);					# Print Output
	exit;
	

	
}	

# -----------------------------------   Admin: Permissions   -----------------------------------------------
#
#   View and Set Default Permissions
#
# ------------------------------------------------------------------------------------------------------


sub admin_permissions {
	
	my ($dbh,$query) = @_;

	return unless (&is_viewable("admin","permissions")); 		# Permissions	
	
	my $content = qq|<h2>Permissions</h2><p>|;
	
	# my @tables = $dbh->tables();
	my @tables = qw{author box event feed file journal link mapping optlist page person post presentation 
		project publication publisher task template thread topic view};
	my @actions = qw{create edit delete view};
	my @reqs = qw{admin owner project registered anyone};	
	

	$content .= qq|<style>
		select.admin {background-color: #cc0000;}
		select.owner {background-color: #ffcccc;}
		select.project {background-color: #ffcc00;}
		select.registered {background-color: #ff00cc;}
		select.anyone {background-color: #008800;}
		option.admin {background-color: #cc0000;}
		option.owner {background-color: #ffcccc;}
		option.project {background-color: #ffcc00;}
		option.registered {background-color: #ff00cc;}
		option.anyone {background-color: #008800;}
		</style>
		|;
	
	# Table Headings
	$content .= qq|<form method="post" action="admin.cgi">
		<input type="hidden" name="title" value="Permissions">
		<input type="hidden" name="action" value="config">|;	
	$content .= "<p><table cellpadding=3 cellspacing=0 border=1>";
	$content .= "<tr><td><i>Data Type</i></td>";
	foreach my $action (@actions) { $content .= "<td>".ucfirst($action)."</td>"; }
	$content .= "</tr>\n";
	
	foreach my $table (@tables) {
		$content .= "<tr><td>".ucfirst($table)."</td>";
		foreach my $action (@actions) { 
			
			my $vname = $action."_".$table;
			my $creq = &permission_current($action,$table);
			$content .= qq|<td><select name="$vname" class="$creq" >\n|;
			foreach my $req (@reqs) {
				my $sel="";if ($creq eq $req) { $sel = " selected"; }
				$content .= qq|<option class="$req" value="$req"$sel> $req</option>\n|;
			}
			$content .= qq|</select></td>\n|;
		}
		$content .= "</tr>\n";
	}	

	$content .= qq|</table></p>Color will not change until data has been saved.<br>
		<input type="submit" value="Update Permissions"></form>|;
		



	&admin_frame($dbh,$query,"Admin Permissions",$content);					# Print Output
	exit;
	
}



# -----------------------------------   Admin: Harvester   -----------------------------------------------
#
#   Harvester management utilities
#
# ------------------------------------------------------------------------------------------------------

sub admin_harvester {

	my ($dbh,$query) = @_;

	return unless (&is_viewable("admin","harvester")); 		# Permissions
	
	my $content = qq|<h2>Harvester</h2><p>On this page you can manage and operate your harvester. To turn
		on automated harvesting, set 'Enable Harvester' to 'yes' (requires cron). The harvester will
		process one feed every 'Harvester Interval' minutes. To add, manage and delete content sources,
		create, edit and delete feeds (see the menu at left) or use the OPML options below.</p>|;

	my $harvesterlink = $Site->{st_cgi}."harvest.cgi";
	my $edursslink = $Site->{st_cgi}."edurss02.cgi";
	
	
	$content .= &admin_configtable($dbh,$query,"Enable Harvester",
	("Enable Harvester:st_harvest_on:yesno","Harvester Interval:st_harvest_int"));
		
		
	# Get Feed List
	my $feedselector = qq|<option value="0">Please select a feed from the list....</option>\n|;
	my $sql = qq|SELECT feed_id,feed_title,feed_status from feed ORDER BY feed_title|;
	my $sth = $dbh -> prepare($sql);
	$sth -> execute();								
	while (my $feed = $sth -> fetchrow_hashref()) { 
		$feed->{feed_title} = substr($feed->{feed_title},0,45);
		$feedselector .= qq|<option value="$feed->{feed_id}">$feed->{feed_title} ($feed->{feed_status})</option>\n|;
	}

	$content .= qq|
	
		<h3>Operate Harvester</h3>
		<form method="post" action="harvest.cgi">
		<ul>
		<input type="radio" name="source" value="queue" selected> Harvest Next In Queue<br/>
		<input type="radio" name="source" value="feed"> Harvest Feed: <select name="feed">$feedselector</select>
		<br/>
		<input type="radio" name="source" value="url"> Harvest URL:
		<input type="text" name="url" value="Enter full URL here" size="40"><br/>
		<input type="radio" name="source" value="file"> Harvest File:
		<input type="text" name="file" value="File name, file needs to be in same directory as script (for now)" size="40"><br/>
		<input type="radio" name="source" value="all"> Harvest All<br/><br/>
		<input type="submit" class="button" value="Harvest Feed">
		</ul>
		</form>


		<h3>View Harvest Results</h3>
		<p><ul>
		<li><a href="$Site->{cgi}page.cgi?action=viewer">Viewer</a></li>
		</ul></p>
	
		<h3>Import and Export Feeds</h3>|;
		
	if (&new_module_load($query,"XML::OPML")) {
		$content .= qq|		
		<p><ul>
		<li><a href="|.$Site->{st_cgi}.qq|harvest.cgi?action=export">Export OPML File</a></li>
		<li> <a href="$harvesterlink?action=opmlopts">Import Feed List From OPML</a>
		</ul></p>|;
	} else {
		$content .= $vars->{error};
	}

	&admin_frame($dbh,$query,"Admin General",$content);					# Print Output
	exit;

}

# -----------------------------------   Admin: Users   -----------------------------------------------
#
#   Manage Users
#
# ------------------------------------------------------------------------------------------------------

sub admin_users {

	my ($dbh,$query) = @_;


	return unless (&is_viewable("admin","users")); 		# Permissions
	my $adminlink = $Site->{st_cgi}."admin.cgi";
		
	my $intro = "";	
	if ($vars->{msg}) { $intro = qq|<p class="notice">$vars->{msg}</p>|; }
	else { $intro = "<p>On this page you can manage your user accounts and newsletter subscriptions. Note that 
		you can also access user accounts directly by searching and editing in the 'Persons' table, left.</p>";	}
		
		
	my $content = qq|<h2>Users</h2>$intro|;


	$content .= &admin_configtable($dbh,$query,"Enable Registration",
		("Enable Registration:st_reg_on:yesno"));
	
	$content .= &admin_configtable($dbh,$query,"Anonymous User",
		("Anonymous User Name:st_anon","Anonymous IUser ID:st_anon_id"));

	$content .= qq|
		<h3>Find User</h3>
		<div class="adminpanel">
		<form method="post" action="$Site->{st_cgi}admin.cgi">
		<input type="hidden" name="action" value="eduser">
		<table>
		<tr><td>User ID number:</td><td><input type="text" name="pid" size="20"></td></tr>
		<tr><td><b>or</b> userid:</td><td><input type="text" name="ptitle" size="40"></td></tr>
		<tr><td><b>or</b> name:</td><td><input type="text" name="pname" size="40"></td></tr>
		<tr><td><b>or</b> email:</td><td><input type="text" name="pemail" size="40"></td></tr>
		</td></tr></table>
		<input type="submit" value="Find User" class="button">
		</form>
		</div>
	|;

	$content  .= qq|
		<h3>Import User List From File</h3>
		<div class="adminpanel">
		<ul>The file needs to be preloaded on the server. The system expects a tab delimited file with 
		field names in the first row. Importer will not new account if an existing account with the same email address exists. Importer will combine 'First Name' and 'Last Name' to create 'Name'. Importer will autogenerate passwords. Importer will ignore field names it does not recognize. Importer will send email with account information to email address.<br/><br/>
		<form method="post" action="$adminlink">
		<input type="hidden" name="action" value="import">
		<input type="hidden" name="table" value="person">
		$tout
		File: <input type="text" name="file">
		<input type="submit" value="Import" class="button">
		</form></ul></div>|;

	$content .= qq|	<h3>Export User List</h3>
		<div class="adminpanel">

		<p>
		<form method="post" action="$adminlink">
		<input type="hidden" name="action" value="export_users">	
		<select name="exportformat">
		<option value="CSV" selected>Select a Format...</option>
		<option value="CSV">Comma Separated Values</option>
		<option value="TSV">Tab Separated Values</option>
		</select>
		<input type="submit" value="Export User List" class="button">
		</form>
		</p>



		</p></div>|;


	# It's here, but I just don't think it's wise to enable it
	# To enable, remove the word DISABLED

	 	$content .= qq|	<h4>Delete All Users</h4>
		<div class="adminpanel"><p>
		<form method="post" action="$adminlink">
		<input type="hidden" name="saction" value="remove_all">	 
		<select name="action">
		<option value="NONONO" selected>Really?</option>
		<option value="DISABLEDremove_all">Yes, Really</option>
		</select>
		<input type="submit" value="Delete All Users" class="button">
		</form></p>
		</div><p>&nbsp;</p>|;
	
	

	&admin_frame($dbh,$query,"Admin General",$content);					# Print Output
	exit;



}


sub admin_users_edit {

	my ($dbh,$query) = @_;
	
	&error ($dbh,"","","Permission denied") unless ($Person->{person_status} eq "admin"); 		# Permissions

									# Find User Information
	my $user;
	if ($vars->{ptitle}) { $user = &db_get_record($dbh,"person",{person_title=>$vars->{ptitle}}); }
	elsif ($vars->{pname}) {  $user = &db_get_record($dbh,"person",{person_name=>$vars->{name}}); }
	elsif ($vars->{pemail}) {  $user = &db_get_record($dbh,"person",{person_email=>$vars->{pemail}}); }
	elsif ($vars->{pid}) {  $user = &db_get_record($dbh,"person",{person_id=>$vars->{pid}}); }
	else { &error($dbh,"","","User information was not supplied"); }
	unless ($user) { &error($dbh,"","","I feel terrible. User information was not found."); }
	
	$user->{person_name} ||= $user->{person_title};
	my $content = qq|<h2>User Information Found</h2>
		<div class="adminpanel">
		Name: $user->{person_name} ($user->{person_title})<br/>
		UserID: $user->{person_id}<br/>
		Email: $user->{person_email}<br/>
		[<a href="$Site->{st_cgi}admin.cgi?person=$user->{person_id}&action=edit">Edit $user->{person_name}</a>]<br/>
		[<a href="javascript:confirmDelete('$Site->{st_cgi}admin.cgi?person=$user->{person_id}&amp;action=Delete')">Delete $user->{person_name}</a>] <br>
		[<a href="$Site->{st_cgi}login.cgi?action=Subscribe&pid=$user->{person_id}">Edit Subscriptions</a>]<br/>
		<br/>Send this person a message:<br/>
		<form method="post" action="$Site->{st_cgi}admin.cgi">
		<input type="hidden" name="action" value="sendmsg">
		<input type="hidden" name="userid" value="$user->{person_id}">
		<input type="text" size="40" name="subject">
		<textarea cols="80" rows="10" name="body"></textarea>
		<input type="submit" value="send email"></form>
		</div>|;
		
	
	
	my $user = &db_get_record($dbh,"person",{$fields->{id}=>$id_number});
	



	 print "Content-type: text/html; charset=utf-8\n\n";
	 print $Site->{header};
	 print $content;
	 print $Site->{footer};
	 exit;

}

# -----------------------------------   Admin: Users: Send Message  --------------------------------------------
#
#   Manage Users
#
# ------------------------------------------------------------------------------------------------------

sub admin_users_send_message {
	
	 my $content =qq|<h2>Message Sent</h2>|;
	
	
	&error ($dbh,"","","Permission denied") unless ($Person->{person_status} eq "admin"); 		# Permissions
	&error($dbh,"","","No body in message") unless ($vars->{body});
	&error($dbh,"","","No person to send to") unless ($vars->{userid});
	$vars->{subject} ||= "Message from $Person->{person_name} on $Site->{st_name}";
		
	my  $user = &db_get_record($dbh,"person",{person_id=>$vars->{userid}});
	&error($dbh,"","","No email address to send to") unless ($user->{person_email});
	$vars->{body} .= "\n\nSent from gRSShopper administrator on $Site->{st_name}\n";	
		
		
	$vars->{subject} =~ s/&#39;/'/g;
	$vars->{body} =~ s/&#39;/'/g;
	$Site->{st_name} =~ s/&#39;/'/g;
			
	&send_email($user->{"person_email"},$Site->{em_from}, $vars->{subject},$vars->{body});


						
	 print "Content-type: text/html; charset=utf-8\n\n";
	 print $Site->{header};
	 print $content;
	 print $Site->{footer};
	 exit;
}

# -----------------------------------   Admin: Newsletters   -----------------------------------------------
#
#   Manage and Send Newsletters
#
# ------------------------------------------------------------------------------------------------------

sub admin_newsletters {

	my ($dbh,$query) = @_;

	return unless (&is_viewable("admin","newsletter")); 		# Permissions
	my $adminlink = $Site->{st_cgi}."admin.cgi";

	my $content = qq|<h2>Newsletters</h2><p>Each newsletter is composed of a page and a list of subscribers.
		Edit pages at left, and to turn any page into a newsletter, set 'Autopub' to 'yes' and 'Sub' to 'yes'.
		Newsletter contents are typically created automatically using 'keyword' commands in the page; see
		keyword help for more information. Users subscribe to newsletters through the 'Options' screen; 
            you can manage user subscriptions directly from this page, either individually or as a group. Selecting
		'send newsletter' to all subscribers sends the newsletter by email using the values at the bottom
            of the screen.|;




	# Get list of eligible newsletters in dropdown form
	my $npageoptionlist = "<option>Select a newsletter</option>\n";
	my $stmt = qq|SELECT * FROM page WHERE page_sub='yes'|;	
	my $sthl = $dbh->prepare($stmt);
	$sthl->execute();
	while (my $s = $sthl -> fetchrow_hashref()) {
		$npageoptionlist .= qq|<option value="$s->{page_id}">$s->{page_title}</option>\n|;
	}


	$content .= qq|
		<h3>Send Newsletter</h3>
		<div class="adminpanel">
		<form method="post" action="$Site->{st_cgi}admin.cgi">
		<input type="hidden" name="action" value="send_nl">
		<input type="hidden" name="verbose" value="1">		
		<table cellpadding="3">
		<tr><td><b>Page</td><td><b>List</b></td><td>&nbsp;</td></tr>
		<tr><td><select name="page_id">$npageoptionlist</select></td>
		<td>		<select name="send_list">
		<option value="on">Select an action</option>
		<option value="admin">To Admins Only</option>
		<option value="subscribers">To All Subscribers</option>
		<option value="all_users">To All Users</option>		
		</select></td>
		<td><input type="submit" value="Send Newsletter" class="button"></td></tr></table>
		</form>
		</div>
	|;

	$content .= qq|
	

		<br/><h3>Manage Newsletter</h3>
		<div class="adminpanel">

		<b>Post Issue Rollup</b><br/>
		Posts in newsletters can be scheduled for publication ahead of time; see the
		'Edit Post' screen for more. This button will show you the list of posts scheduled
		for upcoiming newsletters.<br>
		<form method="post" action="$adminlink">
		<input type="hidden" name="action" value="rollup">	
		<input type="submit" value="Rollup" class="button">
		</form>
		</div><br/>
		


		<h3>Manage Subscriptions</h3>
		<div class="adminpanel">
				<b>Autosubscribe</b><br/>
		<form method="post" action="$adminlink">
		<select name="action">
		<option>Select an action</option>
		<option value="autosub">Autosubscribe All</option>
		<option value="autounsub">Unsubscribe All</option>
		</select>
		to
		<select name="newsletter">
		$npageoptionlist
		</select>
		<input type="submit" value="Do It" class="button">
		</form>
		</div><br/>
		
	|;

	$content .= &admin_configtable($dbh,$query,"Email Program and Addresses",
		("Mail Program Location:em_smtp","System Email:em_from",
		"Discussion Email:em_discussion","Copyto Email:em_copy","Def:em_def"));

	&admin_frame($dbh,$query,"Admin General",$content);					# Print Output
	exit;



}

# -----------------------------------   Admin: Database   -----------------------------------------------
#
#   Initialization and editing site databases
#
# ------------------------------------------------------------------------------------------------------

sub admin_database {

	my ($dbh,$query,$sst,$columns) = @_;


	return unless (&is_viewable("admin","database")); 		# Permissions
	my $adminlink = $Site->{st_cgi}."admin.cgi";

	if ($vars->{dbmsg}) { $vars->{dbmsg} = qq|<p class="notice">$vars->{dbmsg}</p>|; }
	my $content = qq|$vars->{dbmsg}<h2>Database</h2><p>Get database information and manage database tables.</p>|;


	# Manage Database
	
	my @tables = $dbh->tables();
	$content .= qq|	
		<h3>Manage Database</h3>
		<div class="adminpanel">
		<form method="post" action="admin.cgi">Select table:
		<select name="stable">|;
	foreach my $t (@tables) { 
		$t=~s/`//g;
		my $sel; if ($t eq $sst) { $sel = " selected"; } else {$sel = ""; } 
		$content  .= qq|		<option value="$t"$sel>$t</option>\n|;

	}
	$content .= "</select><br>\n";
	$content .= qq|<select name="action">\n
		<option value="showcolumns">Show Columns</option>\n
		<option value="addcolumn">Add Column</option>\n
		<option value="removecolumnwarn">Remove Column</option>\n
		</select>\n
		<input type="text" name="col" value="" size="12"  style="height:1.8em;"/>\n
		<input type="submit" value="Submit" class="button">\n
	|;
	$content .= "</select></form></ul>\n";

	# Display results from previous processing
	if ($columns) { $content .= $columns; }
	$content .= "<br/>";
	$content .= "</div>";

	

	# Import from File


	my $tout = qq|<select name="table">|;
	foreach my $t (@tables) { $t=~s/`//g;$tout .= qq|<option value="$t">$t</option>\n|; }
	$tout .= "</select><br/>\n";

	
	$content  .= qq|
		<br/><h3>Import Data From File</h3>
		<div class="adminpanel">
		The file needs to be preloaded on the server. The system expects a tab delimited file with 
		field names in the first row. Importer will ignore field names it does not recognize.<br/><br/>
		<form method="post" action="$adminlink" enctype="multipart/form-data">		
		<input type="hidden" name="action" value="import">
		<table cellpadding=2>
		<tr><td>Import into table:</td><td>$tout</td></tr>
		<tr><td>File URL:</td><td><input type="text" name="file_url" size="40"></td></tr>
		<tr><td>Or Select:</td><td><input type="file" name="file_name" /></td></tr>
		<tr><td>Data Format:</td><td><select name="file_format"><option value="">Select a format...</option>
		<option value="tsv">Tab delimited (TSV)</option>
		<option value="csv">Comma delimited (CSV)</option></select></td>
		<tr><td colspan=2><input type="submit" value="Import" class="button"></tr></tr></table>
		</form></div>|;
		
	# Export data		
		
		
	$content .= qq|		
		<h3>Export Data</h3><ul>
		Export scripts use <b>mysqldump</b> and assume you are using MySQL and Linux. If you
		are not set up this way you will need to replace the export scripts with scripts that 
		will work for your system.<br/><br/>
		</ul>|;	
		
			
	$content .= qq|		
		<h3>Create Data Pack</h3><ul>
		Data Packs contain the <i>data</i> from several tables in addition to the basic table structure
		for all tables (which may be modified above). These are intended to create new blank sites out
		of the site you already have, with predefined pages, templates, or whatever. 
		Data Pack scripts use <b>mysqldump</b> and assume 
		you are using MySQL and Linux. If you are not set up this way you will need to replace 
		the export scripts with scripts that will work for your system. Saving a Data Pack
		writes over an existing Data Pack with that name.<br/><br/>
		<form method="post" action="admin.cgi"><table cellpadding="3" cellspacing="0" border="1">
		<input type="hidden" name="action" value="db_pack">
		<tr><td>Create Data Pack named</td><td><input type="text" name="pack" size="20"></td></tr>
		<tr><td valign="top">Use fields:</td><td><select name="fields" multiple="multiple" size="8">|;
		
	foreach my $tt (@tables) { 
		$tt=~s/`//g;
		next if ($tt =~ /config/);
		next if ($tt =~ /person/);		
		next if ($tt =~ /cache/);
		$content  .= qq|	<option value="$tt">$tt</option>\n|;

	}		
	$content .= qq|</select></td></tr><tr><td>&nbsp;</td>
		<td><input type="submit" value="Create Data Pack"></td></tr></table></form>
		</ul>|;		
		
	$content .= qq|		
		<h3>Initialize Website</h3><ul>
		<b>WARNING</b>: This will <i>wipe out</i> your existing database. Do not run this command
		unless you <i>really really</i> want to start over. Initialize will clear out your database 
		and then let you start over on the website with one of the Data Packs you've created and 
		saved.<br/><br/>Click here to initialize: [<a href="initialize.cgi?ignit=manual">Initialize Website</a>]
		</ul>|;				
		
	$Site->{ServerInfo}  =  $dbh->{'mysql_serverinfo'};
	$Site->{ServerStat}  =  $dbh->{'mysql_stat'};
	
	$content .= qq|		
		<h3>Database Information</h3><br/><ul>
		&nbsp;&nbsp;Server Info: $Site->{ServerInfo} <br/>
		&nbsp;&nbsp;Server Stat: $Site->{ServerStat}<br/><br/></ul>|;



	&admin_frame($dbh,$query,"Admin General",$content);					# Print Output
	exit;

 

}

#
#       run_sql_file
#
#     	Yes, I know I could just do $dbh->do(sqlfile)
#       but doing it this way sports and reports errors line by line
#

#-----------------------------------------------------------------------------------------------------------------

sub run_sql_file {
	
	my ($dbh,$sqlFile) = @_;


	# Open the file that contains the various SQL statements
	# Assuming one SQL statement per line

	unless (-e $sqlFile) {	&db_create_tables_err($sqlFile,"Could not find SQL file"); }	

	open (SQLFILE, "$sqlFile") or &file_read_error($sqlFile,$!,"load SQL tables into the database");
	
	# Loop though the SQL file and execute each and every one.
	my @sqllines;
	my $sqlline = "";
	while (<SQLFILE>) {
		chomp;
		my $l = $_;
		$l =~ s/\n//;$l =~ s/\r//;
		next if ($l =~ /^\/\*/);
		next if ($l =~ /^--/);	
		$sqlline .= $l;			
		if ($sqlline =~ /;(.*?)$/) {
			push @sqllines,$sqlline;
			$sqlline = "";
		}
	}
	close SQLFILE;


	foreach my $sqlStatement (@sqllines) {
		my $sth = $dbh->prepare($sqlStatement) or die "Can't prepare $sqlStatement";
print $sqlStatement."<br>";		
		$sth->execute() or print "Can't execute $sqlStatement because $dbh::errstr";
		die "Database initializaton failed: $dbh::errstr\n" if $dbh::err;
	}	
	
	 print "$sqlFile run successfully.<br/>";
exit;	
}

sub admin_db_pack {
	
	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	&error($dbh,"","","No Pack Name specified") unless ($vars->{pack});
												# Make Pack Directory
	my $packsdir = $Site->{st_cgif}."packs/".$vars->{pack};
	unless (-d $packsdir) { mkdir $packsdir, 0755 or die "Error 1062 creating upload directory $packsdir $!"; }
	
												# Clearn out existing files
	opendir (DIR,$packsdir);
	my @files = grep(/grsshopper/, readdir (DIR));
	closedir (DIR);
	foreach my $file (@files) { unlink "$packsdir/$file"; } 												
	
												# Execute shell script
	my $pwd = $Site->{database_pwd}; $pwd =~ s/\&/\\\&/g; 					# cgi-bin/data_pack.sh
	my @fields = split /\0/,$vars->{fields};
	my $fields = join " ",@fields;
	
	my $symsg = qq|./data_pack.sh $vars->{pack} $pwd $Site->{db_name} $fields|;
	print "Content-type: text/html\n\n";
	print $symsg,"<p>";
	my $systring = `./data_packa.sh $vars->{pack} $pwd $Site->{db_name} $fields`;
	$vars->{dbmsg} .= "$systring<br>Data Pack a <b>$vars->{pack}</b> Created";
	&admin_database($dbh,$query);
} 

# --------------------------------------   Update Config -----------------------------------------------
#
#    Accept user input from admin and update the config table
#
# ------------------------------------------------------------------------------------------------------

sub update_config {

	my ($dbh,$query) = @_;
	return unless (&is_allowed("edit","config"));

	# Update Config Table
	while (my ($vx,$vy) = each %$vars) {
		
		next if ($vx =~ /^(action|mode|cronsite|format|button|force|comment|id|title|mod_load|msg|test)$/);	
	
		my $sth; my $sql;
		if ($Site->{$vx}) {	# Existing
		
			$sql = qq|UPDATE config SET config_value=? WHERE config_noun='$vx'|;
			$sth = $dbh->prepare($sql)  or die "Cannot prepare: " . $dbh->errstr();
			$sth->execute($vy) or die "Cannot execute: " . $sth->errstr();
		} else {
				
			$sql = "INSERT INTO config (config_noun,config_value) VALUES (?,?)"; 
			$sth = $dbh->prepare($sql)  or die "Cannot prepare: " . $dbh->errstr();
			$sth->execute($vx,$vy) or die "Cannot execute: " . $sth->errstr();
		}
		$sth->finish();
		
		# Status Message
		$vars->{msg} .= "$vars->{title} : $vx has been set to $vy <br/>";
	}


	# Reload Site Data
	my $sth = $dbh -> prepare("SELECT * FROM config"); $sth -> execute();
	while (my $c = $sth -> fetchrow_hashref()) { $Site->{$c->{config_noun}} = $c->{config_value}; }
	$sth->finish();



	# Display Admin Page
	&admin_sorter($dbh,$query,$vars->{title});

}








# -------   Admin Menu: Courses   -----------------------------------------------

sub admin_courses {

	return unless (&is_viewable("admin","courses")); 		# Permissions
	
	return qq|<div class="menubox">
		
		<h4>Courses</h4>
		<p><ul>
		<li><a href="course.cgi">My Courses</a></li>
		</ul>	
	
	</div>|;

}






# -------   Admin Menu: graph ---------------------------------------------

sub admin_graph {

	return unless (&is_viewable("admin","graph")); 		# Permissions
	my $adminlink = $Site->{st_cgi}."admin.cgi";
		

	return qq|<div class="menubox">
	
		<h4>Graph</h4>



		<ul>
		<b>Generate Graph</b><br/>
		<form method="post" action="$adminlink">
		<input type="hidden" name="action" value="graph">	
		<input type="submit" value="Generate" class="button">
		</form>
		</ul>
	
	</div>|;

}


# -------   Export User List --------------------------------------------------------

sub export_user_list {

	my ($dbh,$query) = @_;
	
	if ($vars->{exportformat} =~ /^CSV$/i) {			# CSV
		print "Content-type: text/plain\n\n";
		print &make_user_list($dbh,$query,"csv");

	}elsif($vars->{exportformat} =~ /^TSV$/i) {		# TSV
		print "Content-type: text/plain\n\n";
		print &make_user_list($dbh,$query,"tsv");
	}


}


sub make_user_list {

	my ($dbh,$query,$delim) = @_;

	my $endlim;
	if ($delim =~ /^CSV$/i) { $endlim = "\n"; $delim = ","; }
	elsif ($delim =~ /^TSV$/i) { $endlim = "\n";$delim = "\t"; }
	my $row = 0; my $output = "";

	my $sql = qq|SELECT * from person|;
	my $sth = $dbh -> prepare($sql);
	$sth -> execute();
										
	while (my $user = $sth -> fetchrow_hashref()) { 
		my @titles; my @data;
		while (my ($ux,$uy) = each %$user) { 
			$user->{$ux} =~ s/$delim/ /ig; 		# clean data of delimiters
			$user->{$ux} =~ s/$endlim/ /ig; 		# clean data of delimiters
			if ($row == 0) { $ux =~ s/person_//; push @titles,$ux; }
			push @data,$uy;
		}
		if ($row == 0) { my $topline = join $delim,@titles; $output .= $topline . "\n"; }
		my $line = join $delim,@data; $output .= $line . "\n";
		$row++;
	}
	return $output;

}

sub delete_all_users {

	my ($dbh,$query) = @_;
	print "Content-type: text/html; charset=utf-8\n\n";					# Header
	$Site->{header} =~ s/\Q[*page_title*]\E/Delete All Users/g;
	print $Site->{header};
	print "<h1>Deleting All Users</h1>";
	print "<p>Ummm.... no. Go edit the code to allow this - line 1270 in admin.cgi</p>";
exit;

# Note - backup of subscription file needs column headers
#exit;
	
	# Save a backup file
	&error($dbh,"","","Can't get users") unless ( my $savetext = &make_user_list($dbh,$query,"TSV") );
	my $savefile = $Site->{st_cgif}."/data/".$Site->{db_name}."_person_".time;
	&error("$dbh","","","Save Users: Cannot open $savefile: $!") unless (open OUT,">$savefile");
	&error("$dbh","","","Save Users: Cannot print to $savefile: $!") unless (print OUT $savetext);
	close OUT;
	print "<p>Backup of users saved to $savefile </p>";


	# Erase all subscriptions 
	my $sql = qq|SELECT page_id FROM page WHERE page_type='email'|;
	my $sth = $dbh -> prepare($sql);
	$sth -> execute();							
	while (my $page = $sth -> fetchrow_hashref()) { 
		&autounsubscribe_all($dbh,$query,$page->{page_id},"return");
	}

	# Erase all users
	# Erase all subscriptions 
	my $sql = qq|SELECT person_id,person_status FROM person|;
	my $sth = $dbh -> prepare($sql);
	$sth -> execute();							
	while (my $user = $sth -> fetchrow_hashref()) { 
		unless ($user->{person_status} eq "admin") {
			unless ($user->{person_id} eq "2") {
				&db_delete($dbh,"person","person_id",$user->{person_id});
			}
		}
	}
	print "<p>All users (except admin) deleted.</p>";

	print $Site->{footer};
	exit;
}




# -------   User Find Form -----------------------------------------------------
#
#   Quick form to find a user

sub userfindform {

	my ($title,$action) = @_;
 
						# Permissions
						
	return unless (&is_allowed("edit","person")); 
	
						# Form
						
	$Site->{header} =~ s/\Q[*page_title*]\E/$title/g;
	return qq|Content-type: text/html; charset=utf-8\n\n|.
		$Site->{header}.
		qq|<h2>$title</h2>
		<p>Select a person to edit. Enter: 
		<form method="post" action="$Site->{st_cgi}login.cgi">
		<input type="hidden" name="action" value="$action">
		User ID number: <input type="text" name="pid" size="20"><br/><br/>
		<b>or</b> userid: <input type="text" name="ptitle" size="40"><br/><br/>
		<b>or</b> name: <input type="text" name="pname" size="40"><br/><br/>
		<b>or</b> email: <input type="text" name="pemail" size="40"><br/><br/>
		<input type="submit" value="Find User data" class="button">
		</form>|.
		$Site->{footer};

}



# -------   Import List --------------------------------------------------------

sub import {

	my ($dbh,$query,$table) = @_;

	my $vars = $query->Vars;
	print "Content-type: text/html\n\n";
	print "<h1>Importing List</h1>";
	print "Table: $table <br>";

	unless (&new_module_load($query,"Text::ParseWords")) {
		&error($dbh,"","","Text::ParseWords is not available"); 
	}


	my $file;
	if ($query->param("file_name")) { $file = &upload_file($query); }		# Uploaded File
	elsif ($vars->{file_url}) { $file = &upload_url($vars->{file_url}); }		# File from URL
	$file->{file_format} = $vars->{file_format};
	
	$file->{file_location}  = $Site->{st_urlf}.$file->{file_dir}.$file->{file_title};
	print "Got a file - $file->{file_location}  -- $file->{file_title} <p>";
	print "Format is $file->{file_format} <br>";


	my $count = 0;
	open DBIN,"$file->{file_location}" or &error($dbh,"","","Can't open $file->{file_location} $!");
	my $count = 0; my @fields;
	while (<DBIN>) {
		chomp;
#		print "$_ <br>\n";
		my @values; my $data;
		
								# Set Up Field Titles from Import File
		if ($count eq 0) { 
			if ($file->{file_format} eq "tsv") { @fields = split "\t",$_; }
			elsif ($file->{file_format} eq "csv") {	@fields = parse_csv($_); }
			else { &error($dbh,"","","File format must be csv or tsv"); }
			
			foreach my $field (@fields) {
				$field = lc($field);
				$field =~ s/ /_/g;
				$field =~ s/first_name/firstname/g;
				$field =~ s/last_name/lastname/g;
				if ($field eq "e-mail_address") { $field = "email"; }
				$field = $table ."_". $field;
			}
			$count++;
			next;
		}
		
								# Assign datafrom file to imput values
		else { 
			if ($file->{file_format} eq "tsv") { @values = split "\t",$_; }
			elsif ($file->{file_format} eq "csv") {	@values = parse_csv($_); }			

			my $innercount=0;
			foreach my $field (@fields) {
				$data->{$field} = $values[$innercount];
				$innercount++;				
			}
		}

		if ($table eq "person") {			# Special functions for person insert
		
			my ($to) = $data->{person_email};				# Check email address
				if ($to =~ m/[^0-9a-zA-Z.\-_@]\./) { 
				print "Rejected: $to is a Bad Email<br/>"; 
				next;
			}

			if (&db_locate($dbh,"person",
				{person_email => $data->{person_email}}) ) {		# Unique Email			
				print "Duplicate email: $data->{person_email}<br/>";
				next;
			}
		
			unless ($data->{person_name}) { 
				$data->{person_name} = $data->{person_firstname} . " " . $data->{person_lastname};
			}
			
			unless ($data->{person_name}) { 
				$data->{person_name} = $data->{person_email};
			}
			
			unless ($data->{person_title}) {
				$data->{person_title} = $data->{person_name};
			}
			
			unless ($data->{person_password}) {
				$data->{person_password} = &random_password();
			}
			
			unless ($data->{person_status}) {
				$data->{person_status} = "reg";
			}
		
		}
		
								# Automatically generated data
								
		$data->{$table."_crdate"} = time;
		$data->{$table."_creator"} = $Person->{person_id};
								

								# Save data to database
		$count++; 
		if ($table eq "person") { next unless ($data->{"person_email"}); }	
		
		my $ok = 0;
		$ok = &db_insert($dbh,$query,$table,$data);
#	while (my ($vx,$vy) = each %$data) { print "$vx = $vy <br>"; }
#		print "Inserting $data->{person_name} ($data->{person_email}) ($data->{person_organization}) <br>";
		if ($ok) { print "."; }

		
								# Send email
	}
	
	print " <br>";
	print "Data uploaded, $count records added.";
	exit;
# connect_page_4_subscriptions_1284638307

	

exit;


}




# -------   Parse CSV -- used by input, requires that you use Text::ParseWords ------


sub parse_csv {
    return quotewords(",",0, $_[0]);
}


# -------   Admin Database ----------------------------------------------------------

sub showcolumns {
	my ($dbh,$query,$msg) = @_;
	my $vars = $query->Vars;

#	my $alterstmt = "ALTER TABLE link MODIFY link_category varchar(255)";
#	my $asth = $dbh -> prepare($alterstmt);
#	$asth -> execute();

#	my $alterstmt = "ALTER TABLE link MODIFY link_content text";
#	my $asth = $dbh -> prepare($alterstmt);
#	$asth -> execute();



	my $colstyle = qq|<style type="text/css">#columns{
		font-family:"Trebuchet MS", Arial, Helvetica, sans-serif;
		width:100%;
		border-collapse:collapse;
		}
		#columns td, #columns th 
		{
		font-size:1em;
		border:1px solid #98bf21;
		padding:3px 7px 2px 7px;
		}
		#columns th 
		{
		font-size:1.1em;
		text-align:left;
		padding-top:5px;
		padding-bottom:4px;
		background-color:#A7C942;
		color:#ffffff;
		}
		#columns tr.alt td 
		{
		color:#000000;
		background-color:#EAF2D3;
		}
		</style>|;

	my $columns = qq|<h3>Table: $vars->{stable}</h3>\n$colstyle\n<table  id="columns" cellpadding=3 cellspacing=0 border=1">	
		<tr><td>Key</td><td>Field</td>
		<td>Type</td><td>Null</td>
		<td>Default</td><td>Extra</td></tr>\n|;
	
	my $showstmt = qq|SELECT * FROM INFORMATION_SCHEMA.COLUMNS WHERE table_name = ? AND table_schema = ? ORDER BY column_name|;
	# Replaces:  
#	my $showstmt = "SHOW COLUMNS FROM $vars->{stable}";
	
	my $sth = $dbh -> prepare($showstmt)  or die "Cannot prepare: $showstmt FOR $vars->{stable}, $Site->{db_name} " . $dbh->errstr();
	$sth -> execute($vars->{stable},$Site->{db_name})  or die "Cannot execute: $showstmt " . $dbh->errstr();
#	$sth-> execute() or die "Cannot execute: $showstmt " . $dbh->errstr();
	my $alt; # Toggle to shade table rows
	while (my $showref = $sth -> fetchrow_hashref()) { 
		if($alt) { $alt=""; } else { $alt=qq| class="alt"|;} 
		unless ($showref->{COLUMN_DEFAULT}) { $showref->{COLUMN_DEFAULT} = "none"; }
		unless ($showref->{COLUMN_KEY}) {  $showref->{COLUMN_KEY} = "-"; }
		unless ($showref->{EXTRA}) {  $showref->{EXTRA} = "-"; }

		$columns .= qq|<tr$alt><td>$showref->{COLUMN_KEY}</td><td>$showref->{COLUMN_NAME}</td><td>$showref->{COLUMN_TYPE}</td>\n|;
		$columns .= "<td>$showref->{IS_NULLABLE}</td><td>$showref->{COLUMN_DEFAULT}</td><td>$showref->{EXTRA}</td></tr>\n";


	}
	$columns .=  "</table>\n";

	# Print the result on the Database screen
	&admin_database($dbh,$query,$vars->{stable},$columns);
	exit;
}
	
sub addcolumn {
	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	my $col = $vars->{col};
	&error($dbh,"","","Column name error - cannot call a column $col") if (
		(($col+0) > 0) ||
		($col =~ /['"`#!$%&@]/)
		);
	my $tab = $vars->{stable};
	
	$dbh->do("ALTER TABLE $tab ADD $col VARCHAR( 250 ) NULL");
	#$dbh->do("ALTER TABLE $tab ADD $col text NULL");
	my $msg = "Column $col added to $tab";
	&showcolumns($dbh,$query,$msg);




}

sub removecolumnwarn {
	
	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	my $col = $vars->{col};
	my $tab = $vars->{stable};
	print "Content-type: text/html\n\n";
	print qq|<html><head></head><h1>WARNING</h1>
		<p>Are you <i>sure</i> you want to drop $col from $tab ?????</p>
		<p><b>All data</b> in $col will be lost. Never to be recovered again.</p>
		<p>You <b>cannot</b> fix this. Backcspace to get out of this.</p>
		<p>If you're <i>sure</i>, press the button:</p>
		<form method="post" action="$Site->{st_cgi}admin.cgi">
		<input type="hidden" name="col" value="$col">
		<input type="hidden" name="stable" value="$tab">
		<input type="hidden" name="action" value="removecolumndo">	
		<input type="submit" value="Remove Column">
		</form></body><html>|;	
		
}

sub removecolumndo {
	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	my $col = $vars->{col};

	&error($dbh,"","","Column name error - cannot remove $col") if (
		($col =~ /_id/) || ($col =~ /_name/) || ($col =~ /_title/) || ($col =~ /_description/)
		);
	my $tab = $vars->{stable};
	
	$dbh->do("ALTER TABLE $tab DROP COLUMN $col");
	my $msg = "Column $col dropped from $tab";

	
	&showcolumns($dbh,$query,$msg);

}


#
# -------   Refield ------------------------------------------------------------
#
# Rebuilds field_definition.pl from database
#

sub refield {

						# Permissions
						
	return unless (&is_allowed("edit","field")); 

	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
		
														# Create File Header		
														
	my $ds = '$'."base_fields";
	my $output = qq|
		sub set_base_fields {
			\$base_fields = {|;
	
														# Get Fields Data, and...
														
	my $sql = qq|SELECT * FROM field|;
	my $sth = $dbh -> prepare($sql);
	$sth -> execute();
	
														# For each field listed...
														
	while (my $ref = $sth -> fetchrow_hashref()) { 
		my $title = $ref->{field_title};
		my $type = $ref->{field_type};
		my $size = $ref->{field_size};
		next unless ($title && $type && $size);
		
														# Create field definition text
														
		$output .= qq|
				$title => {	
					title => "$title",
					type => "$type",
					size => "$size"
				},|;
	}
	
														# Create file footer
														
	$output .= qq|			};
			return \$base_fields;
			};
			1;|;

														# Print the file
		
	my $filename = $Site->{st_cgif}."/data/" . $ENV{'SERVER_NAME'} . ".field_definitions.pl";
	
	open OTPUT,">$filename" or 
		&error("$dbh","","","Cannot print fields definition file $filename: $!");
	print OTPUT $output or 
		&error("$dbh","","","Cannot print fields definition file $filename: $!");;
	close OTPUT;

														# Return to admin menu
	
	$vars->{msg} = "New field types table created.";
	&admin_menu($dbh,$query);
}

#
# -------   Refield ------------------------------------------------------------
#
# Rebuilds record cache
#

sub recache {


	my ($dbh,$query) = @_;
	my $vars = $query->Vars;

	return unless (&is_allowed("edit",$vars->{table})); 			# Get variables
	print "Content-type: text/html\n\n";

	my $format = $vars->{format};							# Set Format
	if ($vars->{type}) { $format = $vars->{type}."_".$format; }
	$format = $vars->{table}."_".$format;
	$vars->{force} = uc($format);

	my $sql = qq|SELECT * FROM $vars->{table}|;				# Select Records
	if ($vars->{type}) { $sql .= " WHERE ".$vars->{table}."_type=?"; }
	my $sth = $dbh -> prepare($sql);
	$sth -> execute($vars->{type});
# my $count=0;
	print "Record search: $sql <br /> Recaching $vars->{table} : $vars->{type} : $vars->{format} ";
	while (my $ref = $sth -> fetchrow_hashref()) { 
		my $idfield = $vars->{table}."_id";

		my $record_text = &format_record($dbh,
			$query,
			$vars->{table},
			$format,
			$ref);

#		print $record_text;
# $count++; last if ($count > 20);
		print "$ref->{$idfield} - ";
	}

	exit;

}



# -------   Admin Menu: topics ---------------------------------------------

sub admin_topics {

	return unless (&is_viewable("admin","topics")); 		# Permissions
	
	return qq|<div class="menubox">
	
		<h4>Build Content Types</h4>
		<p>
		<ul>
		<li><a href="?action=refield">Rebuild Fields List</a></li>
		</ul>
		
		<h4>Matches</h4>
		<p><b>Caution: Reindexing can take a long time</b><ul>
		<li> <a href="?action=reindex_topics">Reindex Topics</a> (Caution - this could take a long time)
		<li><a href="?action=reindex&db=author">Reindex Authors</a></li>
		<li><a href="?action=reindex&db=journal">Reindex Journals</a></li>
		</ul></p>
	
	</div>|;
	
}




# -------   Admin Nav ----------------------------------------------------------
#
#	Prints the navigation bar to create and list types of records
#

sub admin_nav {

	my ($dbh,$query) = @_;

	my @tables = $dbh->tables();
	my $output = qq|
		<div id="admincontent">
		[<a href="$Site->{script}">Admin</a>]<br/><br/>
		|;

	foreach my $table (@tables) {
		$table =~ s/`//ig;
		next unless (&is_viewable("nav",$table)); 		# Permissions

		my $numb;
		if ($table eq "feed") { $numb = "&number=1000"; }
		elsif ($table eq "page") { $numb = "&number=100"; }

		my $tname = ucfirst($table);
		my $title = "List ".$tname."s";
		$output .= qq{
			[<a href="?db=$table&action=edit">New</a>]
			[<a href="?db=$table&action=list$numb">List</a>]
			$tname <br />\n
		};
	}
	$output .= "</div>";
	return $output;
}

# -------   News Rollup ----------------------------------------------------------
#
#	Gives a quick preview of posts slated for upcoming newsletters
#

sub news_rollup {
	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	print "Content-type: text/html; charset=utf-8\n\n";
	print $Site->{header};
	print "<h1>Content for Today & Future Issues</h1>";

	# Get Data for Today and Future Issues
	my $date = &cal_date(time - (3600*24));	# ie., yesterday
	my $issues = ();
	my $stmt = qq|SELECT * FROM post where post_pub_date >?|;	
	my $sthl = $dbh->prepare($stmt);
	$sthl->execute($date);
	my $count = 0;
	while (my $post = $sthl -> fetchrow_hashref()) {
		my $text = qq|<a href="?post=$post->{post_id}">$post->{post_title}</a> 
			[<a href="?action=edit&post=$post->{post_id}">Edit</a>]|; 
		push @{$issues->{$post->{post_pub_date}}},$text;
		$count++; last if ($count>1000);	
	}

	# Sort and Display Content
	my @index = sort keys %$issues;
	foreach my $iss (@index) {
		print "<p><b>ISSUE: $iss</b><ul>\n";
		foreach my $pp (@{$issues->{$iss}}) {
			print "<li>$pp </li>\n";
		}
		print "</ul></p>\n";
	}
	print $Site->{footer};
	exit;
}


# -------   Autosubscribe All ----------------------------------------------------------
#
#	Autosubscribes all users to given newsletter
#


sub autosubscribe_all {

print "Content-type: text/html; charset=utf-8\n\n";

	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	
	print $Site->{header};
	print "<h2>Autosubscribe</h2>";
	my $page = $vars->{newsletter};
	my $stmt = qq|SELECT person_id FROM person|;
	my $pers = $dbh->selectcol_arrayref($stmt);
		
	# Delete Previous Subscriptions
	&save_subscriptions($dbh,$query);
	my $stmt2 = qq|DELETE FROM subscription WHERE subscription_box=?|;
	my $sth = $dbh->prepare($stmt2);
    	$sth->execute($page);	
		
	print "Subscribe to $page <p>";
	my $crdate = time;
	foreach my $person(@$pers) {
		&db_insert($dbh,$query,"subscription",{subscription_box => $page,
								   subscription_person => $person,
								   subscription_crdate => $crdate});

    	
		print "$person subscribed OK<br>";
	
	}
	print $Site->{footer};
exit;

}



# -------   Autosubscribe All ----------------------------------------------------------
#
#	Autosubscribes all users to given newsletter
#


sub autounsubscribe_all {

	my ($dbh,$query,$page,$return) = @_;
	my $vars = $query->Vars;
	
	unless ($return) { 
		print "Content-type: text/html; charset=utf-8\n\n"; 
		print $Site->{header}; 
		print "<h2>Autosubscribe</h2>";
	}
	$page ||= $vars->{newsletter};
	my $stmt = qq|SELECT person_id FROM person|;
	my $pers = $dbh->selectcol_arrayref($stmt);
		
	# Delete Previous Subscriptions
	&save_subscriptions($dbh,$query,$page);
	my $stmt2 = qq|DELETE FROM subscription WHERE subscription_box=?|;
	my $sth = $dbh->prepare($stmt2);
    	$sth->execute($page);	
		
	print "<p>All users unsubscribed from page number $page </p>";
	my $crdate = time;

	unless ($return) {
		print $Site->{footer};
		exit;
	}
	return;
}

sub save_subscriptions {

	my ($dbh,$query,$page) = @_;
	my $savefile = $Site->{data_dir}.$Site->{db_name}."_page_".$page."_subscriptions_".time;
	open OUT,">$savefile" or 
		&error("$dbh","","","Save subscriptions: Cannot open $savefile: $!");
	my $stmt = qq|SELECT * FROM subscription|;	
	my $sthl = $dbh->prepare($stmt);
	$sthl->execute();
	while (my $s = $sthl -> fetchrow_hashref()) {
		print OUT $s->{subscription_box}."\t".$s->{subscription_person}."\t".$s->{subscription_crdate}."\n"
		 or 
		&error("$dbh","","","Save subscriptions: Cannot write to $savefile: $!");
	
	}
	print "<p>Backup of subscriptions saved to $savefile </p>";
	close OUT;
}

# -------   List Records -------------------------------------------------------
#
# List records of a certain type
#
sub list_records {

	my ($dbh,$query,$table) = @_;
	my $vars = $query->Vars;
	my $output = "";
	
	
	
	$vars->{force} = "yes";
	$vars->{where} =~ s/[^\w\s]//ig;	# chars only, no SQL injection for you

#while (my($lx,$ly) = each %$vars) { print "$lx = $ly <br>"; }
#print "Listed<br>";


						# Output Format
	my $format = $table ."_list";

						# Print Page Header
	$output .= "<h2>List ".$table."s</h2>";

	# Search Form
	my $titname; if ($table =~ /^author$|^person$/) { $titname = "name"; }
	else { $titname = "title"; }
	$output .= qq|
		<p> <form method="post" action="$Site->{st_cgi}admin.cgi"> &nbsp; 
		<input type="hidden" name="db" value="$table">
		<input type="hidden" name="action" value="list">
		Find: <input name="where" size="40">
		Sort: <select name="sort">
		<option value="|.$table."_".$titname.qq|">$titname</option>
		<option value="|.$table.qq|_id">Oldest First</option>
		<option value="|.$table.qq|_id DESC">Newest First</option>
		</select>
		<input type="submit" value="List Again">
		</form></p>|;
	if ($vars->{where}) { $output .= "<p>Searching for  $vars->{where} </p>"; }


	if ($table eq "event") {
		my $ctz = $vars->{timezone} || $Site->{st_timezone};
		$output .= qq|<p><form method="post" action="admin.cgi">
			<input type="hidden" name="action" value="list">
			<input type="hidden" name="db" value="event">
			Time Zone: 
		|;
		
		$output .=  &tzdropdown($query,$ctz);
		$output .=  qq|<input type="submit" value="Select time zone">
			</form></p>|;
	} elsif ($table eq "page") {
		$output .=  qq|<p><form method="post" action="admin.cgi">
			<input type="hidden" name="page" value="all">
			<input type="hidden" name="action" value="publish">
			<input type="hidden" name="mode" value="report">
			<input type="submit" class="button" value="Publish all pages">
			</form></p>|;
	}

	if ($vars->{msg}) {
		$output .=  qq|<p class="notice">$vars->{msg}</p>|;
	}

						# Count Number of Items
	my $count = &db_count($dbh,$table);
						# Set Sort, Start, Number values

	my ($sort,$start,$number,$limit) = &sort_start_number($query,$table);
	$output .=  "<p>Listing $start to ".($start+$number)." of $count ".$table."s</p>";

						# Set Conditions Related to Permissions
	my $permtype = "list_".$table; my $where;
	if ($Site->{$permtype} eq "owner" && $Person->{person_status} ne "admin") {
			$where = "WHERE ".$table."_creator = '".$Person->{person_id}."'";

	} else { $where = ""; }

						# Set Search Conditions
	if ($vars->{where}) {
		my $w = "where ".$table."_".$titname." LIKE '%".$vars->{where}."%'";
		if ($where) {
			$where = "($where) AND ($w)";
		} else {
			$where = $w;
		}
	}				

						# Execute SQL search

	my $stmt = qq|SELECT * FROM $table $where $sort $limit|;	

	my $sthl = $dbh->prepare($stmt);
	$sthl->execute();
	$output .=  "<p>\n";
	while (my $list_record = $sthl -> fetchrow_hashref()) {
#print "<hr>";while (my($lx,$ly) = each %$list_record) { print "$lx = $ly <br>"; }

		#&db_update($dbh,"feed", {feed_status => "A"},$list_record->{feed_id} );

						# Format Record
						
		if ($list_record->{page_type} eq "course") {
			$format = "page_course_list";
		}


		my $record_text = &format_record($dbh,
			$query,
			$table,
			$format,
			$list_record,1);
		&make_admin_links(\$record_text);	
		&autodates(\$record_text);
						
		&autotimezones($query,\$record_text); 	# Fill timezone dates
		$output .=  $record_text;

	}


	$output .=  "</p>\n<p>\n";

	$output .=  &next_button($query,$table,"list",$start,$number,$count);
#	print &admin_nav($dbh,$query);

	$sthl->finish( );

	
	&admin_frame($dbh,$query,"List ".$table."s",$output);
}


# -------   Output Record ------------------------------------------------------


sub output_record {

	my ($dbh,$query,$table,$id_number,$format) = @_;
	my $vars = $query->Vars;
	$vars->{comment} = "yes";

											# If ID is specified as text
	if (($id_number+0) == 0) {		# Try to find by title
		$id_number = &find_by_title($dbh,$table,$id_number);
	}

	my $fields = &set_fields($table);

	
	
						# Get Record from DB

	my $wp = &db_get_record($dbh,$table,{$fields->{id}=>$id_number});
	unless ($wp) { &error($dbh,$query,"",
			qq|Looking for $table number $id_number, 
			but it was not found, sorry.|); }
			
						# Permissions
						
	return unless (&is_allowed("view",$table,$wp)); 		
		
			
						# Title
	$wp->{page_title} = $wp->{$fields->{title}} || $wp->{$fields->{name}};
	$Site->{header} =~ s/\Q[*page_title*]\E/$wp->{$fields->{title}}/g;


	

						# Set Formats

	my ($page_format,$record_format,$mime_type) =
		&set_formats($dbh,$query,$wp,$table);
		
		

						# Create Edit Links
						
	my $edit_links = qq|<p class="notice">
		Admin Options: [<a href="?$table=$id_number&action=edit">Edit</a>]
						</p>|;

						# Put Record Data Into Template 

	$wp->{page_content} = &format_record($dbh,$query,$table,$record_format,$wp);


						# For non-Page Records, Add Header and Footer


	unless ($table eq "page" || $format eq "viewer") {
		my $header_template = $Site->{lc($page_format) . "_header"} || lc($page_format) . "_header";
		my $footer_template = $Site->{lc($page_format) . "_footer"} || lc($page_format) . "_footer";
		$wp->{page_content} =
			&db_get_template($dbh,$header_template) .
			$edit_links . $wp->{page_content} .				&db_get_template($dbh,$footer_template);	
	}
	


						# Format Record Content

	$wp->{table} = $table;
	&format_content($dbh,$query,$options,$wp);

	 					# Fill special Admin links and post-cache data

	&make_pagedata($query,\$wp->{page_content});				
	&make_admin_links(\$wp->{page_content});
	&make_login_info($dbh,$query,\$wp->{page_content},$table,$id_number);
	
						# Fill timezone dates
	&autotimezones($query,\$wp->{page_content});
	
	$wp->{page_content} =~ s/\Q]]]\E/] ]]/g;   # Fixes a Firefox XML CDATA bug
	print "Content-type: ".$mime_type."\n\n";
	print $wp->{page_content};

}

# -------  Autopost------------------------------------------------------    

sub autopost {

	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	exit unless ($Person->{person_status} eq "admin");
	my $postid = &auto_post($dbh,$query,$vars->{id});
	print "Content-type: text/html\n\n";
	print "Autopost $postid";
	exit;
	
}

# -------  Autopost------------------------------------------------------    

sub postedit {

	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	exit unless ($Person->{person_status} eq "admin");
	print "Content-type: text/html\n\n";	
	my $postid = &auto_post($dbh,$query,$vars->{id});
	my $posttext = &edit_record($dbh,$query,"post",$postid,1);

 	print $posttext;
	exit;
	
}


# -------   Update Record ------------------------------------------------------                                                   UPDATE

sub update_record {

	my ($dbh,$query,$table,$id_number) = @_;
	my $vars = $query->Vars;

	
 #print "Content-type: text/html; charset=utf-8\n\n";
#while (my($vx,$vy) = each %$vars) { print "$vx = $vy <br/>"; }

						# Validate Input

	&error("nil",$query,"","Database not ready") unless ($dbh);
	&error($dbh,$query,"","Table not specified") unless ($table);
	&error($dbh,$query,"","Fishy ID") unless ($id);

							# Permissions
	
	my $id_field = $table."_id";
	my $record = &db_get_record($dbh,$table,{$id_field=>$id});
	if ($id =~ /new/i) {	return unless (&is_allowed("create",$table)); } 
	else { return unless (&is_allowed("edit",$table,$record)); }


	my $fields = &set_fields($table);


						# Clean Input
						# Fix mismatched href quotes

	$vars->{$fields->{description}} =~ s/href=('|&#39;|&apos;)(.*?)"/href="$2"/ig;	

						# Require URL in link
	if ($vars->{post_type} eq "link") {
		unless ($vars->{$fields->{link}} =~ /http/i) {
			&error($dbh,$query,"","Link must contain 'http'");
		}
	}
						# Capitalize titles in Post
	if ($table eq "post") {
		$vars->{$fields->{title}} = &capitalize($vars->{$fields->{title}});
		$vars->{$fields->{name}} = &capitalize($vars->{$fields->{name}});
		unless ($vars->{$fields->{pub_date}}) {
			$vars->{$fields->{pub_date}} = &cal_date(time); }

	} elsif ($table eq "person") {
	
		if ($vars->{$fields->{password}}) {		# Create a Salted Password
			$vars->{$fields->{password}} = &encryptingPsw($vars->{person_password}, 4);
			
		}
	}
	


						# Kill spartquotes	
	while (my ($vkey,$vval) = each %$vars) {
		$vars->{$vkey} =~ s/\0/,/g;	# Replace 'multi' delimiter with comma
		$vars->{$vkey} =~ s/#!//g;				# No programs!
	#	$vars->{$vkey} =~ s/“/"/g;	# "
	#	$vars->{$vkey} =~ s/”/"/g;	# "
	#	$vars->{$vkey} =~ s/’/-/g;	# '
	#	$vars->{$vkey} =~ s/‘/'/g;	# '
	#	$vars->{$vkey} =~ s/—/--/g;	# '
	#	$vars->{$vkey} =~ s/»/&gt;&gt;/g;	# '	
	#	$vars->{$vkey} =~ s/\x{fffd}//g;	

		# $vars->{$vkey} =~ s/.../.../g;	# '				
		#$vars->{$vkey} = &de_cp1252($vars->{$vkey});
	}

						# Create title for mappings
	if ($table eq "mapping") {
		if ($vars->{mapping_stype} eq "mapping_specific_feed") {
			my $feed_title = &db_get_single_value($dbh,"feed","feed_title",
				$vars->{mapping_specific_feed});
			$vars->{mapping_title} = $feed_title .
				" -> ". $vars->{mapping_dtable};
		} else {
			$vars->{mapping_title} = $vars->{$vars->{mapping_stype}}.
				" -> ". $vars->{mapping_dtable};
		}
	}

					# Create mappings for mappings
	my $pref = $vars->{mapping_prefix};
	my $preff = $pref."_";
	my $mapping_mappings = "";

	while (my($px,$py) = each %$vars) {
		if ($px =~ /$preff/) {

			next unless ($py); next if ($py eq "null");
			if ($mapping_mappings) { $mapping_mappings .= ";"; }
			$mapping_mappings .= $px.",".$py;
		}
	}
	$vars->{mapping_mappings} = $mapping_mappings;

					# Create values for mappings
					# new values
	my $mapping_values = "";				
	if ($vars->{mapping_tval_field} && $vars->{mapping_tval_value}) {
		$mapping_values = $vars->{mapping_tval_field}.",".
			$vars->{mapping_tval_value};
	}		
					# existing values
	while (my($vx,$vy) = each %$vars) {
		if ($vx =~ /mapping_value/) {
			next unless ($vy); next if ($vy eq "null");
			if ($mapping_values) { $mapping_values .= ";"; }
			$vx =~ s/mapping_value_//;
			$mapping_values .= $vx.",".$vy;
		}
	}
	$vars->{mapping_values} = $mapping_values;					

	if ($id_number eq "new") {			# Uniqueness Constraints
		my $l = "";
		if (($l = &db_locate($dbh,"post",{post_link => $vars->{post_link}}))        ||
		    ($l = &db_locate($dbh,"author",{author_name => $vars->{author_name}}))  ||	
		    ($l = &db_locate($dbh,"feed",{feed_link => $vars->{feed_link}})) 	) {
			&error($dbh,"","",
				qq|<p>Duplicate Entry: <a href="$Site->{st_cgi}admin.cgi?$table=$l">$table $l</a></p><p>If you would like to edit the existing
					$table then please <a href="$Site->{st_cgi}admin.cgi?$table=$l&action=edit">Click here</a></p>|);
			exit;
		}
	}

	$id_number = &form_update_submit_data($dbh,$query,$table,$id_number);



						# Identify, Save and Associate File

	my $file;
	
	if ($query->param("file_name")) { $file = &upload_file($query); }		# Uploaded File
	elsif ($vars->{file_url}) { $file = &upload_url($vars->{file_url}); }		# File from URL

	
	# Create File Record
	
	if ($file) {
		my ($ffdev,$ffino,$ffmode,$ffnlink,$ffuid,$ffgid,$ffrdev,$ffsize, $ffatime,$ffmtime,$ffctime,$ffblksize,$ffblocks)
			= stat($file->{fullfilename});
		my $mime; 
		if (&new_module_load($query,"MIME::Types")) { 
			use MIME::Types;
			my MIME::Types $types = MIME::Types->new;
			my MIME::Type  $m = $types->mimeTypeOf($file->{fullfilename});	
			$mime = $m;		
		} else {
			$mime="Unknown; install MIME::Types module to decode upload file mime types";
			$vars->{msg} .= "Could not determine mime type of upload file; install MIME::types module<br>";
		}				
		
		if ($file->{filetype} eq "image") { $file->{file_type} = "Illustration"; } 
		else { $file->{file_type} = "Enclosure"; }
		
		$vars->{file_align} ||= "left";
		$vars->{file_width} ||= "150";
		$vars->{file_link} ||= $vars->{$fields->{link}};
		
		# Create File Record
		my $file_id = &db_insert($dbh,$query,"file",{file_title => $file->{file_title},
					file_dirname => $file->{file_dir}.$file->{file_title},
					file_dir => $file->{file_dir},
					file_mime => $mime,
					file_size => $ffsize,
					file_post => $id_number,
					file_link => $vars->{file_link},
					file_crdate => time,
					file_creator => $Person->{person_id},
					file_type => $file->{file_type},
					file_width => $vars->{file_width},
					file_align => $vars->{file_align}});
		$vars->{msg} .= "File $upload_filename inserted as file number $file_id <br>";
	}
	



						# Insert Topic Matches
	if (($table eq "post") || ($table eq "link")) {
		my $matchstr = $vars->{$fields->{title}} . $vars->{$fields->{description}};
#		&insert_topic_matches($dbh,$query,$matchstr,$table,$id_number);
#		my $matchstr = $vars->{$author};

						# Topic Matches

#		my ($matchmsgstr,$matchmsgids) =
#			&insert_matches($dbh,$query,$vars->{$title}.$vars->{$description},
#				$table,$id_number,"topic","");
#		$vars->{$table."_authorstr"} = $matchmsgstr;
#		$vars->{$table."_authorids"} = $matchmsgids;

						# Author Matches

#		my ($matchmsgstr,$matchmsgids) =
#			&insert_matches($dbh,$query,$vars->{$author},$table,$id_number,"author","");
#		$vars->{$table."_authorstr"} = $matchmsgstr;
#		$vars->{$table."_authorids"} = $matchmsgids;


						# Journal Matches

#		my ($matchmsgstr,$matchmsgids) =
#			&insert_matches($dbh,$query,$vars->{$journal},$table,$id_number,"journal","");
#		$vars->{$table."_journalstr"} = $matchmsgstr;
#		$vars->{$table."_journalids"} = $matchmsgids;


						# Update the input item with matches

#		$id_number = &db_update($dbh,$table, $vars, $id_number);
	}



						# If Topic, Reindex Topic

	if (($table eq "topic") && ($vars->{topic_reindex} eq "yes")) {

		&reindex_topics($dbh,$query,$id_number);
		$vars->{msg} .= "Topic number $id_number successfully reindexed.<br/>";
	}
	
						# If publish selected, publish
						
	if ($vars->{publish_post}) {
		my $text = $vars->{$fields->{description}};
		my $url = $Site->{st_url}.$table."/".$id_number;
		&publish_post($dbh,$query,$text,$url,$vars->{publish_post});
	
	}
#	print "Content-type: text/html; charset=utf-8\n\n";

	$vars->{updated_table} = $table;
	$vars->{updated_title} = $vars->{$fields->{title}};
	return $id_number;
}


# -------   Upload File --------------------------------------------------------------

sub upload_file {
	
	
	my ($query) = @_;
	
	my $file = gRSShopper::File->new();
	$file->{file_title} = $query->param("file_name");

	$file->{file_dir} = $Site->{st_urlf} . "uploads";
	unless (-d $file->{file_dir}) { mkdir $upload_dir, 0755 or die "Error 1857 creating upload directory $file->{file_dir} $!"; }
	unless ($file->{file_title}) { $vars->{msg} .= " No file was uploaded."; }

	# Prepare Filename 	
	my ( $ffname, $ffpath, $ffextension ) = fileparse ( $file->{file_title}, '\..*' );  
	$file->{file_title} = $ffname . $ffextension;
	$file->{file_title} = &sanitize_filename($dbh,$file->{file_title});

	# Set File Upload Directory
	($file->{filetype},$file->{file_dir}) = &file_upload_dir($ffextension);
	my $fulluploaddir = $Site->{st_urlf} . $file->{file_dir};
	unless (-d $fulluploaddir) { mkdir $fulluploaddir, 0755 or die "Error 1867 creating upload directory $fulluploaddir $!"; }
		
	# Store the File
	my $upload_filehandle = $query->upload("file_name");
	$upload_filedirname = $file->{file_dir}.$file->{file_title};
	$upload_fullfilename = $Site->{st_urlf}.$upload_filedirname;
		

	open ( UPLOADFILE, ">$upload_fullfilename" ) or &error($dbh,"","","Failed to upload $upload_fullfilename $!");  
	binmode UPLOADFILE;  
	while ( <$upload_filehandle> ) { print UPLOADFILE; } 
	close UPLOADFILE;
		
	return $file;


}


# -------   Upload URL ---------------------------------------------------------------

sub upload_url {

	my ($url) = @_;
	return unless ($url);
	
	my $file = gRSShopper::File->new();
	
	# Prepare Filename 
	my @parts = split "/",$url; 										
	$file->{file_title} = pop @parts;
	$file->{file_title} = &sanitize_filename($dbh,$file->{file_title});

	# Set File Upload Directory
	my @pparts = split /\./,$file->{file_title};
	my $ffextension = "." . pop @pparts;			
	($file->{filetype},$file->{dir}) = &file_upload_dir($ffextension);
	my $fulluploaddir = $Site->{st_urlf} . $file->{dir};
	unless (-d $fulluploaddir) { mkdir $fulluploaddir, 0755 or die "Error 1892 creating upload directory $upload_dir $!"; }
	$file->{filedirname} = $file->{file_dir}.$file->{file_title};
	$file->{fullfilename} = $Site->{st_urlf}.$file->{filedirname};

	# Get and Store the File
	my $result = getstore($vars->{file_url},$file->{fullfilename});
	unless ($result eq "200") { &error($dbh,"","","Error $result while trying to download $vars->{file_url} "); }

	return $file;

}

# -------   Sanitize Filename --------------------------------------------------------


sub sanitize_filename {

	my ($dbh,$filename) = @_; 
	my $safe_filename_characters = "a-zA-Z0-9_.-";

	$filename =~ tr/ /_/;  
	$filename =~ s/[^$safe_filename_characters]//g;
	if ( $filename =~ /^([$safe_filename_characters]+)$/ )  { $filename = $1;  }  
	else { &error($dbh,"","","Filename $filename contains invalid characters"); }

	return $filename;

}

# -------   Set File Upload Directory --------------------------------------------------------

sub file_upload_dir {

	my ($ff) = @_;
	my $filetype = "";
	my $dir = "";

	if ($ff =~ /\.jpg|\.jpeg|\.gif|\.png|\.bmp|\.tif|\.tiff/i) { 
		$filetype = "image"; $dir = $Site->{up_image}; 
	} elsif ($ff =~ /\.doc|\.txt|\.pdf/i) {
		$filetype = "doc"; $dir = $Site->{up_docs}; 
	} elsif ($ff =~ /\.ppt|\.pps/i) {
		$filetype = "slides"; $dir = $Site->{up_slides}; 
	} elsif ($ff =~ /\.mp3|\.wav/i) {
		$filetype = "audio"; $dir = $Site->{up_audio}; 
	} elsif ($ff =~ /\.flv|\.mp4|\.avi|\.mov/i) {
		$filetype = "video"; $dir = $Site->{up_video}; 
	} else {
		$filetype = "other"; $dir = $Site->{up_files}; 
	}

	return ($filetype,$dir);
}

# -------   Edit Record --------------------------------------------------------
#
# Administrator's general record editing function
#

sub edit_record {

						# Get variables
						
	my ($dbh,$query,$table,$id_number,$viewer) = @_;
	my $id; my $id_value;						# Not needed, but let's wipe out the value
										# in case they're used accidentally. Heh
	my $vars = $query->Vars;
	$vars->{force} = "yes";	# Never use cache on edit

	# print "Content-type: text/html; charset=utf-8\n\n";




						# Special Function to Define Mappings
	if ($table eq "mapping") { 
	
		&edit_mapping($dbh,$query,$table,$id_number,$id_value);
		return;
	}
	
						# Define Form Contents


 						
	my $showcols = {
		author => ["name","nickname","email","twitter","linkedin","delicious","flickr","youtube","opensocialuserid","link","crdate","creator","description","submit"],
		box => ["title","description","content","submit"],
		chat => ["description","signature","shown","creator","crip","crdate","thread"],
		event => ["title","identifier","link","type","group","start","finish","star","host","description","submit"],
		field => ["title","type","size","submit"],
		file => ["title","dirname","link","mime","type","size","align","width","crdate","post","description","submit"],
		feed => ["title","link","html","baseurl","category","genre","type","class","autocats","creator","author","authorname","authoremail","authorurl","rules","lastharvest","copyright","timezone","country","status","tag_req","description","submit"],
		graph => ["type","tableone","idone","urlone","tabletwo","idtwo","urltwo","crdate","submit"],
		journal => ["title","link","description","submit"],
		link => ["title","link","hits","total","author","category","genre","authorname","authorurl","post","copyright","status","feedid","feedname","crdate","issued","modified","type","description","submit","content"],
		lookup => ["taba","ida","tabb","idb","type","submit"],
		media => ["title","url","type","mimetype","link","size","description","submit"],
		person => ["name","title","password","openid","status","email","description","submit"],
		optlist => ["title","table","field","data","list","default","type","submit"],
		page => ["title","header","footer","feed","type","submit","code","description"],
		person => ["name","title","password","openid","status","email","socialnet","description","submit"],
		post => ["title","link","description","submit","author","authorname","journal","journalname","pub_date","category","genre","class","type","image_file","submit","content"],
		publication => ["title","link","author_name","journal_name","volume","pages","publisher_name","type","category","catdetails","crdate","nrc_number","post","submit","description"],
		presentation => ["category","catdetails","title","link","author","conference","location","crdate","attendees","cattendees","slides","slideshare","audio","video","org","description","submit","audio_player","slide_player","video_player"],
		project => ["title","crdate","completion","description"],		
		task => ["title","due","length","priority","project","status","completed","description","submit"],		
		template => ["title","description","submit"],
		theme => ["title","submit"],
		thread => ["title","description","tag","refresh","textsize","updated","current","srefresh","supdated","active","status","submit"],
		topic => ["title","where","reindex","type","description","submit"],
		view => ["title","text","submit"]
	};


	my $form_text = &form_editor($dbh,$query,$table,$showcols,$id_number);
	
#	my $output = $Site->{header}.$form_text.$Site->{footer};
#	$form_text =~ s/&apos;/'/mig;					
	$form_text =~ s/&#39;/'/mig;					
#	&clean_up(\$form_text,"html");
	if ($viewer) { return $form_text; }							# Send form text to viewer, or
	else { &admin_frame($dbh,$query,"Edit $table",$form_text); } 				# Print Output

	
	
}

# -------  Mapping -------------------------------------------------------------

# For to create a mapping from a data source to a content type

sub edit_mapping {

						# Get Data
						
	my ($dbh,$query,$table,$id_number,$id_value,$record) = @_;
	my $vars = $query->Vars;
	return unless (&is_allowed("edit","mapping")); 		# Permissions
	my $mapping = &db_get_record($dbh,"mapping",{mapping_id=>$id_number});
	my $fields = &set_fields($table);
	
#while (my($mx,$my) = each %$mapping) { print "$mx = $my <br>"; }

						# Print Form Heading
	print qq|
 		 <form method="post" action="$Site->{script}">
		 <input type="hidden" name="table" value="mapping">
		 <input type="hidden" name="id" value="$id_number">
		 <input type="hidden" name="action" value="update">\n|;
				
						# Print Editing Screen
	print &map_instructions($dbh,$query,$mapping); 
	print &map_form_source($dbh,$query,$mapping); 
	print &map_form_destination($dbh,$query,$mapping); 
	if ($mapping->{mapping_mappings}) { print &map_form_field_values($dbh,$query,$mapping); }
	if ($mapping->{mapping_dtable}) { print &map_form_mappings($dbh,$query,$mapping); }


						# Print Form Footing	
	print &form_submit();
	print $Site->{footer};
	exit;

}

# -------  Mapping Select Source ---------------------------------------------


sub map_form_source {

	my ($dbh,$query,$mapping) = @_;
	my $vars = $query->Vars;

	my $input_type_selected = {};
	$input_type_selected->{$mapping->{mapping_stype}} = " checked";

#while (my($mx,$my) = each %$mapping) { print "$mx = $my <br>"; }
	my $output = qq|<hr><h4>Define Mapping Source Feeds</h4>
		<p>A mapping will be executed provided a certain input condition is met. Here we 
		define what that condition may be. You can select a feed if it is a...
		<dl>
		<table border=1 cellpadding=5 cellspacing=0 style="color:#91c6e7">|;

						# Specific Feed
	my $mapfeedid = $mapping->{mapping_specific_feed};
	$output .= qq|<tr>
		<td valign="top" width="25%">
		<input type="radio" name="mapping_stype" value="mapping_specific_feed"  
		$input_type_selected->{mapping_specific_feed}>
		Specific Feed:</td>
		<td valign="top" width="75%">
		<select name="mapping_specific_feed" >|;
		
	my $stmt = qq|SELECT feed_id,feed_title FROM feed ORDER BY feed_title|;
	my $sth = $dbh->prepare($stmt);
	$sth->execute();
	while (my $feed = $sth -> fetchrow_hashref()) {
		my $selected; if ($mapfeedid eq $feed->{feed_id}) { $selected = " selected"; }
		my $ft = substr($feed->{feed_title},0,35);
		$output .= qq|<option value="$feed->{feed_id}" $selected> $ft </option>\n|;
	}
	$output .=  qq|</select></td></tr>|;

						# Feed Type
	$output .= qq|<tr>
		<td valign="top" width="25%">	
		<input type="radio" name="mapping_stype"  value="mapping_feed_type"  
		$input_type_selected->{mapping_feed_type}> Feed Type</td>
		<td valign="top" width="75%">
		<input type="text" name="mapping_feed_type" 
		value="$mapping->{mapping_field_type}" size="40">
		[<a href="Javascript:alert('Enter feed types (eg., rss, opml, atom, ical)');">Help</a>]
		</td></tr>|;


						# Feed Field
	$output .= qq|<tr>
		<td valign="top" width="25%">	
		<input type="radio" name="mapping_stype" value=mapping_feed_fields  
		$input_type_selected->{mapping_feed_fields}> Feed Fields</td>
		<td valign="top" width="75%">
		<input type="text" name="mapping_feed_fields" 
		value="$mapping->{mapping_feed_fields}" size="40">
		[<a href="Javascript:alert('Enter field (eg., enclosure, start_date, width)');">Help</a>]
		</td></tr>|;


						# Feed Field Value Pair
	$output .= qq|<tr>
		<td valign="top" width="25%">	
		<input type="radio" name="mapping_stype" value="mapping_feed_value_pair"  
		$input_type_selected->{mapping_feed_value_pair}> Value Pair</td>
		<td valign="top" width="75%">
		<input type="text" name="mapping_field_value_pair" 
		value="$mapping->{mapping_field_value_pair}" size="40">
		[<a href="Javascript:alert('Enter a field and a value (eg., title:OLDaily)');">Help</a>]
		</td></tr>|;


	$output .= qq|</table></dl></p>|;
	return $output;
}



# -------  Map Form Field Values -----------------------------------------------

sub map_form_field_values {

	my ($dbh,$query,$mapping) = @_;
	my $vars = $query->Vars;
	my @dest_columns = &db_columns($dbh,$mapping->{mapping_dtable});

	my $output = qq|<h4>Set Destination Table Values</h4>
		<p>When a new destination record is created, these values will be set:</p><dl>
		<table border=1 cellpadding=5 cellspacing=0 style="color:#91c6e7">\n
		<tr><td><i>Field Name</i></td><td><i>Value</td></tr>|;	
		
						# get existing values, if any, and display
	my @existing;					
	my $tvals = $mapping->{mapping_values};
	my @tvallist = split ";",$tvals;
	foreach my $tval (@tvallist) {
		my ($tvfield,$tvval) = split ",",$tval;
		my $elname = "mapping_value_".$tvfield;
		$output .= qq|<tr><td align="right">$tvfield</td>
					<td><input name="$elname" type="text" size="20"
					value="$tvval"></td></tr>|;
		push @existing,$tvfield;			
	}
	
						# print blank for new value
	$output .=  qq|<tr><td align="right"><select name="mapping_tval_field">|;
	foreach my $dc (@dest_columns) {
			next if $dc =~ /\Q_id\E/i;
			next if (&index_of($dc,\@existing) >= 0);	
			my $match = $dc;
			my $prefix = $mapping->{mapping_dtable}."_";
			$match =~ s/\Q$prefix\E//;
			$output .=  qq|<option value="$dc">$match</option>\n|;
		}
	$output .=  qq|</select></td><td><input name="mapping_tval_value"
		type="text" size="20"></td></tr></table></dl><br/>|;
	
	return $output;				


}



# -------  Map Form Mappings -----------------------------------------------

sub map_form_mappings {

	my ($dbh,$query,$mapping) = @_;
	my $vars = $query->Vars;
	
	my $mapping_prefix = $mapping->{mapping_prefix} || "link";  	# Set prefix and define source columns
	my @source_columns = ();	
	if ($mapping_prefix eq "link") {
		@source_columns = qw|title description type link category guid created issued author authorname authorurl modified base localcat feedid feedname lat long owner_url identifier parent star host sponsor sponsor_url access start finish|;
	}

	
						# get column list for destination
						
	my @dest_columns = &db_columns($dbh,$mapping->{mapping_dtable});	
	
						# print options table headings
	my $output = qq|<h4>Map Table Elements</h4>
		<dl><table border=1 cellpadding=5 cellspacing=0 style="color:#91c6e7">\n
		<tr><td><i>Source</i></td><td>&nbsp;</td><td><i>Destination: $mapping->{mapping_dtable}</i></td></tr>|;	
		
						# Set up hash of existing mappings
	my $mapping_hash = {};
	my @mappinglist = split ";",$mapping->{mapping_mappings};
	foreach my $ml (@mappinglist) {
		my ($mlf,$mlv) = split ",",$ml;
			$mapping_hash->{$mlf} = $mlv;
	}
		
						# print table
	foreach my $sc (@source_columns) {
		next if $sc =~ /\Q_id\E/i;
		my $sp = $mapping_prefix . "_";
		$sc =~ s/\Q$sp\E//;
		my $spc = $mapping_prefix."_".$sc;
		$output .= qq|<tr><td align="right">$sc</td><td> ---> </td>\n|;
		$output .= qq|<td><select name="$spc">\n|;
		$output .= qq|<option value="null"></option>\n|;		
		foreach my $dc (@dest_columns) {
		
			# Create option text
			next if $dc =~ /\Q_id\E/i;
			my $match = $dc;
			my $prefix = $mapping->{mapping_dtable}."_";
			$match =~ s/\Q$prefix\E//;
				
			# print the option	
			$output .=  qq|<option value="$dc"|;
			if ($mapping_hash->{$spc} eq $dc) {		# Print existing mappings
				$output .=  " selected";
			} else {									# Autogenerate new mappings
				if ($sc eq $match) { $output .=  " selected"; }
			}
			$output .=  qq|>$match</option>\n|;
			
		}
	
		$output .=  qq|</select></td></tr>|;
	}
	$output .=  "</table></dl>";
	return $output;
}






# -------  Mapping Select Destination -------------------------------------------

sub map_form_destination {

	my ($dbh,$query,$mapping) = @_;
	my $vars = $query->Vars;

	my $output =  qq|<h4>Define Destination Table</h4>
		<p>Select a destination table: 
		<select name="mapping_dtable">\n|;
		
						# Define list of destination tables
	my @tables = qw|author box event feed file journal link page person post presentation publication project task template topic|;
		
						# Print list of destination tables
	foreach my $t (@tables) {
		my $sel = "";
		if ($t eq $mapping->{mapping_dtable}) { $sel = " selected"; }
		$output .= qq|<option value="$t"$sel>$t</option>\n|;
	}
	$output .= qq|</select></p>\n|;

						# Mapping Priority
	my $priority = $mapping->{mapping_priority} || 1;
	$output .=  qq|<h4>Define Mapping Priority</h4>
		<p>Higher Number = Higher Priority. <b>Priority:
		<input type="text" name="mapping_priority" value="$priority" size="5"></p>|;	

	return $output;

}











	

# -------  Mapping Instructions -----------------------------------------------
	
sub map_instructions {

	my ($dbh,$query,$mapping) = @_;
	my $vars = $query->Vars;

	my $output = qq|
		<h1>Edit Feed Mapping</h1>
		<p>A <i>mapping</i> is a way to direct where you want harvested data
		to be stored. The mapping source is always a feed, while the mapping
		destination is always a database table.</p>|;
	if ($vars->{new_dtable}) {
		$output .=  qq|<p>You have now selected a new mapping source and destination table. Now, 
				specify mapping from input fields to output fields. Some default
                        mappings have been suggested.</p>|;
	}

	$output .= "<p>Editing: <b>". ($mapping->{mapping_title} || "New Mapping") ."</b></p>";
	return $output;

}


















# -------  Delete a Record -----------------------------------------------------

# gets rid of a record forever, and doubles as a spamcatcher

sub delete_record {
	my ($dbh,$query,$table,$id) = @_;
	my $vars = $query->Vars;

	
						# Get Record from DB

	my $fields = &set_fields($table);
	my $wp = &db_get_record($dbh,$table,{$fields->{id}=>$id});
	unless ($wp) { &error($dbh,$query,"",
			qq|Looking for $table $fields->{id} number $id, 
			but it was not found, sorry.|); }
			
						# Permissions
						
	return unless (&is_allowed("delete",$table,$wp)); 
	
						# Ban spam sender IP
	my $banned;
	if ($vars->{action} eq "Spam") {
		my $bs=(); 
		$bs->{banned_sites_ip} = &db_record_crip($dbh,$table,$id);
		&db_insert($dbh,$query,"banned_sites",$bs);
		$banned = $bs->{banned_sites_ip}.
			" added to the list of banned sites.";
	}
	
						# Delete the record
	&db_delete($dbh,$table,$table."_id",$id);
	
						# Delete related graph entries
						
	my $sql = "DELETE FROM graph WHERE graph_tableone=? AND graph_idone = ?";
	my $sth = $dbh->prepare($sql);
    	$sth->execute($table,$id);
	my $sql = "DELETE FROM graph WHERE graph_tabletwo=? AND graph_idtwo = ?";
	my $sth = $dbh->prepare($sql);
    	$sth->execute($table,$id);						

	$vars->{msg} .= "Record $id deleted. $banned";
	
	&list_records($dbh,$query,$table);
	exit;
}

#--------------------------------------------------------
#
#	Feed Functions
#
#--------------------------------------------------------


# -------  Approve Feed --------------------------------------------------------

sub approve_feed {
	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	
	# Permission
	return unless (&is_allowed("approve","feed")); 
	
	$vars->{number} = "1000";
	
	&error($dbh,$query,"","Feed not specified") unless ($vars->{feed});
	&db_update($dbh,"feed",{feed_status=>"A"},$vars->{feed});

	# Clear out cache
	my $sql = "DELETE FROM cache WHERE cache_title = ?";
	my $sval = "RECORD_feed_".$vars->{feed}."_FEED_LIST";
	my $sth = $dbh->prepare($sql);
    	$sth->execute($sval);

	&db_update($dbh,"feed",{feed_status=>"A"},$vars->{feed});
	$vars->{msg} .= "Feed number $vars->{feed} approved.";
	&list_records($dbh,$query,"feed");



	return;
}

# -------  Retire Feed --------------------------------------------------------

sub retire_feed {
	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	$vars->{number} = "1000";

	&error($dbh,$query,"","Feed not specified") unless ($vars->{feed});

				# Get Record from DB

	my $wp = &db_get_record($dbh,"feed",{feed_id=>$vars->{feed}});
	unless ($wp) { &error($dbh,$query,"",
			qq|Looking for $table number $vars->{feed}, 
			but it was not found, sorry.|); }
			
				# Permission
				
	return unless (&is_allowed("retire","feed",$wp)); 

				# Update Status

	&db_update($dbh,"feed",{feed_status=>"R"},$vars->{feed});

				# Clear out cache
	
	my $sql = "DELETE FROM cache WHERE cache_title = ?";
	my $sval = "RECORD_feed_".$vars->{feed}."_FEED_LIST";
	my $sth = $dbh->prepare($sql);
    	$sth->execute($sval);

	$vars->{msg} .= "Feed number $vars->{feed} retired.";
	&list_records($dbh,$query,"feed");
	return;
}

# -------  Count  --------------------------------------------------------

# Counts the number of items in feeds, journals, whatever
# If feed specified, returns the value, otherwise, simply updates DB
# ie., counting X in Y

sub count_feed {
print "Content-type: text/html; charset=utf-8\n\n";
	my ($dbh,$query) = @_;

	my $X = $vars->{count};
	my $Y = $vars->{in};

	my $idfield = $X."_id";
	my $id = $vars->{$idfield};
	my $tracefield = $Y."_".$X."id";
	my $countfield = $X."_".$Y."s";			# eg. feed_links

	if ($id) {
		my $count = &db_count($dbh,$Y,{$idfield => $id});
		return $count;
	} else {
		my $stmt = qq|SELECT $idfield from $X|;
		my $Xs = $dbh->selectcol_arrayref($stmt);
		foreach my $xitem (@$Xs) {
			my $count = &db_count($dbh,$Y,"WHERE $tracefield = '$xitem'");
			&db_update($dbh,$X,{$countfield => $count},$xitem);
		}
		$vars->{msg} .= "Number of $X counted for each $Y and database updated.";
	}

	&admin_menu($dbh,$query);
}

#--------------------------------------------------------              
#
#       CRON TASKSNEWSLETTER
#
#	Cron Functions
#	Perform Cron Function once a minute
#
#--------------------------------------------------------

sub cron_tasks {
	
	my ($dbh,$query) = @_;	
	

	my $log = 0;	# Flag that indicates whether an activity was logged
	
	#my $content = "Cron Report \n\n";
	#$content .= "Site Context: $Site->{context} \n\n";
	#$content .="0 $ARGV[0] 1 $ARGV[1] 2 $ARGV[2] 3 $ARGV[3] \n";

										# Confirm cron key
	unless ($Site->{cronkey} eq $ARGV[1]) {
		print "Error: Cron key mismatch. $ARGV[1] must match the value of the cronkey set in $ARGV[0] admin \n";
		&send_email("stephen\@downes.ca","stephen\@downes.ca","Cron Error - $Site->{st_url}","Error: Cron key mismatch. $ARGV[1] must match the value of the cronkey set in $ARGV[0] admin : $Site->{cronkey}\n");			
		exit;
	}
	
										# Get the time
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my @wdays = qw|Sunday Monday Tuesday Wednesday Thursday Friday Saturday|;
	my $weekday = @wdays[$wday]; 
	if ($min < 10) { $min = "0".$min; }
	if ($mday < 10) { $mday = "0".$mday; }	
	

										# Autopublish
	my $asql=""; my $amode;									
	if ($weekday eq "Sunday" && $hour eq "23" && $min eq "54") 
		{ $amode = "Weekly"; $asql = qq|SELECT * FROM page WHERE page_autopub='yes' AND page_autowhen='Weekly'|; }
	elsif ($hour eq "23" && $min eq "50") { $amode = "Daily";  $asql = qq|SELECT * FROM page WHERE page_autopub='yes' AND page_autowhen='Daily'|; } 
	elsif ($min eq "35") { $amode = "Hourly"; $asql = qq|SELECT * FROM page WHERE page_autopub='yes' AND page_autowhen='Hourly'|; }
	
	if ($asql) {
		my $asth = $dbh -> prepare($asql);		
		$asth->execute();
		if ($dbh->errstr()) { &send_email("stephen\@downes.ca","stephen\@downes.ca","Autopublish Error",$dbh->errstr()); }
		while (my $npage = $asth -> fetchrow_hashref()) { 
			&publish_page($dbh,$query,$npage->{page_id},0);	
			$log = &log_cron("Autopublish $npage->{page_id} - $npage->{page_title}\n");
		}		
		$asth->finish;
		
		
	}
	
	
										# Newsletters
										
	my $sql = qq|SELECT * FROM page WHERE page_subhour=? AND page_submin=? AND (page_subwday LIKE ? OR page_submday LIKE ?)|;
	my $sth = $dbh -> prepare($sql);

	$sth -> execute($hour,$min,'%'.$weekday.'%','%'.$mday.'%');	

	while (my $npage = $sth -> fetchrow_hashref()) { 
		next unless ($npage->{page_subsend} eq "yes");
		my $report = &send_nl($dbh,$query,$npage->{page_id},"subscribers",0);
		$log = &log_cron("Sent newsletter - $npage->{page_title}\n");			
	}
	$sth->finish;
	


										# Harvester
	if ($Site->{st_harvest_on} eq "yes") {	
	

		my $dividend = ($mday * 24 * 60) + ($hour * 60) + $min;
		my $divisor = $Site->{st_harvest_int}; $divisor ||= 60;
		if ($dividend % $divisor == 0) { 
			$hn = "Harvesting";
			my $harvester = $Site->{st_cgif} . "harvest.cgi";
			my $siteurl = $Site->{site_url}; $siteurl =~ s|http://||;$siteurl =~ s|/||;
			my $status = system($harvester,$siteurl,"queue");	
			$log = 1; # Cron log entry completed in harvest.cgi
		}
	} 


	$Site->{log_items} eq "yes";	
	
										# Daily Tasks
	if ($hour eq "0" && $min eq "0") {
		
		&rotate_hit_counters($dbh,$query,"post");			# Rotate hit counters
		
		if ($Site->{log_items} eq "yes") {				# Daily items harvested log
		
			&admin_report($dbh,$query);
		
		}
		
	}
	
	
#	unless ($log) { &log_cron($log); }  # Sends empty log report
	

	
	
	exit;
}



#--------------------------------------------------------                                                                #      NEWSLETTER
#
#	Newsletter Functions
#
#--------------------------------------------------------

sub publish_post {

	my ($dbh,$query,$text,$url,$destination) = @_;
	my $vars = $query->Vars;

	if ($destination eq "twitter") { 
		&post_to_twitter($text,$url);
	} elsif ($destination eq "rss") {
		my $pages = &db_locate_multiple($dbh,"page",{page_type=>'rss'});
		foreach my $page (@$pages) { 
			$vars->{mode} eq "silent";

			&publish_page($dbh,$query,$page,"silent"); 
		}

	      $vars->{msg} .= qq|Updated RSS Feeds|;
   
	}
}

sub send_nl {
	
	my ($dbh,$query,$page_id,$send_list,$verbose) = @_;
	my $vars = $query->Vars;
	my $report = "Send Newsletter\n\n";
	
	return unless (&is_allowed("send","newsletter"));	# Admin Only 		
	
	$page_id ||= $vars->{page_id};				# ID of page to send
	$send_list ||= $vars->{send_list};				# Send to admin or subscribers
	$verbose ||= $vars->{verbose};				# Silent (0) (for cron) or verbose (1)
	my $date = &nice_date(time);
	my $today = &day_today;

	if ($verbose) { 					# Print web page header
		$Site->{header} =~ s/\Q[*page_title*]\E/Send Newsletter/g;
		print "Content-type: text/html; charset=utf-8\n\n"; 
		print $Site->{header};
		print "<h2>Send Newsletter</h2>";
		print "<p>Today is $today, $date.</p>";
	}	
	
								# Get newsletter page data
	my $record = &db_get_record($dbh,"page",{page_id=>$page_id});
	if ($verbose) { print "<p>Preparing email. "; }
	my ($pgcontent,$pgtitle,$pgformat,$pgarchive,$keyword_count) = &publish_page($dbh,$query,$page_id,0);
	$pgtitle .= " ~ $date";
	if ($verbose) { print "Sending page: $pgtitle </p>\n"; }	
	$report .= "$pgtitle \n\n";
	
								# Do not send empty newsletters
	unless ($keyword_count) {
		&send_email("stephen\@downes.ca","stephen\@downes.ca","Failed content",$content.$status);
		if ($verbose) { print "<p>No new content; no newsletter sent.</p>"; print $Site->{footer}; }
		$report .= "No new content; no newsletter sent. \n\n";
		return;
	}

	
								# Get subscriber List
	my $subscribers = {}; my $stmt;
	if ($send_list eq "all_users") { $stmt = "SELECT person_id FROM person";	} 
	else { $stmt = "SELECT subscription_person FROM subscription WHERE subscription_box='$page_id'";	}
	$report .= "Sending to $send_list\n\n";

	$subscribers = $dbh->selectcol_arrayref($stmt);

								# Loop through subscriber list
								
	my $count = 0;							
	foreach my $subscriber (@$subscribers) {
		my $subdata = &db_get_record($dbh,"person",{person_id=>$subscriber});
		if ( ($subdata->{person_email}) &&
		     ( ($send_list eq "subscribers") ||	
		       ($send_list eq "all_users") ||
		       ($send_list eq "admin" && $subdata->{person_status} eq "admin") ) ) {	
			$count++;
			my $customcontent = $pgcontent;
			$customcontent =~ s/SUBSCRIBER/$subdata->{person_email}/sg;				# Customize
			$customcontent =~ s/PERSON/$subdata->{person_id}/sg;		

			&send_email($subdata->{person_email},$Site->{em_from},$pgtitle,$customcontent,$pgformat); 
			$report .= ": $subdata->{person_email}\n";
			if ($verbose) { 
				if ($count < 10) { print "&nbsp"; }
				if ($count < 100) { print "&nbsp"; }
				if ($count < 1000) { print "&nbsp"; }
				print "$count - $subdata->{person_email}\n<br>";
				
			}
		}
	}							
			
	my $cmg = "$count newsletters sent.";
	if ($count == 1) { $cmg = "1 newsletter sent."; }							
	if ($verbose) { 
		print "<hr><p>$cmg newsletter sent.</p>"; 		
		print $Site->{footer};
	}
	$report .= "\n$cmg.\n\n";
	if ($dbh) { $dbh->disconnect; }		# Close Database and Exit
	return $report;								
						
}



# -------   Admin Report -------------------------------------------------------

sub admin_report {

	my ($dbh,$query,$count) = @_;
	my $vars = $query->Vars;
	my $ndate = &nice_date(time);

	my $subject - "Statistics for $ndate from $Site->{st_name}";
	$subject .= &nice_date(time);

	my $tag = $Site->{st_tag};
	$tag =~ s/#//;


	my ($oc,$op,$of,$ol,$ot,$om);
	open FSAVEIN,"/var/www/cgi-bin/data/".$Site->{st_name}."_fsave.txt";
	while (<FSAVEIN>) {
		chomp;
		($oc,$op,$of,$ol,$ot,$om) = split "\t",$_;
		last;
	}
	close FSAVEIN;

	
	my $subCount = $dbh->selectrow_array(qq{SELECT count(*) FROM subscription},undef);	
	my $personCount = $dbh->selectrow_array(qq{SELECT count(*) FROM person},undef);
	my $feedCount = $dbh->selectrow_array(qq{SELECT count(*) FROM feed},undef);

	my $lsql = qq|SELECT count(*) FROM link WHERE (link_title REGEXP '$tag' OR link_description REGEXP '$tag' OR link_category REGEXP '$tag') AND link_type = 'text/html'|;
	my $linkCount = $dbh->selectrow_array($lsql);
	
	my $tsql = qq|SELECT count(*) FROM link WHERE link_type = 'twitter'|;
	my $twitterCount = $dbh->selectrow_array($tsql);
	
	my $msql = qq|SELECT count(*) FROM link WHERE link_type = 'moodle'|;
	my $moodleCount = $dbh->selectrow_array($msql);

	my $msql = qq|SELECT count(*) FROM link WHERE link_type = 'diigo'|;
	my $diigoCount = $dbh->selectrow_array($msql);
	

	&log_status($dbh,$query,"General Stats","headers:Subscriptions,Persons,Feeds,Blog Posts,Twitter,Moodle,Diigo");
	&log_status($dbh,$query,"General Stats","$subCount,$personCount,$feedCount,$linkCount,$twitterCount,$moodleCount,$diigoCount");


	my $content = qq|Statistics for $ndate from $Site->{st_name}:\n|;
	$content .= "Subscriptions: Total: $count ; Since last: ".($count - $oc)."\n";
	$content .= "Persons:  Total: $personCount  ; Since last: ".($personCount - $op)."\n";
	$content .= "Feeds:  Total: $feedCount  ; Since last: ".($feedCount - $of)."\n";
	$content .= "Blog Posts  Total: $linkCount ; Since last: ".($linkCount - $ol)." \n";
	$content .= "Twitter: Total:  $twitterCount  ; Since last: ".($twitterCount - $ot)."\n";
	$content .= "Moodle:  Total: $moodleCount ; Since last: ".($moodleCount - $om)." \n";

	my $sql = qq|SELECT person_email FROM person WHERE person_status='admin'|;

	
	my $ary_ref = $dbh->selectcol_arrayref($sql);
	foreach my $admin (@$ary_ref) {
		next unless $admin =~ /downes/i;
		&send_email($admin,$Site->{em_from},$subject,$content,"html"); 

	}

	

}





# -------  Rotate Hit Counters -----------------------------------------------------------

sub rotate_hit_counters {

	my ($dbh,$query,$table) = @_;
	print "Content-type:text/html\n\n";
	print "Rotating hits table<p>";

	# Set default variables
	my $hitsfield = $table."_hits";
	my $totalfield = $table."_hits";
	my $idfield = $table."_id";

	# Republish Pages Before Rotating
	my $psql = "SELECT page_id FROM page WHERE page_autopub=?";
	my $psth = $dbh->prepare($psql);
	$psth->execute("yes");
	while (my $page = $psth -> fetchrow_hashref()) {
		my $archive_url = &publish_page($dbh,$query,$page->{page_id});
		my $qsql = "UPDATE page SET page_latest = ? WHERE page_id = ?"; 
		my $qsth = $dbh->prepare($qsql);
		$qsth->execute($archive_url,$page->{page_id});
	}

	# Rotate the Counters
	my $sql = "SELECT $idfield,$hitsfield,$totalfield FROM $table WHERE $hitsfield > 0";
	print "$sql <p>";
	my $sth = $dbh->prepare($sql);
	$sth->execute();
	while (my $record = $sth -> fetchrow_hashref()) {
		my $usql = "UPDATE $table SET $hitsfield = ? WHERE $idfield = ?"; 
		my $usth = $dbh->prepare($usql);
		$usth->execute("0",$record->{$idfield});
	print "Content-type: text/html\n\n";
	print "ID: $record->{$idfield} Total $record->{$totalfield} Today $record->{$hitsfield} <br />\n";

	}
	print "Content-type:text/html\n\n";
	print "<p>Rotated $table hit counter</p>";
}


# -------  Format Content -----------------------------------------------------------


sub make_heading {
	my ($script) = @_;
	return unless ($script->{heading});
	my $heading = "";
	if ($script->{format} =~ /txt/) { $heading = "\n\n$script->{heading}\n\n"; }
	else {	$heading = "<h1>$script->{heading}</h1>\n"; }
	return $heading;
}

sub make_next_link {
	my ($dbh,$vars,$options,$person,$script) = @_;
	my @optlist; my $optstring;
	while (my($ox,$oy) = each %$script) { push @optlist,"$ox=$oy"; }
	$optstring = join ";",@optlist;
	return "http://www.downes.ca/cgi-bin/page.cgi?".$optstring;
}





# -------  DB Creator IP ------------------------------------------------------------

# Returns the creator IP for a record given table and IP
# Used to delete spam

sub db_record_crip {

	my ($dbh,$table,$value) = @_;
	return unless ($value);					# Never compare blank values
	my $stmt = "SELECT ".$table."_crip FROM $table WHERE ".$table."_id='$value'";
	my $ary_ref = $dbh->selectcol_arrayref($stmt);
	return $ary_ref->[0];
}




sub day_today {

	# What day is it Today? Return the name of the day
	my ($sec,$min,$hour,$mday,$mon,$year,$wday,$yday,$isdst) = localtime(time);
	my @days = ('Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday');
	return $days[$wday];
}



# -------   Capitalize ---------------------------------------------------------

# For titles
# Adapted from Joseph Brenner >  Text-Capitalize >  Text::Capitalize
# http://search.cpan.org/~doom/Text-Capitalize/Capitalize.pm

sub capitalize {

	my $sentence = shift;
return $sentence;
	$sentence =~ s/&apos;/'/ig;				# '
	$sentence =~ s/&#39;/'/ig;
	my $words; my @words;

	my $title = shift; my $first; my $last;
	my $new_sentence;

								# Defines a word array
	my $word_rule =  qr{ ([^\w\s]*)   			# $1 - leading punctuation 
                   ([\w']*) #'   				# $2 - the word itself 
                   ([^\w\s]*)  					# $3 - trailing punctuation 
                   (\s*)       					# $4 - trailing whitespace 
                 }x ;

								# Define exceptions
	my @exceptions = qw(a an the and or nor for but so yet	
		to of by at for but in with has de von);
	my $exceptions_or = join '|', @exceptions;
	my $exception_rule = qr/^(?:$exceptions_or)$/oi; 

	my $i = 0;						# Extract Words
	while ($sentence =~ /$word_rule/g) {
		if ( ($2 ne '') or $1 or $3 or ($4 ne '') ) {   
			$words[$i] = [$1, $2, $3, $4]; 
			$i++; 
		}
	}

	$first = 0;						# For each word...
	$last = @words+0; 
	for (my $i=$first; $i<=$last; $i++) { 
		my $punct_leading; my $word; my $punct_trailing; my $spc;
       		{  						# Spoof 'continue'
		if ($i >= 0){ $punct_leading = $words[$i]; } else { $punct_leading = ""; }
		$word = $words[$i];
		$punct_trailing = $words[$i+1];
		$spc = $words[$i+2];

#		($punct_leading, $word, $punct_trailing, $spc) = ( @{ $words[$i] } );

		$_ = $word;

		next if ( /[[:upper:]]/ );			# Skip special caps eg. iMac
		next if ( /^[[:upper:]]+$/);

		if ( /^[dl]'/) { #'				# Skip special french cases
			s{ ^(d') (\w) }{ lc($1) . uc($2) }iex;
			s{ ^(l') (\w) }{ lc($1) . uc($2) }iex;
			if ( ($i == $first) or ($i == $last) ) { 
				$_ = ucfirst;
			}
			next;
		}

		if ( ($i == $first) or ($i == $last) ) {	# Capitalize first and last
			$_ = ucfirst( lc );
			next;
		}

 								# Skip exceptions
		if ( /$exception_rule/ ) {
			$_ = lc;
		} else {
			$_ = ucfirst( lc );			# Cap the rest
		}

       		} continue { 
								# Append word to title
			$new_sentence .=  $punct_leading . $_ . $punct_trailing . $spc;
		}

	}  # end of per word for loop

	# Fix upper-case contractions
	$new_sentence =~ s/(\S')(\S)/$1\l$2/ig;
	$new_sentence =~ s/'/&#39;/ig;  #'
		
	return $new_sentence;
}


sub moderate_meeting {
	
	my ($dbh,$query) = @_;
	my $vars = $query->Vars;
	
	unless ($vars->{meeting_name}) { $vars->{meeting_name} = "Administrator Meeting"; }	
	unless ($vars->{meeting_id}) { $vars->{meeting_id} = "12345"; }		


	&bbb_join_as_moderator($vars->{meeting_id},$Person->{person_name},$Person->{person_title});

	exit;


	
}

#
# Don't Delete these
# They're actually used by gRSShopper.pl
#

# -------   Header ------------------------------------------------------------

sub header {

	my ($dbh,$query,$table,$format,$title) = @_;
	my $template = "admin_header";

	return &template($dbh,$query,$template,$title);

}

# -------   Footer -----------------------------------------------------------

sub footer {

	my ($dbh,$query,$table,$format,$title) = @_;
	my $template = "admin_footer";
	return &template($dbh,$query,$template,$title);

}


