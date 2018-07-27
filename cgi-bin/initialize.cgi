#!/usr/bin/env perl
print "Content-type:text/html\n\n";
print "in Initialize<p>";

#-------------------------------------------------------------------------------
#
#	    gRSShopper
#           Initialization Functions
#           20 March 2017 - Stephen Downes
#
#-------------------------------------------------------------------------------

# Forbid bots

	die "HTTP/1.1 403 Forbidden\n\n403 Forbidden\n" if ($ENV{'HTTP_USER_AGENT'} =~ /bot|slurp|spider/);



# Load gRSShopper

	use File::Basename;
	use CGI::Carp qw(fatalsToBrowser);
	my $dirname = dirname(__FILE__);
	require $dirname . "/grsshopper.pl";




# Load modules

	our ($query,$vars) = &load_modules("initialize");
    	while (my ($vx,$vy) = each %$vars) {
  #  		print "$vx = $vy <br>";

	}



# Load Site

our $Site = gRSShopper::Site->new({									# Create new Site object
	no_db		=>	'1',									#   no database
	context		=>	'initialize',
	data_dir	=>	'./data/',
});

print "Action: ",$vars->{action},"<br>";

if ($vars->{action}) {					# Perform Action, or

	if ($vars->{action} eq "command") { &__command(); }
	elsif ($vars->{action} eq "file") {  &__multisite_form($vars->{action}); }
	elsif ($vars->{action} eq "url") {  &__multisite_form($vars->{action}); }
	elsif ($vars->{action} eq "db") {   &__multisite_form($vars->{action}); }
	elsif ($vars->{action} eq "multisite") {   &__init_in_multisite($vars); }
	else { &__init_error($vars->{action}) }
}

exit;

#  Multisite Form
  #
  #  Form to input values for database access
  #

  sub __multisite_form {

  	my ($action) = @_;

	# Create or update database information
	# to be stored in multisite.txt file
	if ($action eq "file" || $action eq "url") {

		$Site->{database}->{loc} ||= "localhost";
		print "Content-type: text/html\n\n";
		print qq|			<form action="initialize.cgi" method="post">

		<!-- DB Administrator Info -->
			Please enter database information for $Site->{st_host}
			<br>
			<br><table cellspacing=1 cellpadding=2 border=0>
			<tr><td colspan=2><br>Please enter database administrator information<br> (required to create databases and grant privileges)<br><br></td></tr>

			<tr><td align="right">Admin Username</td><td><input type="text" name="admin_usr" value=""></td></tr>
			<tr><td align="right">Admin Password</td><td><input type="password" name="admin_pwd" value=""></td></tr>


		<!-- Database Info -->
			<tr><td colspan=2><br>Database Information:<br><br></td></tr>
			<input type="hidden" name="st_host" value="$Site->{st_host}">
			<tr><td align="right">Database Name</td><td><input type="text" name="db_name" value="$Site->{database}->{name}"></td></tr>
			<tr><td align="right">Database Location</td><td><input type="text" name="db_loc" value="$Site->{database}->{loc}"></td></tr>
			<tr><td align="right">Database Username</td><td><input type="text" name="db_usr" value="$Site->{database}->{usr}"></td></tr>
			<tr><td align="right">Database Password</td><td><input type="password" name="db_pwd" value="$Site->{database}->{pwd}"></td></tr>
			<tr><td align="right">Language</td><td><input type="text" name="site_language" value="$Site->{site_language}"></td></tr>
			<tr><td align="right">Site Document Directory</td><td><input type="text" name="st_urlf" value="$Site->{st_urlf}"></td></tr>
			<tr><td align="right">Site CGI Directory</td><td><input type="text" name="st_cgif" value="$Site->{st_cgif}"></td></tr>


		<!-- Site Info -->

			<tr><td colspan=2><br>Site Information:<br><br></td></tr>
			<tr><td align="right">Site Name</td><td><input type="text" name="st_name" value="$Site->{st_name}"></td></tr>
			<tr><td align="right">Site Tag</td><td><input type="text" name="st_tag" value="$Site->{st_tag}"></td></tr>
			<tr><td align="right">Site Email Address</td><td><input type="text" name="st_email" value="$Site->{st_email}"></td></tr>
			<tr><td align="right">Site Time Zone</td><td><input type="text" name="st_timezone" value="$Site->{st_timezone}"></td></tr>
			<tr><td align="right">License</td><td><input type="text" name="st_license" value="$Site->{st_license}"></td></tr>
			<tr><td align="right">Site Key</td><td><input type="text" name="st_key" value="$Site->{st_key}"></td></tr>

		<!--  Site Administrator -->

			<tr><td colspan=2><br>Site Administrator:<br><br></td></tr>
			<tr><td align="right">Administrator Username</td><td><input type="text" name="site_admin_name"></td></tr>
			<tr><td align="right">Administrator Password</td><td><input type="password" name="site_admin_pwd"></td></tr>




			<tr><td></td><td><br><input type="submit" name="action" value="multisite"><br>
			</td></tr></table><br/><br/><p>
			</form>
			<a href="admin.cgi">Return to Admin</a>|;

	}





	elsif ($action eq "db") {

		print "Content-type: text/html\n\n";

		print "Need to create DB<p>";
		print "Data dir is: ",$Site->{data_dir},"<p>";

		$Site->__dbinfo();


		print "DB Name: ",$Site->{database}->{name},"<p>";

	}


  }



    sub __init_in_multisite {



    	# Restrict input characters
    	while (my ($vx,$vy) = each %$vars) {
    		print "$vx = $vy <br>";
		next if ($vx eq "error");
		next if ($vx eq "warnings");
		if ($vars->{$vx} =~ /[^\/\\\-0-9a-zA-Z_,\0#@&;\.]/) {
		#	print "Content-type: text/html\n\n";
		#	print "<h1>Input Error in vx: $vars->{$vx} </h1><p>Allowed characters for input: a-zA-Z0-9 # @ & . ; / \</p>";
		#	exit;
			}
	}
	$vars->{site_language} =~ s/\0/,/i;
    	# Standardize dirtectory names
    	unless ($vars->{st_urlf} =~ /\/$/) { $vars->{st_urlf} .= "/"; }
    	unless ($vars->{st_cgif} =~ /\/$/) { $vars->{st_cgif} .= "/"; }

											# Open the multisite configuration file,
											# Initialize if file can't be found or opened
  	my $data_file = $vars->{st_cgif}."data/" . "multisite.txt";
  	my $output = "";

	if (-e $data_file) {								# If the multisite configuration file exists
		open IN,"$data_file" or die "Can't open $data_file to read";		#    open it

		my $url_located = 0;
		while (<IN>) {								#    read each line
			my $line = $_;
			next if ($line =~ /^$Site->{st_host}/);				#    if it's the current site, skip
			$output .= $line;						#    otherwise write data to output
		}
		close IN;

    	}



    	# Make Document Directories
	unless (-d $vars->{st_urlf}) { mkdir $vars->{st_urlf} or die "Could not make the document directory $vars->{st_urlf}  $!"; }
	unless (-d $vars->{st_urlf}) { die "Error making the document directory $vars->{st_urlf}  $!"; }
	foreach my $subdir (qw(archive assets files images logs stats)) {
		mkdir($vars->{st_urlf}.$subdir."/");
		unless (-d $vars->{st_urlf}.$subdir."/") { die "Error making subdirectory ".$vars->{st_urlf}.$subdir."/ $!"; }
	}




											#    write current site data to output
	my $new_line = qq|$Site->{st_host}\t$vars->{db_name}\t$vars->{db_loc}\t$vars->{db_usr}\t$vars->{db_pwd}\t$vars->{site_language}\t$vars->{st_urlf}\t$vars->{st_cgif}\n| or die "Cannot write to $data_file";
	$output .= $new_line;

	open OUT,">$data_file" or die "Cannot open $data_file: $!";		# Save output
	print OUT $output  or die "Cannot save to $data_file: $!";		# Save output;
	close OUT;


print "OK we're here <P>";
	# Load database information into the $Site object
	$Site->__dbinfo();



	# Create Database
	my $dbsetup1="create database ".$vars->{db_name};
	my $dbsetup2= "GRANT ALL PRIVILEGES ON ".$vars->{db_name}.".* TO ".$vars->{db_usr}."@".$vars->{db_loc}." IDENTIFIED BY '".$vars->{db_pwd}."'";
	my $dbsetup3 = "FLUSH PRIVILEGES;";
	my $dbc = DBI->connect("DBI:mysql:host=".$vars->{db_loc}.";port=3306", $vars->{admin_usr},$vars->{admin_pwd}) or die "Cannot connect to database: $! ".$DBI::errstr;
	$dbc->do($dbsetup1) or die "Failed to create database in $vars->{db_name}\n".$DBI::errstr;
	$dbc->do($dbsetup2) or die "Failed to grant privileges in $vars->{db_name}\n".$DBI::errstr;
	$dbc->do($dbsetup3) or die "Failed to flush privileges in $vars->{db_name}\n".$DBI::errstr;
	$dbc->disconnect;



	# Connect to Database
	$Site->__db_connect({initialize => "new"});
	our $dbh = $Site->{dbh};
	print "Created database ",$vars->{db_name},"<p>";


	# Write gRSShopper tables
	&run_sql_file($dbh,$vars->{st_cgif}."sql/grsshopper_tables.sql");

	# Write Config (Stores general site information, can be edited later by admin)

	$vars->{st_pub} = $vars->{st_email};
	$vars->{st_crea} = $vars->{st_email};
	$vars->{reset_key} = $vars->{st_key};
	$vars->{cronkey} = $vars->{st_key};
	my @configs = qw(st_name st_tag st_pub st_crea st_license st_timezone reset_key cronkey);
	foreach $config (@configs) {
	   print "$config = ".$vars->{$config}." <br>";

	   &db_insert($dbh,"","config",{config_noun=>$config,config_value=>$vars->{$config}}) or print "Error inserting $config -- $vars->{err}";
	}
	print "Stored site config information in database<p>";


	# Import gRSShopper data

	# Form (defines editing forms for various data types)
	my $file->{file_location} = $vars->{st_cgif}."sql/box.json";
	&import_json($file,"box");

	# Form (defines editing forms for various data types)
	$file->{file_location} = $vars->{st_cgif}."sql/form.json";
	&import_json($file,"form");

	# Template (defines various page templates)
	$file->{file_location} = $vars->{st_cgif}."sql/template.json";
	&import_json($file,"template");

	# View (predefined view templates for various data types)
	$file->{file_location} = $vars->{st_cgif}."sql/view.json";
	&import_json($file,"view");


	# Connect to Database
	$Site->__db_connect();
	print "Connected to database<p>";



	# Create Admin and anon Accounts
	# Note: windows users must perform this step manually
	my $site_admin_name = $vars->{site_admin_name};
	my $encryptedPsw = &encryptingPsw($vars->{site_admin_pwd}, 4);
	my $id_number = &db_insert($dbh,"","person",{person_title=>$site_admin_name,person_password=>$encryptedPsw,person_status=>"admin"});
	if ($id_number) { print qq|Created Site Administrator - <a href="admin.cgi">click here to login</a><p>|; }
	else { print qq|error creating admin user.|; }



	#&__multisite_form("Updated");						# Show the form again




	print "Done";

    }





sub __command {

	if ($vars->{cause} eq "file") {  $Site->__multisite_form($vars->{action}); }
	elsif ($vars->{cause} eq "url") {   $Site->__multisite_form($vars->{action}); }
	else { __init_error($vars->{action}) }

}



  sub __init_error {

	my ($action) = @_;
	print "Content-type: text/html\n\n";
	print qq|
			Initialization error. Did not recognize the following command: $action <p>
	|;


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

	unless (-e $sqlFile) {	die "Could not find SQL file $sqlFile"; 	}

	open (SQLFILE, "$sqlFile") or die "Could not load SQL file into the database: $!";

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


	print qq|<textarea cols=80 rows=5"> |;

      	# Execute each SQL command in turn
	foreach my $sqlStatement (@sqllines) {
		next unless ($sqlStatement);
		print $sqlStatement;
		my $sth = $dbh->prepare($sqlStatement) or die "Cannot prepare SQL statement";
		$sth->execute() or die "Cannot execute SQL statement";
		print "Database initializaton failed" if $dbh::err;
	}
	print qq|</textarea><p>|;

      print "Ran SQL file $sqlFile OK<br><br>";

}
