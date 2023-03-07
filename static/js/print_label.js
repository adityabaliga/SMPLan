var lbl_smpl_no_pos = 0;
var lbl_prod_date_pos =1;
var lbl_customer_pos = 2;
var lbl_machine_pos = 3;
var lbl_size_pos = 4;
var lbl_numbers_pos = 5;
var lbl_packet_name_pos = 6;
var lbl_lamination_pos = 7;
var lbl_mill_id_pos = 8;
var lbl_grade_pos = 9;
var lbl_mill_pos = 10;
var lbl_comment_pos = 11;
var lbl_2nd_customer_pos = 12;
var lbl_mat_type_pos = 13;
var lbl_scams_no_pos = 14;
var lbl_coating_pos = 15;
var lbl_part_no_pos = 16;
var lbl_batch_no_pos = 17;
var lbl_net_wt_pos = 18;
var lbl_gross_wt_pos = 19;
var lbl_top_comment_pos = 20;
var lbl_format_size = 21;
var lbl_mat_status = 22;

//function to reduce the font size when length of text is long
//https://stackoverflow.com/questions/18229230/dynamically-change-the-size-of-the-font-size-based-on-text-length
function resize_to_fit(elementID){
    var docElement = document.getElementById(elementID);
    if(docElement != null){
        var windowStyle = window.getComputedStyle(docElement);
        var fontSize = windowStyle.fontSize;
        //var fontSize = window.getComputedStyle(document.getElementById(elementID)).fontSize;
        document.getElementById(elementID).style.fontSize = (parseFloat(fontSize) - 1) + 'px';
        var font_test = document.getElementById(elementID).style.fontSize;
        var elementClientHeight = parseFloat(document.getElementById(elementID).outerText.length) * parseFloat(font_test);
        var elementClientWidth = (document.getElementById(elementID).clientWidth);
        var par = document.getElementById('label_details_size');
        var child = document.getElementById(elementID);
        var parentClientHeight = document.getElementById('label_details_size').clientWidth;
        if(elementClientHeight >=  1.7*parentClientHeight){
            resize_to_fit(elementID);
        }
    }
}


function get_param_new(){
    var queryString = decodeURIComponent(window.location.search);
    var url = window.location.href;
    queryString = queryString.substring(1);
    var queries = queryString.split("&");
    var line_count=4;

    document.getElementById("machine").innerHTML = queries[lbl_machine_pos];
    document.getElementById("top_comment").innerHTML = queries[lbl_top_comment_pos];
    if(queries[lbl_top_comment_pos] == "RH" || queries[lbl_top_comment_pos] == "LH"){
        document.getElementById("top_comment").style.fontSize = "23px";
    }
    document.getElementById("prod_date").innerHTML = "DATE: " + queries[lbl_prod_date_pos];

    if (queries[lbl_2nd_customer_pos] != "" && !url.includes("print_label_tsl")){
        document.getElementById("customer").innerHTML = queries[lbl_customer_pos]+ " - " + queries[lbl_2nd_customer_pos];
    }else{
        document.getElementById("customer").innerHTML = queries[lbl_customer_pos];
    }

    document.getElementById("smpl_no").innerHTML = queries[lbl_smpl_no_pos] + " - " + queries[lbl_packet_name_pos] + " (" +queries[lbl_mat_type_pos] + ")";
    document.getElementById("size").innerHTML = queries[lbl_size_pos];


     if(url.includes('print_label_tsl')){
      document.getElementById("numbers").innerHTML = "NUMBERS: " + queries[lbl_numbers_pos];
     }else{
        if(queries[lbl_size_pos].includes("c")){
            document.getElementById("size").innerHTML +=  " - " + queries[lbl_numbers_pos] + " metres";
        }else{
        document.getElementById("size").innerHTML +=  " - " + queries[lbl_numbers_pos] + " Nos";
        }
     }


    if(queries[lbl_coating_pos] != ""){
        document.getElementById("coating").innerHTML = 'COATING: ' + queries[lbl_coating_pos];
        line_count+=1;
        }else{
        myobj = document.getElementById("coating");
        myobj.remove();
    }

    if(queries[lbl_batch_no_pos] != ""){
        document.getElementById("batch_no").innerHTML = 'BATCH NO: ' + queries[lbl_batch_no_pos];
        line_count+=1;
        }else{
        myobj = document.getElementById("batch_no");
        myobj.remove();
    }

    if(queries[lbl_mill_pos] != ""){
        if(queries[lbl_customer_pos].startsWith("HONDA")){
            document.getElementById("mill_id").innerHTML = "COIL NO : " + queries[lbl_mill_id_pos] + " (" + queries[lbl_mill_pos] + ")";
        }else{
            document.getElementById("mill_id").innerHTML = queries[lbl_mill_pos] + " ID : " + queries[lbl_mill_id_pos];
        }
        line_count+=1;
    }else{
        myobj = document.getElementById("mill_id");
        myobj.remove();
    }

    if(queries[lbl_grade_pos] != ""){
        document.getElementById("grade").innerHTML = "GRADE: " + queries[lbl_grade_pos];
        line_count+=1;
        }else{
        myobj = document.getElementById("grade");
        myobj.remove();
    }

    if(queries[lbl_comment_pos] != ""){
        document.getElementById("comments").innerHTML = queries[lbl_comment_pos];
        line_count+=1;
        }else{
        myobj = document.getElementById("comments");
        myobj.remove();
    }

    if(queries[lbl_net_wt_pos] != "" || queries[lbl_gross_wt_pos] != ""){
        document.getElementById("net_wt").innerHTML = "";
        if(queries[lbl_net_wt_pos] != ""){
            document.getElementById("net_wt").innerHTML = 'NET WT: ' + queries[lbl_net_wt_pos] + 'kgs';
        }else{
            myobj = document.getElementById("net_wt");
            myobj.remove();
        }
        if(queries[lbl_gross_wt_pos] != ""){
            document.getElementById("gross_wt").innerHTML = 'GROSS WT: ' + queries[lbl_gross_wt_pos] + 'kgs';

        }else{
            myobj = document.getElementById("gross_wt");
            myobj.remove();
        }
        line_count+=1;
        }else{
            myobj = document.getElementById("net_wt");
            myobj.remove();
            myobj = document.getElementById("gross_wt");
            myobj.remove();
        }

    if(queries[lbl_scams_no_pos] != ""){
        document.getElementById("scams_no").innerHTML = 'SCAMS NO: ' + queries[lbl_scams_no_pos];
        line_count+=1;
        }else{
        myobj = document.getElementById("scams_no");
        myobj.remove();
    }

    if(queries[lbl_part_no_pos] != ""){
        document.getElementById("part_no").innerHTML = 'PART NO: ' + queries[lbl_part_no_pos];
        line_count+=1;
        }else{
        myobj = document.getElementById("part_no");
        myobj.remove();
    }

    if(queries[lbl_lamination_pos] == "" ){
        queries[lbl_lamination_pos] = "No Lamination";
    }

    if(queries[lbl_lamination_pos] != "No Lamination") {
        document.getElementById("lamination").innerHTML = "LAMI: " + queries[lbl_lamination_pos];
        line_count+=1;
        }else{
        myobj = document.getElementById("lamination");
        myobj.remove();
    }

    // Formatting
    if(queries[lbl_format_size] == 'big'){

        if((document.getElementById("customer").innerHTML).length < 20){
            document.getElementById("customer").style.fontSize = "50px";
        }else if((document.getElementById("customer").innerHTML).length > 20 && (document.getElementById("customer").innerHTML).length < 23){
            document.getElementById("customer").style.fontSize = "45px";
        }
        else{
            document.getElementById("customer").style.fontSize = "40px";
        }
    }else{
        if((document.getElementById("customer").innerHTML).length < 20){
            document.getElementById("customer").style.fontSize = "32px";
        }else if((document.getElementById("customer").innerHTML).length > 20 && (document.getElementById("customer").innerHTML).length < 23){
            document.getElementById("customer").style.fontSize = "28px";
        }
        else{
            document.getElementById("customer").style.fontSize = "22px";
        }
    }

    if(queries[lbl_format_size] == 'big'){
        document.getElementById('label_size').className = 'label_big';
        document.getElementById('label_details_size').className = 'label_details_big';
        //document.getElementById('label_details2').setAttribute("style","font-size:18px");
        var elements = document.getElementsByClassName('label_details2');
        for (var i = 0; i < elements.length; i++) {
          var element = elements[i];
          element.style.fontSize = "22px";

        }

        document.getElementById('machine').setAttribute("style","width:210px");
        document.getElementById('top_comment').setAttribute("style","width:210px");

    }

    resize_to_fit("customer");
    resize_to_fit("size");
    resize_to_fit("mill_id");
    resize_to_fit("grade");
    resize_to_fit("scams_no");
    resize_to_fit("part_no");
    resize_to_fit("lamination");
    resize_to_fit("comments");
    resize_to_fit("top_comment");

    qr_string = queries[lbl_smpl_no_pos] + ',' + queries[lbl_size_pos] + ',' + queries[lbl_numbers_pos] + ',';
    qr_string+= queries[lbl_net_wt_pos] + ',' + queries[lbl_gross_wt_pos] + ',' + queries[lbl_mat_status];

    var qrcode = new QRCode(document.getElementById("qr_code_block"),{
    text: qr_string,
    width: 90,
    height: 90,
    colorDark : "#000000",
    colorLight : "#ffffff",
    correctLevel : QRCode.CorrectLevel.H
        });



}


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
