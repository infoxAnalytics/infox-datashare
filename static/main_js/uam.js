function getResult(x) {
    $(location).attr('href', x);
}


function getSurvey(x) {
    $(location).attr('href', '/do-survey?name='+x);
}


// Main function jobs
/// Create table for system logs
function create_table_for_system_logs(x) {
	var content = '';
	content += '<table class="table table-striped table-bordered" width="100%" cellspacing="0" id="log_table">';
    content += '      <thead>';
    content += '        <tr>';
    content += '          <th>ID</th>';
    content += '          <th>Type</th>';
    content += '          <th>IP</th>';
    content += '          <th>Severity</th>';
    content += '          <th>Log</th>';
    content += '          <th>Timestamp</th>';
    content += '          <th>Username</th>';
    content += '        </tr>';
    content += '      </thead>';
    content += '      <tbody>';
    $.each(x.content, function(k, v) {
    	content += '<tr>';
    	content += '	<td>'+v.id+'</td>';
    	content += '	<td>'+v.type+'</td>';
    	content += '	<td>'+v.ip+'</td>';
    	content += '	<td><button type="button" class="'+v.severity[1]+'" style="width:100%">'+v.severity[0]+'</button></td>';
    	content += '	<td style="word-break:break-all;">'+v.log+'</td>';
    	content += '	<td>'+v.timestamp+'</td>';
    	content += '	<td>'+v.username+'</td>';
    	content += '</tr>';
    });
    content += '	</tbody>';
    content += '</table>';
    return content;
}


/// Search system logs
function search_log() {
	$("#log_table_area table").remove();
    var get_all_log = document.querySelector('[id="get_all_log"]').value;
    if( !$("#event_ip").val() ){
        var event_ip = "none";
    }else{
        var event_ip = document.querySelector('[id="event_ip"]').value;
    }
    if( !$("#event_keyword").val() ){
        var event_keyword = "none";
    }else{
        var event_keyword = document.querySelector('[id="event_keyword"]').value;
    }
    if( !$("#event_start_date").val() ){
        var event_start_date = "none";
    }else{
        var event_start_date = document.querySelector('[id="event_start_date"]').value;
    }
    if( !$("#event_end_date").val() ){
        var event_end_date = "none";
    }else{
        var event_end_date = document.querySelector('[id="event_end_date"]').value;
    }
    if( !$("#event_type").val() ){
        var event_type = "none";
    }else{
        var event_type = $("#event_type").val().join(',');
    }
    if( !$("#event_severity").val() ){
        var event_severity = "none";
    }else{
        var event_severity = $("#event_severity").val().join(',');
    }
    if( !$("#event_users").val() ){
        var event_users = "none";
    }else{
        var event_users = $("#event_users").val().join(',');
    }
    var data = {"PROCESS":"SearchLog", "ALL_LOG":get_all_log, "EVENT_IP":event_ip, "EVENT_KEYWORD":event_keyword, "EVENT_START_DATE":event_start_date, "EVENT_END_DATE":event_end_date, "EVENT_TYPE":event_type, "EVENT_SEVERITY":event_severity, "EVENT_USERS":event_users};
    $.ajax({
      type: "POST",
      url: "/admin-components",
      data: data,
      dataType: "json",
      success: function(data) {
        if ( data.STATUS == "OK" ) {
            new PNotify({
                title: 'Query completed.',
                text: data.q,
                type: 'success'
              });
            $("#log_table_area div#log_table_wrapper").remove();
            $(create_table_for_system_logs(data)).appendTo("#log_table_area");
            $('#log_table').DataTable({ "order": [[ 0, "desc" ]], columnDefs: [{ type: 'date-euro', targets: 5 }] });
          } else {
            $("#log_table_area div#log_table_wrapper").remove();
            new PNotify({
                title: 'Oops !!! Something went wrong.',
                text: data.ERROR,
                type: 'error'
              });
          }
      }
    });
}

function pendingAccountManager(x,y) {
    if( !$("#"+y+"_project").val() ){
        var projects = "none";
    }else{
        var projects = $("#"+y+"_project").val().join(',');
    }
    var data = {"PROCESS":"ChangeUserStatus", "USER_ID":y, "USER_STATUS":x, "PROJECT":projects}
    $.ajax({
      type: "POST",
      url: "/admin-components",
      data: data,
      dataType: "json",
      success: function(data) {
        if ( data.STATUS == "OK" ) {
            new PNotify({
                title: 'User Status Changed.',
                text: data.MESSAGE,
                type: 'success'
              });
            $(location).attr('href', '/management');
          } else {
            new PNotify({
                title: 'Oops !!! Something went wrong.',
                text: data.ERROR,
                type: 'error'
              });
          }
      }
    });
}