var url = 'https://el30.mooc.ca/cgi-bin/api.cgi';

// Stores current status of the Reader
var readerTable;
var readerIndex;

//
//  Initialize Content Windows
//

function startUp(url) {

  $( document ).ready(function() {

    read_into({div:"Read",cmd:"list",table:"link",tab:"Read"});
    read_into({div:"Make",cmd:"list_tables",table:"tables",tab:"Make"});
    $('#list-button').hide();
    closeTalkNav();  // To get it to slide the right way when first started

  });
}

//
//  openDiv
//
//  Load content into a div and show the div
//

function openDiv(url,div,app,db,id,title,starting_tab,autopost) {
//alert("Cmd: "+app+", Table: "+db+", ID: "+id+", Title: "+title+", Starting Tab: "+starting_tab+"Autopost: "+autopost);
    // Assign a URL to main add an "active" class to the button that opened the tab

    if (title) { url = url + "?cmd="+app+"&app="+app+"&db="+db+"&id="+id+"&title="+title+"&autopost="+autopost; }
    else if (id) { url = url + "?cmd="+app+"&app="+app+"&db="+db+"&id="+id+"&autopost="+autopost; }
    else { url = url + "?cmd="+app+"&app="+app+"&db="+db; }

    var openme = 'main';
    if (div) { openme=div;}
    $('#'+openme).load(url, function(respose, status, xhr) {
        if (status == "error") {
            var msg = "Sorry but there was an error: ";
            alert(msg + xhr.status + " " + xhr.statusText);
        }
     });
     $('#'+openme+'-tab').show();

}

//
//  openDiv
//
//  Load content into a div
//  Accepts input as serialized json
//

function read_into(args) {

   if (!args.url) { args.url = url; }                                       // set default api url
   if (!args.div) { alert("Div not specified in read_into"); return;}       // set div to read into
   if (args.cmd) {
       args.url += "?cmd="+args.cmd;
       if (args.table) { args.url += "&table="+args.table; }
       if (args.id) { args.url += "&id="+args.id; }
       if (args.tab) { args.url += "&tab="+args.tab; }
   }

    // Load Content into Div
    //  $('#Reader').load(url+ "?cmd=show&table=link&id=2",function(response, status, xhr){
      $('#'+args.div).load(args.url,function(response, status, xhr){
        if (status == "error") {
             var msg = "Sorry but there was an error loading "+args.url+" into "+args.div;
             alert(msg + xhr.status + " " + xhr.statusText);
             return;
           }
      });


}

//
// The Main Window uses Bootstrap Nav tabs
// For information see: https://getbootstrap.com/docs/4.0/components/navs/
//


//
// Visibility toggle
//

function toggle_visibility(id) {
       var e = document.getElementById(id);
       if(e.style.display == 'block')
          e.style.display = 'none';
       else
          e.style.display = 'block';
    }

    //
    // Generic 'Persist' Show-Hide toggle - not sure where I use this
    //


    function onclick_function(col_name,persist) {

        $('#'+col_name+'_button').show();
        if (persist) { return; }
        $('#'+col_name+'_result').hide();
    }



//
//  Open and Close Left and Right Side Navigation
//  Resizing when window resized
//

var sidebarwidth=450;
var leftstatus="closed";
var rightstatus="closed";
var viewportWidth = jQuery(window).width();


function openNav() {
    var leftWidowWidth = sidebarwidth;
    if (viewportWidth < leftWidowWidth) { leftWidowWidth = viewportWidth; }  // Don't overlap small windows
    document.getElementById("mySidenav").style.width = leftWidowWidth+"px";
    document.getElementById("main").style.marginLeft = leftWidowWidth+"px";
    leftstatus="open";
}

function closeNav() {
    document.getElementById("mySidenav").style.width = "0px";
    document.getElementById("main").style.marginLeft = "0px";
    leftstatus="closed";
}


function openTalkNav() {
    var rightWidowWidth = sidebarwidth;
    var rightWidowLeft = viewportWidth - sidebarwidth;
    if (rightWidowLeft < 0) { rightWidowLeft = 0; }  // Don't overlap small windows
    if (viewportWidth < rightWidowWidth) { rightWidowWidth = viewportWidth; }  // Don't overlap small windows
    document.getElementById("main").style.marginRight = sidebarwidth+"px";
    document.getElementById("myTalknav").style.left = rightWidowLeft+"px";
    document.getElementById("myTalknav").style.width = sidebarwidth+"px";
    rightstatus="open";
}

function closeTalkNav() {
    document.getElementById("myTalknav").style.left = viewportWidth+"px";
    document.getElementById("main").style.marginRight= "0px";
    rightstatus="closed";
}

$( window ).resize(function() {
  viewportWidth = jQuery(window).width();
//  alert("window resized to "+viewportWidth);
  if (leftstatus == "open") { openNav(); }
  if (leftstatus == "closed") { closeNav(); }
  if (rightstatus == "open") { openTalkNav(); }
  if (rightstatus == "closed") { closeTalkNav(); }
});
//
// Load some content into divs - I'm not sure I use this anywhere
//


$(document).ready( function() {
    $("#load_home").on("click", function() {
        $("#content").load("content.html");
    });
});







//
// Open the Columns Window (Used by the Forms editor)
//

function openColumns(url,db) {

    // Load the api result into the columns_table div
    $("#columns_table").load(url, function(response, status, xhr) {
        if (status == "error") {
            var msg = "Sorry but there was an error showing columns: ";
            alert(msg + xhr.status + " " + xhr.statusText);
        }
     });
}




//
// Function for tab opening
//
// Closes other tabs in parent div and opens the tab 'tabName'
//


function openTab(event, tabName, tabType, tabID) {
    // Declare all variables
    var i, tabcontent, tablinks;

    // Get all siblings and hide them
    $('#'+tabName).siblings().hide();

    // Get all elements with class=tabType and remove the class "active"
    $('.'+tabType).removeClass("active");

    // Show the current tab, and add an "active" class to the button that opened the tab
    $('#'+tabName).show();
    if (tabID) { $('#'+tabID).show(); }            // Force hidden tab to reveal itself
    event.currentTarget.className += " active";    // Is there a JQuery way to do this??

}



//
// Open hidden left-side tab
//

function openHiddenTab(event,url,search,tabname,db,tab) {

    // Assign a URL
    if (search.length > 0) { url = url + "?cmd=list&obj=record&tab="+tab+"&search="+search+"db="+db;}
    if (search.length == 0) { url = url + "?cmd=list&obj=record&tab="+tab+"&table="+db; }

    // Get all elements with class="tablinks" and remove the class "active"
    tablinks = document.getElementsByClassName("tablinks");
    for (i = 0; i < tablinks.length; i++) {
        tablinks[i].className = tablinks[i].className.replace(" active", "");
    }

    // Load the result into the hidden tab content window
    $("#List").load(url, function(response, status, xhr) {
        if (status == "error") {
            var msg = "Sorry but there was an error: ";
            alert(msg + xhr.status + " " + xhr.statusText);
        }
     });

    // Show the hidden tab
    $("#"+tabname).show();

    // Open the tab content
    openTab(event, 'List');

    // Make the formerly hidden tab active
    $("#"+tabname).addClass("active");
}

function WhichElementIsThis(event) {
    event = event || window.event;
    var elem = event.target || event.srcElement;
    return elem;
}






// Submission Functions






//
// API List Submission Function - handles input from list and search requests
//                                and places results in a div with id 'List'
//

function list_form_submit(url,formid) {
  var dat;
  dat = $('#'+formid).serialize();
  //alert(dat);
   $.ajax({
        type: "POST",
        url: url,
        data: $('#'+formid).serialize(), // serializes the form's elements.
        error: function(value) {
            $("#List").html("<div class=\"error\">An error has occurred: "+value+"</div>");
        },
        success: function(value)
        {
            $("#List").html(value);
            $("#mySidenav").animate({ scrollTop: 0 }, "fast");
        }
      });
}
//
// API Input Submission Function
//


function api_submit(url,div,cmd,obj,table,id,col,content) {
        $('#'+div+"_div").addClass('spinner');
        $.ajax({
            url: url,
            data: {cmd:cmd,obj:obj,table:table,id:id,col:col,content:content},
            error: function(value) {
                alert("Sorry, but an error occurred: "+value);
                $('#'+div+'_result').html("<div class=\"error\">An error has occurred</div>");
                $('#'+div+'_result').show(); },
            success: function(value) {
                $('#'+div+'_result').html("<div class=\"success\">"+value+"</div>");
                $('#'+div+'_liveupdate').html(value);
                $('#'+div+'_result').show();
                var previewUrl= url+"?cmd=show&table="+table+"&id="+id+"&format=summary";
                $('#Preview').load(previewUrl);
                $('.empty-after').val("");
               },
            type: "post",
        });
        setTimeout(function(){$('#'+div+"_div").removeClass('spinner');}, 1000);
        setTimeout(function(){$('#'+div+"_result").hide();}, 100000);
}


//
// Generic Submission Function
//


function submit_function(url,table,id,col_name,content,type) {
//alert("Called"+table+id+col_name+content+type);
        $('#'+col_name+"_div").addClass('spinner');
        $.ajax({
            url: url,
            data: {cmd:'update',type:type,table_id:id,table_name:table,updated:1,value:content,col_name:col_name,type:type},
            error: function(value) {
                $('#'+col_name+'_result').html("<div class=\"error\">An error has occurred</div>");
                $('#'+col_name+'_result').show();
              },

            success: function(value) {
                $('#'+col_name+'_result').hide();
                $('#'+col_name+'_result').html("<div class=\"success\">"+value+"</div>");
                $('#'+col_name+'_liveupdate').html(value);
                $('#'+col_name+'_result').show();
                var previewUrl= url+"?cmd=show&table="+table+"&id="+id+"&format=summary";
                $('#Preview').load(previewUrl);
                $('.empty-after').val("");
               },
            type: "post",
        });

        setTimeout(function(){$('#'+col_name+"_div").removeClass('spinner');}, 1000);
        setTimeout(function(){$('#'+col_name+"_result").hide();}, 100000);
}

function record_delete(url,table,id,col_name,content,type) {
//
// Function for delete record
//

  if (confirm('Are you sure you want to delete?')) {
    // Delete it!
    $.ajax({
        url: url,
        data: {table:table,id:id,cmd:'delete',obj:'record'},
        error: function(value) { alert("error deleting "+table); },
        success: function(value) {
            $('#'+table+"-"+id).html("deleted");
            setTimeout(function(){$('#'+table+"-"+id).hide(); }, 1000);
        },
        type: "post",
    });




  } else {
    // Do nothing!
  }

}
//
// Function for Graph Removal
//

function removeKey(url,table,id,key,keyid) {

        var col_name = table+"_"+key;
        submit_function(url,table,id,col_name,keyid,'remove');
}

//
// Submit Column Function
//

function submit_column(url,table,id,col_name,content,type) {
        $('#submit_column_result').hide();
        $('#columns_table').addClass('spinner');
        $.ajax({
            url: url,
            data: {type:type,table_id:id,table_name:table,updated:1,value:content,col_name:col_name,type:type},
            error: function(value) {
                $('#submit_column_result').html("<div class=\"error\">An error has occurred</div>");
                $('#submit_column_result').show(); },
            success: function(value) {
                $('#submit_columns_result').html("<div class=\"success\">"+value+"</div>");
                $('#submit_columns_result').show();
               },
            type: "post",
        });
        setTimeout(function(){$('#columns_table').removeClass('spinner');}, 1000);
}

function alter_column(url,table,col_name) {

        $('#submit_column_result').hide();
        $('#columns_table').addClass('spinner');

        var content = col_name +';'+
            $('#'+col_name+'_type').val() +';'+
            $('#'+col_name+'_size').val();
        $.ajax({
            url: url,
            data: {type:'alter',table_id:'alter',table_name:table,updated:1,value:content,col_name:col_name},
            error: function(value) {
                $('#submit_column_result').html("<div class=\"error\">An error has occurred</div>");
                $('#submit_column_result').show(); },
            success: function(value) {
                $('#submit_columns_result').html("<div class=\"success\">"+value+"</div>");
                $('#submit_columns_result').show();
               },
            type: "post",
        });
        setTimeout(function(){$('#columns_table').removeClass('spinner');}, 1000);
}

function remove_column(url,table,col_name,content) {
        $('#submit_column_result').hide();
        $('#columns_table').addClass('spinner');

        $.ajax({
            url: url,
            data: {table_id:table,table_name:table,updated:1,value:content,col_name:col_name,type:'column_remove'},
            error: function(value) {
                $('#submit_column_result').html("<div class=\"error\">An error has occurred</div>");
                $('#submit_column_result').show(); },
            success: function(value) {
                $('#submit_columns_result').html("<div class=\"success\">"+value+"</div>");
                $('#submit_columns_result').show();
               },
            type: "post",
        });
        setTimeout(function(){$('#columns_table').removeClass('spinner');}, 1000);
}
