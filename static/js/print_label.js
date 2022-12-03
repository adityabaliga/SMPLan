function get_param(){
    var queryString = decodeURIComponent(window.location.search);
    queryString = queryString.substring(1);
    var queries = queryString.split("&");

    document.getElementById("smpl_no").innerHTML = queries[0] + " - " + queries[6];
    if(queries[2] == "TSDPL"){
        document.getElementById("customer").innerHTML = queries[2]+ " - " + queries[11];
    }
    else{
        document.getElementById("customer").innerHTML = queries[2];
    }
    if((document.getElementById("customer").innerHTML).length < 11){
        document.getElementById("customer").style.fontSize = "50px";
    }else if((document.getElementById("customer").innerHTML).length > 11 && queries[2].length < 15){
        document.getElementById("customer").style.fontSize = "38px";
    }
    else{
        document.getElementById("customer").style.fontSize = "35px";
    }

    document.getElementById("size").innerHTML = " " + queries[4] + " - " + queries[5] + "   metres";
    if(document.getElementById("size").innerHTML.length > 23){
        document.getElementById("size").style.fontSize = "22px";
    }
    if(queries[7] != 'N/A'){
         document.getElementById("mill_id").innerHTML = " " + queries[9] + ' ID: ' + queries[7];
    }else{
        myobj = document.getElementById("mill_id");
        myobj.remove();
    }

    if(queries[8] != 'N/A'){
        if(queries[8].includes('SCAMS NO'))
        {
            grade = queries[8].split('SCAMS NO');
            html = '<p name="scams_no" id="scams_no">%scams_no%</p>';
            scams_in_html = 'SCAMS NO: ' + grade[1].slice(1);
            newHTML = html.replace('%scams_no%', scams_in_html);
            document.getElementById("grade").innerHTML = " " + 'GRADE: ' + grade[0];
            document.getElementById('label_details').insertAdjacentHTML('beforeend', newHTML)
        }
        else{
         document.getElementById("grade").innerHTML = " " + 'GRADE: ' + queries[8];
         }
    }else{
        myobj = document.getElementById("grade");
        myobj.remove();
    }


    document.getElementById("prod_date").innerHTML = " " + "DATE : " + queries[1];
    if(queries[9] == "undefined"){
        document.getElementById("comments").innerHTML = "";
    }
    else{
        document.getElementById("comments").innerHTML = " " + queries[10];
    }

    document.getElementById("machine").innerHTML = "";

}

function get_param_reshearing(){
    var queryString = decodeURIComponent(window.location.search);
    queryString = queryString.substring(1);
    var queries = queryString.split("&");


    if(queries[2] == "TSDPL"){
        document.getElementById("customer").innerHTML = queries[2]+ " - " + queries[11];
         mat_type_pos = 12;
    }
    else{
        document.getElementById("customer").innerHTML = queries[2];
         mat_type_pos = 11;
    }

    if (queries[mat_type_pos] != ""){
        mat_type = '(' + queries[mat_type_pos] + ')';
    }else{
        mat_type = '';
    }

    document.getElementById("smpl_no").innerHTML = queries[0] + " - " + queries[6] + ' ' + mat_type;

    if((document.getElementById("customer").innerHTML).length < 11){
        document.getElementById("customer").style.fontSize = "50px";
    }else if((document.getElementById("customer").innerHTML).length > 11 && queries[2].length < 15){
        document.getElementById("customer").style.fontSize = "38px";
    }
    else{
        document.getElementById("customer").style.fontSize = "33px";
    }

    document.getElementById("size").innerHTML = " " + queries[4] + " - " + queries[5] + " Nos";
    if(document.getElementById("size").innerHTML.length > 23){
        document.getElementById("size").style.fontSize = "22px";
    }
    if(queries[7] != 'N/A'){
         document.getElementById("mill_id").innerHTML = " " + queries[9] + ' ID: ' + queries[7];
    }else{
        myobj = document.getElementById("mill_id");
        myobj.remove();
    }

    if(queries[8] != 'N/A'){
        if(queries[8].includes('SCAMS NO'))
            {
                grade = queries[8].split('SCAMS NO');
                html = '<p name="scams_no" id="scams_no">%scams_no%</p>';
                scams_in_html = 'SCAMS NO: ' + grade[1].slice(1);
                newHTML = html.replace('%scams_no%', scams_in_html);
                document.getElementById("grade").innerHTML = " " + 'GRADE: ' + grade[0];
                document.getElementById('label_details').insertAdjacentHTML('beforeend', newHTML)
            }
            else{
             document.getElementById("grade").innerHTML = " " + 'GRADE: ' + queries[8];
             }
    }else{
        myobj = document.getElementById("grade");
        myobj.remove();
    }


    document.getElementById("prod_date").innerHTML = " " + "DATE : " + queries[1];
    if(queries[10] == "undefined"){
        document.getElementById("comments").innerHTML = "";
    }
    else{
        document.getElementById("comments").innerHTML = " " + queries[10];
    }

    document.getElementById("machine").innerHTML = queries[3];

}


function get_param_big(){
    var queryString = decodeURIComponent(window.location.search);
    queryString = queryString.substring(1);
    var queries = queryString.split("&");
    var mat_type, mat_type_pos;


    if(queries[2] == "TSDPL"){
        document.getElementById("customer").innerHTML = queries[2]+ " - " + queries[12];
        mat_type_pos = 13;
    }
    else{
        document.getElementById("customer").innerHTML = queries[2];
        mat_type_pos = 12;
    }


    if (queries[mat_type_pos] != ""){
        mat_type = '(' + queries[mat_type_pos] + ')';
    }else{
        mat_type = '';
    }

    if(queries[2].length < 16){
        document.getElementById("customer").style.fontSize = "60px";
    }
    else if(queries[2].length > 16 && queries[2].length < 19){
        document.getElementById("customer").style.fontSize = "55px";
    }
    else{
        document.getElementById("customer").style.fontSize = "35px";
    }

    var myobj;
    document.getElementById("smpl_no").innerHTML = queries[0] + " - " + queries[6] + ' ' + mat_type;
    document.getElementById("size").innerHTML = " " + queries[4] + " - " + queries[5] + " No.s";
    //If mill id is marked N/A in the processing page. We have to remove the line from the label
    if(queries[9] != 'N/A'){
        if(queries[9].includes('SCAMS NO'))
            {
                grade = queries[9].split('SCAMS NO');
                html = '<p name="scams_no" id="scams_no">%scams_no%</p>';
                scams_in_html = 'SCAMS NO: ' + grade[1].slice(1);
                newHTML = html.replace('%scams_no%', scams_in_html);
                document.getElementById("grade").innerHTML = " " + 'GRADE: ' + grade[0];
                document.getElementById('label_details').insertAdjacentHTML('beforeend', newHTML)
            }
            else{
             document.getElementById("grade").innerHTML = " " + 'GRADE: ' + queries[9];
             }
         }else{
        myobj = document.getElementById("mill_id");
        myobj.remove();
    }

    if(queries[8] != 'N/A'){
        document.getElementById("mill_id").innerHTML = " " + queries[10] + ' ID: ' + queries[8];
    }else{
        myobj = document.getElementById("mill_id");
        myobj.remove();
    }

    document.getElementById("prod_date").innerHTML = " " + "DATE : " + queries[1];
    if(queries[7] != "No Lamination"){
        document.getElementById("lamination").innerHTML = queries[7];
    }else{
        document.getElementById("lamination").innerHTML = "";
    }

    if(queries[11] == "undefined"){
        document.getElementById("comments").innerHTML = "";
    }
    else{
        document.getElementById("comments").innerHTML = " " + queries[11];
    }

    document.getElementById("machine").innerHTML = "";

}
