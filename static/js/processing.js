const pkt_name_arr=[];

// This function is to set the focus when the page loads for CTL, NCTL and Reshearing operations
function setFocusToTextBox(operation){
    var customer;
    if(operation == "Narrow_CTL"){
        document.getElementById("output_length").focus();

    }
    if(operation == "Reshearing"){
        document.getElementById("output_width").focus();
        //customer = cust_name_for_label(document.getElementById("customer").value);
        //document.getElementById("customer").value = customer;
    }
    if(operation == "CTL"){
        document.getElementById("output_length").focus();
    }

    // Set processing date as today's date and disable future dates
    // Get the current date
    var currentDate = new Date();

    // Format the date to yyyy-mm-dd
    var year = currentDate.getFullYear();
    var month = String(currentDate.getMonth() + 1).padStart(2, '0');
    var day = String(currentDate.getDate()).padStart(2, '0');
    var formattedDate = year + '-' + month + '-' + day;

    // Set the max attribute of the date picker input
    var processing_date = document.getElementById('processing_date');
    processing_date.setAttribute('max', formattedDate);

    //if customer is TTSS, make mill, mill id and material type readonly
    var customer = document.getElementById("customer").value;
    if (customer.startsWith("TT STEEL SERVICE INDIA"))
    {
        document.getElementById('mill_id').readOnly = true;
        document.getElementById('mill').readOnly = true;
        document.getElementById('grade').readOnly = true;
        document.getElementById('mat_type').readOnly = true;
        //document.getElementById('scams_no').readOnly = true;
        document.getElementById('coating').readOnly = true;
    }

    var table = document.getElementById('packet_names');
    var packet_name;
    for (let i = 1; i < table.rows.length; i++) {
            const row = table.rows[i];
            packet_name = row.cells[0].lastChild.data + 'X' + row.cells[1].lastChild.data + '-' +row.cells[2].lastChild.data;
            // Traverse the cells in the current row
            pkt_name_arr.push(packet_name);
    }
}

//This function reloads the page if the user uses back to come to the page
//https://stackoverflow.com/questions/43043113/how-to-force-reloading-a-page-when-using-browser-back-button
window.addEventListener( "pageshow", function ( event ) {
  var historyTraversal = event.persisted ||
                         ( typeof window.performance != "undefined" &&
                              window.performance.navigation.type === 2 );
  if ( historyTraversal ) {
    // Handle page restore.
    window.location.reload();
  }
});

function length_of_coil(){
    var thickness = Number(document.getElementById("thickness").value);
    var input_material = document.getElementById("input_material").value;
    input_material = input_material.split(' x ')
    var width = Number(input_material[0]);
    var input_weight = Number(document.getElementById("input_weight").value);
    length_of_coil = input_weight/thickness/width/0.00000785;
    //if material is aluminium, the length has to be 3 times that of steel
    var grade = document.getElementById("grade").value;
    var mat_type = document.getElementById("mat_type").value;
    var mat_type_true = false;
    if(mat_type){
        if(mat_type.includes("ALUMINIUM")){
            mat_type_true = true;
        }
    }


    if(grade.includes("ALU ") || grade.includes("ALUMINIUM ") || mat_type_true){
        length_of_coil= length_of_coil*(7.85/2.71);
    }
    document.getElementById("length_of_coil").value = length_of_coil.toFixed(0);
}

// This function is to set the focus when the page loads for slitting operation
function setFocusToTextBox_Slit(operation){

        document.getElementById("output_width").focus();
        if(operation == "Mini_Slitting"){
            //add_row_for_length();
        }
        length_of_coil();

        //Set Processing Date and Setting date as today's date as max
        // Set processing date as today's date and disable future dates
    // Get the current date
    var currentDate = new Date();

    // Format the date to yyyy-mm-dd
    var year = currentDate.getFullYear();
    var month = String(currentDate.getMonth() + 1).padStart(2, '0');
    var day = String(currentDate.getDate()).padStart(2, '0');
    var formattedDate = year + '-' + month + '-' + day;

    // Set the max attribute of the date picker input
    var processing_date = document.getElementById('processing_date');
    processing_date.setAttribute('max', formattedDate);

    var setting_date = document.getElementById('setting_date');
    setting_date.setAttribute('max', formattedDate);

    //if customer is TTSS, make mill, mill id and material type readonly
    var customer = document.getElementById("customer").value;
    if (customer.startsWith("TT STEEL SERVICE INDIA"))
    {
        document.getElementById('mill_id').readOnly = true;
        document.getElementById('mill').readOnly = true;
        document.getElementById('grade').readOnly = true;
        document.getElementById('mat_type').readOnly = true;
        //document.getElementById('scams_no').readOnly = true;
        document.getElementById('coating').readOnly = true;
    }

}

//https://stackoverflow.com/questions/5629805/disabling-enter-key-for-form
//Disbale Enter key
window.addEventListener('keydown',function(e){if(e.keyIdentifier=='U+000A'||e.keyIdentifier=='Enter'||e.keyCode==13){if(e.target.nodeName=='INPUT'&&e.target.type=='text'){e.preventDefault();return false;}}},true);

//Disable Submit button once submit is pressed
window.addEventListener('beforeunload', function (e) {
  document.getElementById("submit").disabled = true;
});


//This is a function to check if packet name has been repeated
function check_packet_name(table_id, table_row){
    // Get the row where the change was made and calculate the weight of the processed material
	var rowCount = table_row.offsetParent.parentElement.rowIndex;
	var last_row = document.getElementById(table_id).rows[rowCount];

    var length =  Number(last_row.cells[1].lastChild.value);
    var width =  Number(last_row.cells[0].lastChild.value);
    var packet_name =  (last_row.cells[3].lastChild.value);

    packet_key = width + 'X' + length + '-' + packet_name;

    if(pkt_name_arr.includes(packet_key)){
        window.alert('Packet name is already used');
        last_row.cells[3].lastChild.value = '';
        last_row.cells[3].lastChild.focus();

    }else{
        pkt_name_arr.push(packet_key);
    }


}

// This function calculates the weight for CTL, NCTL and Reshearing functions
function for_packets_and_weight(table_id,table_row,operation){

   // Get the row where the change was made and calculate the weight of the processed material
	var rowCount = table_row.offsetParent.parentElement.rowIndex;
	var last_row = document.getElementById(table_id).rows[rowCount];
	//var numbers = Number(last_row.cells[3].lastChild.value);
	var thk = Number(document.getElementById('thickness').value);
	//var weight_pos = 5;
    var width =  Number(last_row.cells[0].lastChild.value);


    var length =  Number(last_row.cells[1].lastChild.value);

    var numbers =  Number(last_row.cells[4].lastChild.value);
    weight_pos = 5;

    var weight = (thk * width * length * numbers * 0.00000785)/1000;
    last_row.cells[weight_pos].lastChild.value = weight.toFixed(3);
    var rm_weight = Number(document.getElementById("weight").value);

    //if material is aluminium, the weight has to be 1/3 that of steel
    var grade = document.getElementById("grade").value;
    var mat_type = document.getElementById("mat_type").value;
    var mat_type_true = false;
    if(mat_type){
        if(mat_type.includes("ALUMINIUM")){
            mat_type_true = true;
        }
    }

    if(grade.includes("ALU ") || grade.includes("ALUMINIUM ") || mat_type_true){
        last_row.cells[weight_pos].lastChild.value = (weight/3).toFixed(3);
    }

    calculate_wt_and_cuts(table_id);
}

// This function calculates the weight for Trap NCTL and Reshearing functions
function for_packets_and_weight_trap(table_id,table_row,operation){

   // Get the row where the change was made and calculate the weight of the processed material
	var rowCount = table_row.offsetParent.parentElement.rowIndex;
	var last_row = document.getElementById(table_id).rows[rowCount];
	//var numbers = Number(last_row.cells[3].lastChild.value);
	var thk = Number(document.getElementById('thickness').value);
	//var weight_pos = 5;
    var width =  Number(last_row.cells[0].lastChild.value);


    var length1 =  Number(last_row.cells[1].lastChild.value);
    var length2 =  Number(last_row.cells[2].lastChild.value);

    var numbers =  Number(last_row.cells[5].lastChild.value);
    weight_pos = 6;

    var length = (length1+length2)/2;
    var weight = (thk * width * length * numbers * 0.00000785)/1000;
    last_row.cells[weight_pos].lastChild.value = weight.toFixed(3);
    var rm_weight = Number(document.getElementById("weight").value);

    //if material is aluminium, the weight has to be 1/3 that of steel
    var grade = document.getElementById("grade").value;
    var mat_type = document.getElementById("mat_type").value;
    var mat_type_true = false;
    if(mat_type){
        if(mat_type.includes("ALUMINIUM")){
            mat_type_true = true;
        }
    }

    if(grade.includes("ALU ") || grade.includes("ALUMINIUM ") || mat_type_true){
        last_row.cells[weight_pos].lastChild.value = (weight/3).toFixed(3);
    }

    calculate_wt_and_cuts_trap(table_id);
}


// To calculate processed weight and no of cuts every time numbers are changed
function calculate_wt_and_cuts(table_id){
    var table = document.getElementById(table_id);
    var total_processed_wt =0;
    var total_cuts = 0;
    var total_pkts;
    for (var i = 1, row; row = table.rows[i]; i++) {
        total_processed_wt += Number(row.cells[5].lastChild.value);
        total_cuts += Number(row.cells[4].lastChild.value);

    }
    //var total_order_wt = Number(document.getElementById("order_wt").value);
    //var completed_proc_wt = Number(document.getElementById("tot_proc_wt").value);
    //var scrap_wt = total_order_wt - total_processed_wt - completed_proc_wt ;


    document.getElementById("total_processed_wt").value = Number(total_processed_wt.toFixed(3));
    document.getElementById("total_cuts").value = total_cuts;
    document.getElementById("total_packets").value = table.rows.length - 1;

    validate();

    //document.getElementById("balance_wt").value = scrap_wt.toFixed(3);
    //document.getElementById("scrap_wt").value = Number(scrap_wt.toFixed(3));
}

// To calculate processed weight and no of cuts every time numbers are changed
function calculate_wt_and_cuts_trap(table_id){
    var table = document.getElementById(table_id);
    var total_processed_wt =0;
    var total_cuts = 0;
    var total_pkts;
    for (var i = 1, row; row = table.rows[i]; i++) {
        total_processed_wt += Number(row.cells[6].lastChild.value);
        total_cuts += Number(row.cells[5].lastChild.value);

    }
    //var total_order_wt = Number(document.getElementById("order_wt").value);
    //var completed_proc_wt = Number(document.getElementById("tot_proc_wt").value);
    //var scrap_wt = total_order_wt - total_processed_wt - completed_proc_wt ;


    document.getElementById("total_processed_wt").value = Number(total_processed_wt.toFixed(3));
    document.getElementById("total_cuts").value = total_cuts;
    document.getElementById("total_packets").value = table.rows.length - 1;

    validate();

    //document.getElementById("balance_wt").value = scrap_wt.toFixed(3);
    //document.getElementById("scrap_wt").value = Number(scrap_wt.toFixed(3));
}

function time_taken(){
   var t1 = document.getElementById("start_time").value;
   var t2 = document.getElementById("end_time").value;

   var parts = t1.split(':');
   var d1 = Number(parts[0])*60 + Number(parts[1]);
   parts = t2.split(':');
   var d2 = Number(parts[0])*60 + Number(parts[1]);
   // this would also work
   // d2.toTimeString().substr(0, d2.toTimeString().indexOf(' '));
   if(d2>d1){
    var diff =  d2 - d1;
    document.getElementById("processing_time").value = diff;
   }
   else{
    document.getElementById("end_time").value = "";
    alert("Please re-enter the time. End time must be greater than start time");
    document.getElementById("start_time").focus();
   }
    validate();
}

function time_taken_setting(){
   var t1 = document.getElementById("setting_start_time").value;
   var t2 = document.getElementById("setting_end_time").value;
   var parts = t1.split(':');
   var d1 = Number(parts[0])*60 + Number(parts[1]);
   parts = t2.split(':');
   var d2 = Number(parts[0])*60 + Number(parts[1]);
   // this would also work
   // d2.toTimeString().substr(0, d2.toTimeString().indexOf(' '));
   if(d2>=d1){
    var diff =  d2 - d1;
    document.getElementById("setting_time").value = diff;
   }
   else{
    document.getElementById("setting_end_time").value = "";
    alert("Please re-enter the time. End time must be greater than start time");
    document.getElementById("setting_start_time").focus();
   }
}
function change_part_length(table_id){
    var table = document.getElementById(table_id);
    var total_processed_wt =0;
    var total_length = 0;
    var total_parts = 0;
    for (var i = 1, row; row = table.rows[i]; i++) {
        total_length += Number(row.cells[0].lastChild.value);
    }
    document.getElementById("total_length").value = total_length;
    document.getElementById("total_parts").value = table.rows.length-1;
    if(document.getElementById("total_width").value){
    get_part_weight();
   }

}

function change_width(table_id){
    var table = document.getElementById(table_id);
    var total_width =0;

    for (var i = 1, row; row = table.rows[i]; i++) {
        total_width += Number(row.cells[0].lastChild.value);
    }
    document.getElementById("total_width").value = total_width;

    var rm_size = document.getElementById('input_material').value;
    rm_size = rm_size.split(' x ');
    var rm_width = rm_size[0];

    if(total_width > rm_width){
        alert('Processed width is greater than Input material width. Please check');
        document.getElementById('submit').disabled = true;
    }
    else{
        document.getElementById('submit').disabled = false;
    }
   if(document.getElementById("total_length").value){
    get_part_weight();
   }

}

//Calculates processed weight for slitting
function get_part_weight(){
    var total_length = Number(document.getElementById("total_length").value);
    var steel_density = 0.00000785;
    var aluminium_density = 0.0000027;
    var thickness = Number(document.getElementById("thickness").value);
    var input_material = (document.getElementById("input_material").value);
    var grade = document.getElementById("grade").value;
    var mat_type = document.getElementById("mat_type").value;

    input_material = input_material.split("x");

    var width = Number(input_material[0]);
    rm_wt = Number(document.getElementById("input_weight").value);

    var operation = document.getElementById("operation").value;

    if(operation == "Mini_Slitting"){
        width= document.getElementById("total_width").value;
    }

    var mat_type_true = false;
    if(mat_type){
        if(mat_type.includes("ALUMINIUM")){
            mat_type_true = true;
        }
    }

    if(grade.includes("ALU ") || grade.includes("ALUMINIUM ") || mat_type_true){
        var total_processed_wt = thickness * width * total_length * aluminium_density;
        var coil_length = rm_wt/thickness/width/aluminium_density;
        document.getElementById("total_processed_wt").value = total_processed_wt.toFixed(3);
    }else{
        var total_processed_wt = thickness * width * total_length * steel_density;
        var coil_length = rm_wt/thickness/width/steel_density;
        document.getElementById("total_processed_wt").value = total_processed_wt.toFixed(3);
    }

    var allowance = 1.01;
    if((total_processed_wt ) > allowance*rm_wt){
        alert('Processed wt is greater than Input material weight. Please check');
        document.getElementById('submit').disabled = true;
    }
    else{
        document.getElementById('submit').disabled = false;
    }

    //var total_order_wt = Number(document.getElementById("order_wt").value);
    //var completed_proc_wt = Number(document.getElementById("tot_proc_wt").value);
    //var scrap_wt = total_order_wt - total_processed_wt - completed_proc_wt ;


    //document.getElementById("balance_wt").value = scrap_wt.toFixed(3);

    //validate();
}

function add_row_for_length(){
    var input_size_tbl = document.getElementById('numbers_pkts1');
    var input_material, newHTML;
    var input_mtrl_array = [];
    var html = '<tr><td><input type = "text" id="ip_sz_for_length" value = "%input_sz%" readonly></td><td><input type="number" id="length_run_for_sz" value = ""></td><td><input type="number" id="no_of_parts_for_sz" value = "" readonly><td><input type="number" id="wt_run_for_sz" value = "" readonly></td></tr>'
    for(i=1;i<input_size_tbl.rows.length;i++){
        if (input_mtrl_array.includes(input_size_tbl.rows[i].cells[0].childNodes[0].value)== false){
            input_mtrl_array.push(input_size_tbl.rows[i].cells[0].childNodes[0].value);
        }
    }
    for(i=0;i<input_mtrl_array.length;i++){
        newHTML = html.replace('%input_sz%', input_mtrl_array[i]);
        document.getElementById('length_processed').insertAdjacentHTML('beforeend', newHTML);
    }

}

function addRowPartsTable(tableID){
    var table = document.getElementById(tableID);

    var rowCount = table.rows.length;
    var row = table.insertRow(rowCount);
}

function addRow(tableID)
	 {

			var table = document.getElementById(tableID);
			var operation = document.getElementById("operation").value;

			var rowCount = table.rows.length;
			var row = table.insertRow(rowCount);
            if(tableID == "part_tbl" || tableID == "numbers_pkts"){
                row.id = rowCount;
            }
			var last_row = document.getElementById(tableID).rows[rowCount-1];

			var colCount = table.rows[1].cells.length;

			for(var i=0; i<colCount; i++) {

				var newcell	= row.insertCell(i);

				newcell.innerHTML = table.rows[1].cells[i].innerHTML;
				newcell.hidden = table.rows[1].cells[i].hidden;

                if(tableID == "numbers_pkts"){
                    if(newcell.lastElementChild.id == 'output_width' || newcell.lastElementChild.id == 'output_length'){
				        newcell.lastElementChild.value = last_row.cells[i].lastElementChild.value;
                    }

                if(newcell.lastElementChild.id == 'packet_name'){
                    var str = last_row.cells[i].lastElementChild.value;
                    var index = str.length - 1;

                      while (index >= 0) {
                        if (/[a-zA-Z]/.test(str[index])) {
                          break;
                        }
                        index--;
                      }

                    var secondPart = parseInt(str.substring(index+1)) +1;
                    var firstPart;
                    if (secondPart > 9){
                        firstPart = str.substring(0, index+1);
                    }else{
                        firstPart = str.substring(0, index+2);
                    }



                    console.log(firstPart);
                    console.log(secondPart);
                    newcell.lastElementChild.value = firstPart + secondPart.toString();
                    //return [firstPart, secondPart];
                }
				//if(operation == 'Reshearing' || operation == 'Narrow_CTL'){
				//    newcell.lastChild.value = table.rows[rowCount-1].cells[i].lastChild.value;
				//}
				//alert(newcell.childNodes);
				/*switch(newcell.childNodes[0].type) {
					case "text":
							newcell.childNodes[0].value = "";
							break;
					case "checkbox":
							newcell.childNodes[0].checked = false;
							break;
					case "select-one":
							newcell.childNodes[0].selectedIndex = 0;
							break;
				}*/
				}
			}
    }

function validate(){
    var total_processed_wt, total_order_wt, completed_proc_wt, order_completed_chk, rm_wt;
    //total_processed_wt = Number(document.getElementById("total_processed_wt").value);
    //total_order_wt = Number(document.getElementById("order_wt").value);
    completed_proc_wt = Number(document.getElementById("total_processed_wt").value);
    rm_wt = Number(document.getElementById("weight").value);
    order_completed_chk = true;
    total_processed_wt = 0;

    //if (total_order_wt*0.98 > (total_processed_wt + completed_proc_wt)){
    //    order_completed_chk = confirm("Order weight is greater than Processing Weight. Should the order be marked complete? /nPress OK to mark order complete");
    //    }
    //if(order_completed_chk == false){
    //    document.getElementById("balance_wt").value = 0;
    //}

    // If RM weight is more then the check of 7% is ok. But when RM weight is less, then  5% margin becomes less
    // So, when RM less than 3MT, I am giving an allowance of 8%

    var allowance = 1.01;
    if(rm_wt < 3){
        allowance = 1.02;
    }

    if((total_processed_wt + completed_proc_wt) > allowance*rm_wt){
        alert('Processed wt is greater than Input material weight. Please check');
        document.getElementById('submit').disabled = true;
    }
    else{
        document.getElementById('submit').disabled = false;
    }


 }

function print_label(){
   var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var data = "";
    var size_pos = 4;
    var fg_table = document.getElementById('fg_table');
    for(i=0;i<10;i++){
        // This is because size has been made a text box to give more flexibility
        if(i==4){
            data = data + fg_table.rows[rowId].cells[size_pos].lastChild.value + '&';
        }else{
            data = data + fg_table.rows[rowId].cells[i].lastChild.data + '&';
        }

    }
    // Since Comments and 2nd customer are text boxes; we will have to take value and not data property
    var comment_pos = 10;
    //if(fg_table.rows[rowId].cells[comment_pos].lastChild.value != ""){
    data = data + fg_table.rows[rowId].cells[comment_pos].lastChild.value + '&';
    //}
    var second_customer_pos = 11;
    var customer_pos = 2;
    if(fg_table.rows[rowId].cells[customer_pos].lastChild.data == "TSDPL"){
        data = data + fg_table.rows[rowId].cells[second_customer_pos].lastChild.value ;
    }
    var new_page;

    new_page = window.open('print_label_slit?' + data);
    //new_page.document.write("output");
}

function print_label_slit_new(){
    var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var data = "";
    var size_pos = 0;
    var coil_length_pos = 1;
    var packet_name_pos = 2;
    var second_customer_pos = 3;
    var net_wt_pos = 4;
    var gross_wt_pos = 5;
    var lamination_pos = 6;
    var batch_no_pos = 7;
    var top_comment_pos = 8;
    var comment_pos = 9;
    var status_pos = 10;
    var label_size_pos = 11;
    var label_format_pos = 12;

    var fg_table = document.getElementById('fg_table');

    //Keeping same format as other stickers for ease of processing in print_label.js
    data += document.getElementById('lbl_smpl_no').value + '&';
    data += document.getElementById('lbl_prod_date').value + '&';
    data += document.getElementById('lbl_customer').value + '&';
    data += document.getElementById('lbl_machine').value + '&';
    data += fg_table.rows[rowId].cells[size_pos].lastChild.value + '&';
    data += fg_table.rows[rowId].cells[coil_length_pos].lastChild.value + '&';
    data += fg_table.rows[rowId].cells[packet_name_pos].lastChild.value + '&';
    data += fg_table.rows[rowId].cells[lamination_pos].lastChild.value + '&';
    data += document.getElementById('lbl_mill_id').value + '&';
    data += document.getElementById('lbl_grade').value + '&';
    data += document.getElementById('lbl_mill').value + '&';
    data += fg_table.rows[rowId].cells[comment_pos].lastChild.value + '&';
    data += fg_table.rows[rowId].cells[second_customer_pos].lastChild.value + '&';
    data += document.getElementById('lbl_mat_type').value + '&';
    data += document.getElementById('lbl_scams_no').value + '&';

    //Adding blanks for coating, part_no
    data += '&' + '&';
    data += fg_table.rows[rowId].cells[batch_no_pos].lastChild.value + '&';
    data += fg_table.rows[rowId].cells[net_wt_pos].lastChild.value + '&';
    data += fg_table.rows[rowId].cells[gross_wt_pos].lastChild.value + '&';
    data += fg_table.rows[rowId].cells[top_comment_pos].lastChild.value + '&';
    data += fg_table.rows[rowId].cells[label_size_pos].lastChild.value + '&';
    data += fg_table.rows[rowId].cells[status_pos].lastChild.value + '&';
    data += document.getElementById('lbl_qc_name').value;

    var new_page;
    if(document.getElementById('lbl_format').value == "TSL"){
        new_page = window.open('print_label_tsl?' + data);
    }else{
        new_page = window.open('print_label?' + data);
    }
}

function print_label_new(){
    lbl_format = document.getElementById('lbl_format').value;
    lbl_format_size = document.getElementById('lbl_format_size').value;
    var fg_table = document.getElementById('label_table');
    var data = "";
    data += document.getElementById('lbl_smpl_no').value + '&';
    data += document.getElementById('lbl_prod_date').value + '&';
    data += document.getElementById('lbl_customer').value + '&';
    data += document.getElementById('lbl_machine').value + '&';
    data += document.getElementById('lbl_size').value + '&';
    data += document.getElementById('lbl_numbers').value + '&';
    data += document.getElementById('lbl_packet_name').value + '&';
    data += document.getElementById('lbl_lamination').value + '&';
    data += document.getElementById('lbl_mill_id').value + '&';
    data += document.getElementById('lbl_grade').value + '&';
    data += document.getElementById('lbl_mill').value + '&';
    data += document.getElementById('lbl_comment').value + '&';
    data += document.getElementById('lbl_2nd_customer').value + '&';
    data += document.getElementById('lbl_mat_type').value + '&';
    data += document.getElementById('lbl_scams_no').value + document.getElementById('lbl_scams_pkt').value + '&';
    data += document.getElementById('lbl_coating').value + '&';
    data += document.getElementById('lbl_part_no').value + '&';
    data += document.getElementById('lbl_batch_no').value + '&';
    data += document.getElementById('lbl_net_wt').value + '&';
    data += document.getElementById('lbl_gross_wt').value + '&';
    data += document.getElementById('lbl_top_comment').value + '&';
    data += document.getElementById('lbl_format_size').value + '&';
    data += document.getElementById('lbl_mat_status').value + '&';
    data += document.getElementById('lbl_qc_name').value + '&';

    var new_page;
    if(document.getElementById('lbl_format').value == "TSL"){
        new_page = window.open('print_label_tsl?' + data);
    }else{
        new_page = window.open('print_label?' + data);
    }

}

function print_label_big(){
   var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var data = "";
    var fg_table = document.getElementById('fg_table');
    for(i=0;i<11;i++){
        data = data + fg_table.rows[rowId].cells[i].lastChild.value + '&';
    }
    // Since Comments and 2nd customer are text boxes; we will have to take value and not data property
    var comment_pos = 11;
    var mat_type_pos = 12;
    //if(fg_table.rows[rowId].cells[comment_pos].lastChild.value != ""){
    data = data + fg_table.rows[rowId].cells[comment_pos].lastChild.value + '&' ;
    //}
    var second_customer_pos = 12;

    var customer_pos = 2;
    if(fg_table.rows[rowId].cells[customer_pos].lastChild.value == "TSDPL"){
        data = data + fg_table.rows[rowId].cells[second_customer_pos].lastChild.value + '&';
        mat_type_pos = 13;
    }

    data = data + fg_table.rows[rowId].cells[mat_type_pos].lastChild.value;
    var new_page;

    new_page = window.open('print_label_big?' + data);
    //new_page.document.write("output");
}

function print_label_reshearing(){
   var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var data = "";
    var fg_table = document.getElementById('fg_table');
    for(i=0;i<10;i++){
        data = data + fg_table.rows[rowId].cells[i].lastChild.data + '&';
    }
    // Since Comments and 2nd customer are text boxes; we will have to take value and not data property
    var comment_pos = 10;
    var mat_type_pos = 11;
    //if(fg_table.rows[rowId].cells[comment_pos].lastChild.value != ""){
    data = data + fg_table.rows[rowId].cells[comment_pos].lastChild.value + '&' ;
    //}
    var second_customer_pos = 11;

    var customer_pos = 2;
    if(fg_table.rows[rowId].cells[customer_pos].lastChild.data == "TSDPL"){
        data = data + fg_table.rows[rowId].cells[second_customer_pos].lastChild.value + '&';
        mat_type_pos = 12;
    }

    data = data + fg_table.rows[rowId].cells[mat_type_pos].lastChild.value;
    var new_page;

    new_page = window.open('print_label_reshearing?' + data);
    //new_page.document.write("output");
}

//HTML displays the date in yyyy-mm-dd format. This is not suitable for the label.
// This function converts yyyy-mm-dd to dd/mm/yyyy
function change_date_format(date){
    var ddmmyyyy;
    date= date.split('-');
    ddmmyyyy = date[2] + '/' + date[1] + '/' + date[0];
    return ddmmyyyy;
}

//This function will manage the customer name for the label
function cust_name_for_label(customer){
    customer = customer.toLowerCase();
    // Start by removing pvt ltd or PRIVATE LIMITED or LIMITED or LTD in the name. Also remove anything after [
    customer = customer.replace("private",'');
    customer = customer.replace("limited",'');
    customer = customer.replace("pvt",'');
    customer = customer.replace("ltd",'');
    customer = customer.replaceAll(".",'');
    customer = customer.replaceAll("&",' and ');

    temp_customer = customer.split('[');
    customer =  temp_customer[0];
    var cust_name;
    var cust_split;

    if(customer.startsWith("veer o metal") || customer.startsWith("veer-o-metal")){
        cust_name= "Veer O Metals";
    }
    else if(customer.startsWith("ttp technolgies")){
        cust_name= "TTP Technologies";
    }
    else if(customer.startsWith("mpp technolgies")){
        cust_name= "MPP Technologies";
    }
    else if(customer.startsWith("nash industries")){
        cust_name= "Nash Industries";
    }
    else if(customer.startsWith("balmer lawrie")){
        cust_name= "Balmer Lawrie";
    }
    else if(customer.startsWith("metal storage")){
        cust_name= "Metal Storage";
    }
    else if(customer.startsWith("bharat metal")){
        cust_name= "Bharat Metal";
    }
    else if(customer.startsWith("aditya auto")){
        cust_name= "Aditya Auto";
    }
    else if(customer.startsWith("satrac eng")){
        cust_name= "SATRAC";
    }
    else if(customer.startsWith("mallik eng")){
        cust_name= "Mallik Engg";
    }
    else if(customer.startsWith("kanunga")){
        cust_name= "Kanunga Extrusion";
    }
    else if(customer.startsWith("sun zone")){
        cust_name= "SUN ZONE SOLAR";
    }
    else if(customer.startsWith("tata steel downstream products")){
        cust_name= "TSDPL";
    }
    else if(customer.startsWith("honda")){
        cust_name= "HONDA";
    }
    else if(customer.startsWith("tt steel")){
        cust_name= "TTSSI";
    }
    else if(customer.startsWith("jr and ")){
        cust_name= "J R AND COMPANY";
    }
    else if(customer.startsWith("vns ")){
        cust_name= "VNS";
    }
    else{
        cust_split = customer.split(' ');
        if(cust_split.length >=2){
            customer = cust_split[0] + ' ' + cust_split[1];
        }
        cust_name = customer.toUpperCase();
    }

    return cust_name;
}

//This is for label in new format for slitting
function make_label_new_slit(th){

    qc_name = document.getElementById("names_of_qc").value;
    if(!qc_name){
        window.alert("QC Name is not entered.");
        return; // Exit the function
    }

    var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var row_id = th.parentNode.id;

    var width_table = document.getElementById('numbers_pkts1');
    var parts_table = document.getElementById('part_tbl');
    var fg_table = document.getElementById('fg_table');

    //Get values for the rows
    //Row 1
    var smpl_no = document.getElementById("smpl_no").value;
    var prod_date = document.getElementById("processing_date").value;
    prod_date = change_date_format(prod_date);
    var machine = document.getElementById("operation").value;

    //Row 2
    var mill_name = document.getElementById("mill").value;
    mill_name = mill_name.split(' ');
    var mill;
    if(mill_name[0] == ''){
        mill = "MILL"
    }else{
        mill = mill_name[0];
    }
    var mill_id = document.getElementById("mill_id").value;
    if(mill_name[0] == ''){
        mill = "MILL"
    }else{
        mill = mill_name[0];
    }
    if(mill_id == ''){
     mill_id = 'N/A';
    }
    var customer = document.getElementById("customer").value;
    customer = cust_name_for_label(customer);

    //Row 3
    var grade_field = document.getElementById("grade").value;
    var grade_coating = "";
    //Grade. Check if grade exists
    /*if (grade_field.includes("GRADE")){
        grade = grade_field.split("GRADE").pop();
        grade_coating = grade.split(' ');
        grade=grade_coating[0];
        grade = grade.slice(1);
        grade = grade.replace('.','');

    }*/

    var material_type = '';
    var grade = '';
    var coating = '';
    var scams_no = '';
    var incoming_date = (document.getElementById('incoming_date').value);
    incoming_date = incoming_date.split('/');
    var new_incoming_date = incoming_date[1] + '/' + incoming_date[0] + '/' + incoming_date[2];
    new_incoming_date = new Date(new_incoming_date);
    var check_date = new Date("04/25/2023");


    if (grade_field.length > 0){
    if(new_incoming_date < check_date){
        grade_field = grade_field.split(';');
        //Material Type
        /*var mat_type = grade_field.split("ID");

        mat_type = mat_type[0].split("GRADE");
        var material_type = mat_type[0];
        material_type = material_type.replaceAll('COIL','');
        material_type = material_type.replaceAll('SHEETS','');
        material_type = material_type.replaceAll('.','');*/
        material_type = grade_field[0];
        material_type = material_type.replaceAll('COIL','');
        material_type = material_type.replaceAll('SHEETS','');
        material_type = material_type.replaceAll('.','');
        material_type = material_type.replaceAll('MAT TYPE:','');

        for(i=1;i<grade_field.length;i++){
            if(grade_field[i].includes("GRADE")){
                grade = grade_field[i].split("GRADE").pop();
                grade = grade.replaceAll(':','');
                grade = grade.trim();
            }
            if(grade_field[i].includes("COATING")){
                coating = grade_field[i].split("COATING").pop();
                coating = coating.replaceAll(':','');
                coating = coating.trim();
            }

            if(grade_field[i].includes("SCAMS NO")){
                scams_no = grade_field[i].split("SCAMS NO").pop();
                scams_no = scams_no.replaceAll(':','');
                scams_no = scams_no.trim();
            }
        }
    }else{
            material_type = document.getElementById('mat_type').value;

            material_type = material_type.replaceAll('COIL','');
            material_type = material_type.replaceAll('SHEETS','');
            material_type = material_type.replaceAll('.','');


            grade = document.getElementById('grade').value;
            scams_no = document.getElementById('scams_no').value;
            if(scams_no == 'None'){
                scams_no = '';
            }
            coating = document.getElementById('coating').value;
            if(coating == 'None'){
                coating = '';
            }
        }
    }
    else if(grade_field == ''){
        grade = 'N/A';
    }
    else{
        grade = grade_field;
    }

    //Populate the rows
    //Row 1
    document.getElementById('lbl_smpl_no').value = smpl_no;
    document.getElementById('lbl_prod_date').value = prod_date;
    document.getElementById('lbl_machine').value = machine;

    //Row 2
    document.getElementById('lbl_mill').value = mill;
    document.getElementById('lbl_mill_id').value = mill_id;
    document.getElementById('lbl_customer').value = customer;

    //Row 3
    document.getElementById('lbl_grade').value = grade.trimEnd();
    document.getElementById('lbl_mat_type').value = material_type.trimEnd();
    document.getElementById('lbl_scams_no').value = scams_no.trimEnd();
    document.getElementById('lbl_qc_name').value = qc_name;

    //If customer is TTSS grade, material type to be made read only
    var customer = document.getElementById("customer").value;
    if (customer.startsWith("TT STEEL SERVICE INDIA"))
    {
        document.getElementById('lbl_grade').readOnly = true;
        document.getElementById('lbl_mat_type').readOnly = true;
        //document.getElementById('lbl_scams_no').readOnly = true;
    }

    //FG_Table population
    var html = '<tr id= %id%>' +
            '<td><input type="text" style="width:100px;border: 0px none;" id="lbl_size" name="lbl_size" value="%size%"></td>' +
            '<td><input type="text" style="width:100px;border: 0px none;" id="lbl_coil_length" name="lbl_coil_length" value="%coil_length%"></td>' +
            '<td><input type="text" style="width:100px;" id="lbl_packet_name" name="lbl_packet_name" value="%packet_name%"></td>' +
            '<td><input type="text" style="width:130px;"  id="lbl_2nd_customer" name="lbl_2nd_customer"></td>' +
            '<td><input type="text" style="width:100px;"  id="lbl_net_wt" name="lbl_net_wt"></td>' +
            '<td><input type="text" style="width:100px;" id="lbl_gross_wt" name="lbl_gross_wt"></td>' +
            '<td><input type="text" style="width:130px;"  id="lbl_lamination" name="lbl_lamination"></td>' +
            '<td><input type="text" style="width:130px;"  id="lbl_batch_no" name="lbl_batch_no"></td>' +
            '<td><input type="text" style="width:130px;"  id="lbl_top_comment" name="lbl_top_comment"></td>' +
            '<td><input type="text" style="width:130px;"  id="lbl_comment" name="lbl_comment"></td>' +
            '<td><input type="text" style="width:50px;"  id="lbl_mat_status" name="lbl_mat_status" value="%status%"></td>' +

            '<td><select name ="lbl_format_size" id="lbl_format_size">' +
            '<option value ="big">BIG</option><option value ="small">SMALL</option></select></td>' +
            '<td><select name ="lbl_format" id="lbl_format"><option value ="SMPL">SMPL</option>' +
            '<option value ="TTS">TTS</option><option value ="HONDA">HONDA</option>' +
            '<option value ="TSL">TSL</option></select></td>' +
            '<td><input type = "button" class="btn btn-default" value="Print" onclick="print_label_slit_new()"></td>' +
            '</tr>';

    var part_length = parts_table.rows[rowId].cells[0].lastChild.value;
    var part_name = parts_table.rows[rowId].cells[1].lastChild.value;
    var newHTML = html.replace('%coil_length%', part_length);
    var newNEWHTML= '';
    var width, width_name, width_part_name, width_status;
    var thickness = document.getElementById("thickness").value;
    var id = 1;
    if (fg_table.rows.length > 2){
        id = fg_table.rows.length;
    }

    for(j=1;j<width_table.rows.length;j++){
        width = width_table.rows[j].cells[0].lastChild.value;
        if( width_table.rows[j].cells[0].lastChild.value == "0"){
            width = "BAL";
        }
        width_name = width_table.rows[j].cells[1].lastChild.value;
        width_status = width_table.rows[j].cells[2].lastElementChild.selectedOptions[0].innerHTML;
        size = thickness + " X " + width + " x Coil";
        width_part_name = part_name + width_name;
        newNEWHTML = newHTML.replace('%packet_name%', width_part_name);
        newNEWHTML = newNEWHTML.replace('%size%', size);
        //newNEWHTML = newNEWHTML.replace('%coil_name%', width_part_name);
        newNEWHTML = newNEWHTML.replace('%status%', width_status);
        newNEWHTML = newNEWHTML.replace('%id%', id);
        document.getElementById('fg_table').insertAdjacentHTML('beforeend', newNEWHTML);
        id = id +1;
    }

}

//This function is to get details for the sticker for the specific part
function make__part_label_slit(th){
    var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var row_id = th.parentNode.id;

    var width_table = document.getElementById('numbers_pkts1');
    var parts_table = document.getElementById('part_tbl');
    var fg_table = document.getElementById('fg_table');
    var newHTML = '';
    var newNEWHTML = '';
    var id = 1;
    if (fg_table.rows.length > 2){
        id = fg_table.rows.length;
    };
    var part_length,part_name, width, width_name, width_part_name, size, prod_date;
    var html = '<tr id= %id%><td>%smpl_no%</td><td>%prod_date%</td><td>%customer%</td><td>%machine%</td><td><input type="text" id="size" name="size" value = "%size%"></td><td>%coil_length%</td><td>%coil_name%</td><td>%mill_id%</td><td>%grade%</td><td>%mill%</td><td><input type="text" id="comment" name="comment"></td><td><input type = "button" class="btn btn-default" value="Print" onclick="print_label()"></td></tr>'

    // If customer is TSDPL; 2nd customer field has to be added
    var customer = document.getElementById("customer").value;
    customer = cust_name_for_label(customer);
    /*if (customer == "TSDPL" ){
        html = '<tr id= %id%><td>%smpl_no%</td><td>%prod_date%</td><td>%customer%</td><td>%machine%</td><td><input type="text" id="size" name="size" value = "%size%"></td><td>%coil_length%</td><td>%coil_name%</td><td>%mill_id%</td><td>%grade%</td><td>%mill%</td><td><input type="text" id="comment" name="comment"></td><td><input type="text" id="customer2nd" name="customer2nd"></td><td><input type = "button" class="btn btn-default" value="Print" onclick="print_label()"></td></tr>'
    }*/

    var thickness = document.getElementById("thickness").value;

    var mill_id = document.getElementById("mill_id").value;
    var grade_field = document.getElementById("grade").value;
    var smpl_no = document.getElementById("smpl_no").value;
    var mill_name = document.getElementById("mill").value;
    mill_name = mill_name.split(' ');
    var mill;
    if(mill_name[0] == ''){
        mill = "MILL"
    }else{
        mill = mill_name[0];
    }
    if(mill_id == ''){
     mill_id = 'N/A';
    }
    if(grade = ''){
        grade = 'N/A';
    }


    //var customer2 = document.getElementById("customer2").value;

    var prod_date = document.getElementById("processing_date").value;
    prod_date = change_date_format(prod_date);
    if (grade_field.includes("GRADE")){
        grade = grade_field.split("GRADE").pop();
        grade = grade.slice(1);
        //grade_field = grade_field.split(".");
        //grade = grade_field[0];
    }
    else{
        grade = grade_field;
    }



    part_length = parts_table.rows[rowId].cells[0].lastChild.value;
    part_name = parts_table.rows[rowId].cells[1].lastChild.value;
    newHTML = html.replace('%coil_length%', part_length);
    newHTML = newHTML.replace('%grade%', grade);
    newHTML = newHTML.replace('%smpl_no%', smpl_no);
    newHTML = newHTML.replace('%customer%', customer);
    newHTML = newHTML.replace('%machine%', "Slitting");
    newHTML = newHTML.replace('%mill_id%', mill_id);
    newHTML = newHTML.replace('%prod_date%', prod_date);
    newHTML = newHTML.replace('%mill%', mill);

    for(j=1;j<width_table.rows.length;j++){
        width = width_table.rows[j].cells[0].lastChild.value;
        if( width_table.rows[j].cells[0].lastChild.value == "0"){
            width = "BAL";
        }
        width_name = width_table.rows[j].cells[1].lastChild.value;
        size = thickness + " X " + width + " x Coil";
        width_part_name = part_name + width_name;
        newNEWHTML = newHTML.replace('%coil_name%', width_part_name);
        newNEWHTML = newNEWHTML.replace('%size%', size);
        newNEWHTML = newNEWHTML.replace('%coil_name%', width_part_name);
        newNEWHTML = newNEWHTML.replace('%id%', id);
        document.getElementById('fg_table').insertAdjacentHTML('beforeend', newNEWHTML);
        id = id +1;
    }


}

//Fill label table for CTL
function make__part_label_ctl(th){
    var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var row_id = th.parentNode.id;

    var numbers_table = document.getElementById('numbers_pkts');
    //var parts_table = document.getElementById('part_tbl');
    var newHTML = '';
    var newNEWHTML = '';
    var id =1;
    var packet_nos,packet_name, output_length, width, width_part_name, size, prod_date, lamination, lami_type;
    var html = '<tr id= %id%><td><input type="text" style="width:130px;border: 0px none;" id="lab_smpl_no" name="lab_smpl_no" value="%smpl_no%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_prod_date" name="lab_prod_date" value="%prod_date%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_customer" name="lab_customer" value="%customer%"></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_machine" name="lab_machine" value="%machine%" readonly></td>' +
                '<td><input type="text" style="border: 0px none;" id="lab_size" name="lab_size" value="%size%"></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_numbers" name="lab_numbers" value="%numbers%" ></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_packet_no" name="lab_packet_no" value="%packet_no%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_lamination" name="lab_lamination" value="%lamination%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_mill_id" name="lab_mill_id" value="%mill_id%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_grade" name="lab_grade" value="%grade%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_mill" name="lab_mill" value="%mill%" readonly></td>' +
                '<td><input type="text" id="comment" name="comment"></td>' +
                '<td><input type="text" id="mat_type" name="mat_type" value = "%mat_type%"></td>' +
                '<td><input type = "button" class="btn btn-default" value="Print" onclick="print_label_big()"></td>';
                //+ '<td><input type = "button" class="btn btn-default" value="Export" id="export_to_excel" onclick="export_to_xls(event, this)"></td></tr>';

    // If customer is TSDPL; 2nd customer field has to be added
    var customer = document.getElementById("customer").value;
    customer = cust_name_for_label(customer);
    if (customer == "TSDPL"){
        html = '<tr id= %id%><td><input type="text" style="width:130px;border: 0px none;" id="lab_smpl_no" name="lab_smpl_no" value="%smpl_no%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_prod_date" name="lab_prod_date" value="%prod_date%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_customer" name="lab_customer" value="%customer%"></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_machine" name="lab_machine" value="%machine%" readonly></td>' +
                '<td><input type="text" style="border: 0px none;" id="lab_size" name="lab_size" value="%size%"></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_numbers" name="lab_numbers" value="%numbers%" ></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_packet_no" name="lab_packet_no" value="%packet_no%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_lamination" name="lab_lamination" value="%lamination%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_mill_id" name="lab_mill_id" value="%mill_id%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_grade" name="lab_grade" value="%grade%" readonly></td>' +
                '<td><input type="text" style="width:130px;border: 0px none;" id="lab_mill" name="lab_mill" value="%mill%" readonly></td>' +
                '<td><input type="text" id="comment" name="comment"></td>' +
                '<td><input type="text" id="cusomter2" name="customer2"></td>' +
                '<td><input type="text" id="mat_type" name="mat_type" value = "%mat_type%"></td>' +
                '<td><input type = "button" class="btn btn-default" value="Print" onclick="print_label_big()"></td></tr>';
    }
    var thickness = document.getElementById("thickness").value;
    var mill_id = document.getElementById("mill_id").value;
    var grade_field = document.getElementById("grade").value;
    var smpl_no = document.getElementById("smpl_no").value;
    var mill_name = document.getElementById("mill").value;
    mill_name = mill_name.split(' ');

    var mill, material_type, mat_type;
    if(mill_name[0] == ''){
        mill = "MILL"
    }else{
        mill = mill_name[0];
    }
    if(mill_id == ''){
     mill_id = 'N/A';
    }
    if(grade = ''){
        grade = 'N/A';
    }

    mat_type = grade_field.split("ID");
    mat_type = mat_type[0].split("GRADE");
    material_type = mat_type[0];
    material_type = material_type.replaceAll('COIL','');
    material_type = material_type.replaceAll('SHEETS','');
    material_type = material_type.replaceAll('.','');

    var machine = document.getElementById("machine").value;

    //var customer2 = document.getElementById("customer2").value;

    var prod_date_check = document.getElementById("processing_date");
    var prod_date = document.getElementById("processing_date").value;
    prod_date = change_date_format(prod_date);
    if (grade_field.includes("GRADE")){
        grade = grade_field.split("GRADE").pop();
        grade = grade.slice(1);
    }
    else{
        grade = grade_field;
    }


    width = numbers_table.rows[rowId].cells[0].lastChild.value;
    output_length = numbers_table.rows[rowId].cells[1].lastChild.value;
    var lami_check = numbers_table.rows[rowId];
    lamination = numbers_table.rows[rowId].cells[2].lastElementChild.selectedOptions[0].innerHTML;
    packet_name = numbers_table.rows[rowId].cells[3].lastChild.value;
    packet_nos = numbers_table.rows[rowId].cells[4].lastChild.value;


    if(lamination == "No Lamination"){
        lami_type = " ";
    }else{
        lamination = lamination.split('-');
        lami_type = lamination[0].toUpperCase() + "LAMINATION";
    }

    newHTML = html.replace('%numbers%', packet_nos);
    newHTML = newHTML.replace('%grade%', grade);
    newHTML = newHTML.replace('%smpl_no%', smpl_no);
    newHTML = newHTML.replace('%customer%', customer);
    newHTML = newHTML.replace('%machine%', machine);
    newHTML = newHTML.replace('%mill_id%', mill_id);
    newHTML = newHTML.replace('%prod_date%', prod_date);
    newHTML = newHTML.replace('%mill%', mill);
    newHTML = newHTML.replace('%mat_type%', material_type);

    size = thickness + " X " + width + " X " + output_length;
    newHTML = newHTML.replace('%size%', size);
    newHTML = newHTML.replace('%packet_no%', packet_name);
    newHTML = newHTML.replace('%lamination%', lami_type);

    //var fg_table =
    id = document.getElementById('fg_table').rows.length;
    newHTML = newHTML.replace('%id%', id);


    document.getElementById('fg_table').insertAdjacentHTML('beforeend', newHTML);


    /*for(j=1;j<width_table.rows.length;j++){
        width = width_table.rows[j].cells[0].lastChild.value;
        width_name = width_table.rows[j].cells[1].lastChild.value;

        width_part_name = width_name + part_name;
        newNEWHTML = newHTML.replace('%coil_name%', width_part_name);

        newNEWHTML = newNEWHTML.replace('%coil_name%', width_part_name);
        newNEWHTML = newNEWHTML.replace('%id%', id);
        document.getElementById('fg_table').insertAdjacentHTML('beforeend', newNEWHTML);
        id = id +1;
    }*/


}

/*function export_to_xls(e, th){
    e.preventDefault();
    var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var row_id = th.parentNode.id;
    var export_row = "";
    var fg_table = document.getElementById('fg_table');

    for(i=0;i<fg_table.rows[rowId].cells.length-2;i++){
            export_row += fg_table.rows[rowId].cells[i].lastChild.value + ';';
    }

    // This is an AJAX request to asynchronously send a request to Python
    // This helps us send a request but remain on the same page
    // https://stackoverflow.com/questions/41323679/how-to-send-data-to-flask-via-ajax
    $.ajax({
        url: '/background_process_test',
        type: 'POST',
        data: {
                 'new_freq': export_row  //  to the GET parameters
                },
        success: function (response) {
            alert(response);
        }
        });
}*/

function honda_part_no(width,length){
    var part_no = "";
    var coating = "";
    var wt_per_sheet = "";

            if (width == 720 && length == 745){
            part_no = "KONA PLATE BOTTOM";
            wt_per_sheet = 3.37;
            coating = "20/0";
        }
    else if (width == 600 && length == 820){
                part_no = "KONA OUTER R/L";
                wt_per_sheet = 3.09;
                coating = "0/20";
            }
    else if (width == 370 && length == 415){
                part_no = "K0LA+K0PA+K0YA, Tank Upper";
                wt_per_sheet = 0.97;
                coating = "0/20";
            }
    else if (width == 430 && length == 455){
                part_no = "K0LA+K0PA+K0YA, Tank Lower";
                wt_per_sheet = 1.23;
                coating = "0/20";
            }
    else if (width == 570 && length == 830){
                part_no = "K1KA R/L";
                wt_per_sheet = 2.97;
                coating = "0/20";
            }
    else if (width == 600 && length == 715){
                part_no = "K1KA PLATE BOTTOM";
                wt_per_sheet = 2.69;
                coating = "20/0";
            }
    else if (width == 550 && length == 790){
                part_no = "K1CA TANK R/L";
                wt_per_sheet = 2.73;
                coating = "0/20";
            }
    else if (width == 590 && length == 705){
                part_no = "K1CA TANK BOTTOM";
                wt_per_sheet = 2.61;
                coating = "20/0";
            }
    else if (width == 530 && length == 765){
                part_no = "K67 OUTER R/L";
                wt_per_sheet = 2.55;
                coating = "0/20";
            }
    else if (width == 575 && length == 640){
                part_no = "K67 PLATE BOTTOM";
                wt_per_sheet = 2.31;
                coating = "20/0";
            }
    else if (width == 510 && length == 785){
                part_no = "K0VA OUTER R/L";
                wt_per_sheet = 2.50;
                coating = "0/20";
            }
    else if (width == 600 && length == 660){
                part_no = "K0VA PLATE BOTTOM";
                wt_per_sheet = 2.29;
                coating = "20/0";
            }
    else if (width == 655 && length == 740){
                part_no = "K3CA UPPER";
                wt_per_sheet = 2.66;
                coating = "0/30";
            }
    else if (width == 565 && length == 645){
                part_no = "K3CA BTM";
                wt_per_sheet = 2.29;
                coating = "0/20";
    }
    else if (width == 520 && length == 765){
                part_no = "KTE TANK R/L";
                wt_per_sheet = 2.50;
                coating = "0/20";
            }
    else if (width == 565 && length == 645){
                part_no = "KTE TANK BOTTOM";
                wt_per_sheet = 2.29;
                coating = "20/0";
            }
    else if (width == 515 && length == 715){
                part_no = "K1EA TANK R/L";
                wt_per_sheet = 2.31;
                coating = "0/20";
            }
    else if (width == 620 && length == 675){
                part_no = "K1EA TANK BOTTOM";
                wt_per_sheet = 2.63;
                coating = "20/0";
            }

    else{
        part_no = "";
        wt_per_sheet = 0;
        coating = "";
    }
    return (part_no + ";" + wt_per_sheet + ";" +coating);
    //return part_no;
}

//Fill label details new version. This will allow for all formats and sizes
function make_label_new(th){

    qc_name = document.getElementById("names_of_qc").value;
    if(!qc_name){
        window.alert("QC Name is not entered.");
        return; // Exit the function
    }
    var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var row_id = th.parentNode.id;
    var operation = document.getElementById("operation").value;
    var numbers_table = document.getElementById('numbers_pkts');

    // First step is to clear all old values in the Label table
    var label_table = document.getElementById('label_table');

    //if (label_table.style.display =='table-row') {
        //label_table.style.display = 'none';
        var inputs = label_table.getElementsByTagName('input');
        for (i = 0; i < inputs.length; i++) {
            inputs[i].value = "";
        }
    //}

    /*else {
        label_table.style.display = 'table-row';
    }*/

    // Get values for the fields one by one
    //Row 1
    var smpl_no = document.getElementById("smpl_no").value;
    var prod_date = document.getElementById("processing_date").value;
    prod_date = change_date_format(prod_date);
    var machine = document.getElementById("machine").value;
    var width = numbers_table.rows[rowId].cells[0].lastChild.value;
    var output_length = numbers_table.rows[rowId].cells[1].lastChild.value;
    if(operation.includes('Trap')){
        output_length = numbers_table.rows[rowId].cells[1].lastChild.value + ' - ' + numbers_table.rows[rowId].cells[2].lastChild.value;
    }

    var thickness = document.getElementById("thickness").value;
    var size = thickness + " X " + width + " X " + output_length;




    //Row 2
    var customer = document.getElementById("customer").value;
    customer = cust_name_for_label(customer);
    var mill_name = document.getElementById("mill").value;
    mill_name = mill_name.split(' ');
    var mill;
    if(mill_name[0] == ''){
        mill = "MILL"
    }else{
        mill = mill_name[0];
    }
    if(mill_id == ''){
     mill_id = 'N/A';
    }
    var mill_id = document.getElementById("mill_id").value;

    //Row 3
    var lamination = numbers_table.rows[rowId].cells[2].lastElementChild.selectedOptions[0].innerHTML;
    var packet_name = numbers_table.rows[rowId].cells[3].lastChild.value;
    var packet_nos = numbers_table.rows[rowId].cells[4].lastChild.value;
    if (customer.startsWith("HONDA") || customer.startsWith("TTSSI")){
        var honda_part_num = honda_part_no(Number(width), Number(output_length));
        honda_part_num = honda_part_num.split(';');
        document.getElementById('lbl_part_no').value = honda_part_num[0];
        if(honda_part_num[1] != 0){
            document.getElementById('lbl_net_wt').value = Math.round(Number(honda_part_num[1]) * Number(numbers_table.rows[rowId].cells[4].lastChild.value));
        }
        document.getElementById('lbl_coating').value = honda_part_num[2];
    }

    var lami_type;

    if(lamination == "No Lamination"){
        lami_type = " ";
    }else{
        lamination = lamination.split('-');
        lami_type = lamination[0].toUpperCase() + "LAMINATION";
    }

    //Row 4
    var grade_field = document.getElementById("grade").value;
    var grade_coating = "";
    //Grade. Check if grade exists
    /*if (grade_field.includes("GRADE")){
        grade = grade_field.split("GRADE").pop();
        grade_coating = grade.split(' ');
        grade=grade_coating[0];
        grade = grade.slice(1);
        grade = grade.replace('.','');

    }*/

    var material_type = '';
    var grade='';
    var coating='';
    var scams_no='';
    var incoming_date = (document.getElementById('incoming_date').value);
    incoming_date = incoming_date.split('/');
    var new_incoming_date = incoming_date[1] + '/' + incoming_date[0] + '/' + incoming_date[2];
    new_incoming_date = new Date(new_incoming_date);
    var check_date = new Date("04/25/2023");

    if (grade_field.length > 0){
         if(new_incoming_date < check_date){
            grade_field = grade_field.split(';');
            //Material Type
            /*var mat_type = grade_field.split("ID");

            mat_type = mat_type[0].split("GRADE");
            var material_type = mat_type[0];
            material_type = material_type.replaceAll('COIL','');
            material_type = material_type.replaceAll('SHEETS','');
            material_type = material_type.replaceAll('.','');*/
            material_type = grade_field[0].toUpperCase();
            material_type = material_type.replaceAll('COIL','');
            material_type = material_type.replaceAll('SHEETS','');
            material_type = material_type.replaceAll('.','');
            material_type = material_type.replaceAll('MAT TYPE:','');

            for(i=1;i<grade_field.length;i++){
                grade_field[i] = (grade_field[i].toUpperCase());
                if((grade_field[i].toUpperCase()).includes("GRADE")){
                    grade = grade_field[i].split("GRADE").pop();
                    grade = grade.replaceAll(':','');
                    grade = grade.trim();
                }
                if((grade_field[i].toUpperCase()).includes("COATING")){
                    coating = grade_field[i].split("COATING").pop();
                    coating = coating.replaceAll(':','');
                    coating = coating.trim();
                }

                if((grade_field[i].toUpperCase()).includes("SCAMS NO")){
                    scams_no = grade_field[i].split("SCAMS NO").pop();
                    scams_no = scams_no.replaceAll(':','');
                    scams_no = scams_no.trim();
                }
            }
        }
        else{
            material_type = document.getElementById('mat_type').value;

            material_type = material_type.replaceAll('COIL','');
            material_type = material_type.replaceAll('SHEETS','');
            material_type = material_type.replaceAll('.','');


            grade = document.getElementById('grade').value;
            scams_no = document.getElementById('scams_no').value;
            if(scams_no == 'None'){
                scams_no = '';
            }
            coating = document.getElementById('coating').value;
            if(coating == 'None'){
                coating = '';
            }
        }
    }
    else if(grade_field == ''){
        grade = 'N/A';
    }
    else{
        grade = grade_field;
    }

    //SCAMS No.
    /*var scams_no = "";
    var scams_no_field = grade_field.split('SCAMS NO');
    if(scams_no_field[1]){
        scams_no = scams_no_field[1].slice(1);
        scams_no = (scams_no.split(' '))[0];
        scams_no = scams_no.replace('.','');
    }*/
    var mat_status = numbers_table.rows[rowId].cells[6].lastElementChild.selectedOptions[0].innerHTML;


    // Populate the label_table with the values
    //Row 1
    document.getElementById('lbl_smpl_no').value = smpl_no;
    document.getElementById('lbl_prod_date').value = prod_date;
    document.getElementById('lbl_machine').value = machine;
    document.getElementById('lbl_size').value = size;

    //Row 2
    document.getElementById('lbl_customer').value = customer;
    //document.getElementById('lbl_prod_date').value = prod_date;
    document.getElementById('lbl_mill').value = mill;
    document.getElementById('lbl_mill_id').value = mill_id;

    //Row 3
    document.getElementById('lbl_numbers').value = packet_nos;
    document.getElementById('lbl_packet_name').value = packet_name;
    document.getElementById('lbl_lamination').value = lamination;
    //document.getElementById('lbl_size').value = size;

    //Row 4
    document.getElementById('lbl_grade').value = grade.trimEnd();
    document.getElementById('lbl_mat_type').value = material_type.trimEnd();
    document.getElementById('lbl_scams_no').value = scams_no.trimEnd();
    //document.getElementById('lbl_size').value = size;

    //If customer is TTSS grade, material type to be made read only
    var customer = document.getElementById("customer").value;
    if (customer.startsWith("TT STEEL SERVICE INDIA"))
    {
        document.getElementById('lbl_grade').readOnly = true;
        document.getElementById('lbl_mat_type').readOnly = true;
        //document.getElementById('lbl_scams_no').readOnly = true;
    }

    var tsl_no;
    //Row 5
    if(document.getElementById('lbl_customer').value == "TATA STEEL"){
        tsl_no = document.getElementById('lbl_smpl_no').value.slice(3);
        document.getElementById('lbl_batch_no').value = tsl_no + 'P';
    }
    document.getElementById('lbl_mat_status').value = mat_status;
    document.getElementById('lbl_qc_name').value = qc_name;



}


//Fill label details new version. This will allow for all formats and sizes
function make_label_trap_new(th){

    qc_name = document.getElementById("names_of_qc").value;
    if(!qc_name){
        window.alert("QC Name is not entered.");
        return; // Exit the function
    }

    var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var row_id = th.parentNode.id;
    var operation = document.getElementById("operation").value;
    var numbers_table = document.getElementById('numbers_pkts');

    // First step is to clear all old values in the Label table
    var label_table = document.getElementById('label_table');

    //if (label_table.style.display =='table-row') {
        //label_table.style.display = 'none';
        var inputs = label_table.getElementsByTagName('input');
        for (i = 0; i < inputs.length; i++) {
            inputs[i].value = "";
        }
    //}

    /*else {
        label_table.style.display = 'table-row';
    }*/

    // Get values for the fields one by one
    //Row 1
    var smpl_no = document.getElementById("smpl_no").value;
    var prod_date = document.getElementById("processing_date").value;
    prod_date = change_date_format(prod_date);
    var machine = document.getElementById("machine").value;
    var width = numbers_table.rows[rowId].cells[0].lastChild.value;
    var output_length = numbers_table.rows[rowId].cells[1].lastChild.value;
    if(operation.includes('Trap')){
        output_length = numbers_table.rows[rowId].cells[1].lastChild.value + ' - ' + numbers_table.rows[rowId].cells[2].lastChild.value;
    }

    var thickness = document.getElementById("thickness").value;
    var size = thickness + " X " + width + " X " + output_length;




    //Row 2
    var customer = document.getElementById("customer").value;
    customer = cust_name_for_label(customer);
    var mill_name = document.getElementById("mill").value;
    mill_name = mill_name.split(' ');
    var mill;
    if(mill_name[0] == ''){
        mill = "MILL"
    }else{
        mill = mill_name[0];
    }
    if(mill_id == ''){
     mill_id = 'N/A';
    }
    var mill_id = document.getElementById("mill_id").value;

    //Row 3
    var lamination = numbers_table.rows[rowId].cells[3].lastElementChild.selectedOptions[0].innerHTML;
    var packet_name = numbers_table.rows[rowId].cells[4].lastChild.value;
    var packet_nos = numbers_table.rows[rowId].cells[5].lastChild.value;
    if (customer.startsWith("HONDA") || customer.startsWith("TTSSI")){
        var honda_part_num = honda_part_no(Number(width), Number(output_length));
        honda_part_num = honda_part_num.split(';');
        document.getElementById('lbl_part_no').value = honda_part_num[0];
        if(honda_part_num[1] != 0){
            document.getElementById('lbl_net_wt').value = Math.round(Number(honda_part_num[1]) * Number(numbers_table.rows[rowId].cells[4].lastChild.value));
        }
        document.getElementById('lbl_coating').value = honda_part_num[2];
    }

    var lami_type;

    if(lamination == "No Lamination"){
        lami_type = " ";
    }else{
        lamination = lamination.split('-');
        lami_type = lamination[0].toUpperCase() + "LAMINATION";
    }

    //Row 4
    var grade_field = document.getElementById("grade").value;
    var grade_coating = "";
    //Grade. Check if grade exists
    /*if (grade_field.includes("GRADE")){
        grade = grade_field.split("GRADE").pop();
        grade_coating = grade.split(' ');
        grade=grade_coating[0];
        grade = grade.slice(1);
        grade = grade.replace('.','');

    }*/

    var material_type = '';
    var grade='';
    var coating='';
    var scams_no='';
    var incoming_date = (document.getElementById('incoming_date').value);
    incoming_date = incoming_date.split('/');
    var new_incoming_date = incoming_date[1] + '/' + incoming_date[0] + '/' + incoming_date[2];
    new_incoming_date = new Date(new_incoming_date);
    var check_date = new Date("04/25/2023");

    if (grade_field.length > 0){
         if(new_incoming_date < check_date){
            grade_field = grade_field.split(';');
            //Material Type
            /*var mat_type = grade_field.split("ID");

            mat_type = mat_type[0].split("GRADE");
            var material_type = mat_type[0];
            material_type = material_type.replaceAll('COIL','');
            material_type = material_type.replaceAll('SHEETS','');
            material_type = material_type.replaceAll('.','');*/
            material_type = grade_field[0].toUpperCase();
            material_type = material_type.replaceAll('COIL','');
            material_type = material_type.replaceAll('SHEETS','');
            material_type = material_type.replaceAll('.','');
            material_type = material_type.replaceAll('MAT TYPE:','');

            for(i=1;i<grade_field.length;i++){
                grade_field[i] = (grade_field[i].toUpperCase());
                if((grade_field[i].toUpperCase()).includes("GRADE")){
                    grade = grade_field[i].split("GRADE").pop();
                    grade = grade.replaceAll(':','');
                    grade = grade.trim();
                }
                if((grade_field[i].toUpperCase()).includes("COATING")){
                    coating = grade_field[i].split("COATING").pop();
                    coating = coating.replaceAll(':','');
                    coating = coating.trim();
                }

                if((grade_field[i].toUpperCase()).includes("SCAMS NO")){
                    scams_no = grade_field[i].split("SCAMS NO").pop();
                    scams_no = scams_no.replaceAll(':','');
                    scams_no = scams_no.trim();
                }
            }
        }
        else{
            material_type = document.getElementById('mat_type').value;

            material_type = material_type.replaceAll('COIL','');
            material_type = material_type.replaceAll('SHEETS','');
            material_type = material_type.replaceAll('.','');


            grade = document.getElementById('grade').value;
            scams_no = document.getElementById('scams_no').value;
            if(scams_no == 'None'){
                scams_no = '';
            }
            coating = document.getElementById('coating').value;
            if(coating == 'None'){
                coating = '';
            }
        }
    }
    else if(grade_field == ''){
        grade = 'N/A';
    }
    else{
        grade = grade_field;
    }

    //SCAMS No.
    /*var scams_no = "";
    var scams_no_field = grade_field.split('SCAMS NO');
    if(scams_no_field[1]){
        scams_no = scams_no_field[1].slice(1);
        scams_no = (scams_no.split(' '))[0];
        scams_no = scams_no.replace('.','');
    }*/
    var mat_status = numbers_table.rows[rowId].cells[7].lastElementChild.selectedOptions[0].innerHTML;


    // Populate the label_table with the values
    //Row 1
    document.getElementById('lbl_smpl_no').value = smpl_no;
    document.getElementById('lbl_prod_date').value = prod_date;
    document.getElementById('lbl_machine').value = machine;
    document.getElementById('lbl_size').value = size;

    //Row 2
    document.getElementById('lbl_customer').value = customer;
    //document.getElementById('lbl_prod_date').value = prod_date;
    document.getElementById('lbl_mill').value = mill;
    document.getElementById('lbl_mill_id').value = mill_id;

    //Row 3
    document.getElementById('lbl_numbers').value = packet_nos;
    document.getElementById('lbl_packet_name').value = packet_name;
    document.getElementById('lbl_lamination').value = lamination;
    //document.getElementById('lbl_size').value = size;

    //Row 4
    document.getElementById('lbl_grade').value = grade.trimEnd();
    document.getElementById('lbl_mat_type').value = material_type.trimEnd();
    document.getElementById('lbl_scams_no').value = scams_no.trimEnd();
    //document.getElementById('lbl_size').value = size;

    //If customer is TTSS grade, material type to be made read only
    var customer = document.getElementById("customer").value;
    if (customer.startsWith("TT STEEL SERVICE INDIA"))
    {
        document.getElementById('lbl_grade').readOnly = true;
        //document.getElementById('lbl_mat_type').readOnly = true;
        //document.getElementById('lbl_scams_no').readOnly = true;
    }

    var tsl_no;
    //Row 5
    if(document.getElementById('lbl_customer').value == "TATA STEEL"){
        tsl_no = document.getElementById('lbl_smpl_no').value.slice(3);
        document.getElementById('lbl_batch_no').value = tsl_no + 'P';
    }
    document.getElementById('lbl_mat_status').value = mat_status;
    document.getElementById('lbl_qc_name').value = qc_name;

}


////Fill label table for Reshearing
function make__part_label_reshearing(th){
    var rowId = parseInt(event.target.parentNode.parentNode.id);
              //this gives id of tr whose button was clicked
    var row_id = th.parentNode.id;

    var numbers_table = document.getElementById('numbers_pkts');
    //var parts_table = document.getElementById('part_tbl');
    var newHTML = '';
    var newNEWHTML = '';
    var id =1;
    var packet_nos,packet_name, output_length, width, width_part_name, size, prod_date, lamination, lami_type, grade;
    var html = '<tr id= %id%><td>%smpl_no%</td><td>%prod_date%</td><td>%customer%</td><td>%machine%</td><td>%size%</td><td>%numbers%</td><td>%packet_no%</td><td>%mill_id%</td><td>%grade%</td><td>%mill%</td><td><input type="text" id="comment" name="comment"></td><td><input type="text" id="mat_type" name="mat_type" value = "%mat_type%"></td><td><input type = "button" class="btn btn-default" value="Print" onclick="print_label_reshearing()"></td></tr>';

    // If customer is TSDPL; 2nd customer field has to be added
    var customer = document.getElementById("customer").value;
    customer = cust_name_for_label(customer);
    if (customer == "TSDPL"){
        html = '<tr id= %id%><td>%smpl_no%</td><td>%prod_date%</td><td>%customer%</td><td>%machine%</td><td>%size%</td><td>%numbers%</td><td>%packet_no%</td><td>%mill_id%</td><td>%grade%</td><td>%mill%</td><td><input type="text" id="comment" name="comment"></td><td><input type="text" id="cusomter2" name="customer2"></td><td><input type="text" id="mat_type" name="mat_type" value = "%mat_type%"></td><td><input type = "button" class="btn btn-default" value="Print" onclick="print_label_reshearing()"></td></tr>';
    }
    var thickness = document.getElementById("thickness").value;
    var mill_id = document.getElementById("mill_id").value;
    var grade_field = document.getElementById("grade").value;
    var smpl_no = document.getElementById("smpl_no").value;
    var mill_name = document.getElementById("mill").value;
    mill_name = mill_name.split(' ');

    var mill, material_type;
    if(mill_name[0] == ''){
        mill = "MILL"
    }else{
        mill = mill_name[0];
    }
    if(mill_id == ''){
     mill_id = 'N/A';
    }

    mat_type = grade_field.split("ID");

    mat_type = mat_type[0].split("GRADE");
    material_type = mat_type[0];
    material_type = material_type.replaceAll('COIL','');
    material_type = material_type.replaceAll('SHEETS','');
    material_type = material_type.replaceAll('.','');

    var machine = document.getElementById("machine").value;

    //var customer2 = document.getElementById("customer2").value;

    var prod_date_check = document.getElementById("processing_date");
    var prod_date = document.getElementById("processing_date").value;
    prod_date = change_date_format(prod_date);
    if (grade_field.includes("GRADE")){
        grade = grade_field.split("GRADE").pop();
        grade = grade.slice(1);
    }
    else if(grade_field == ''){
        grade = 'N/A';
    }
    else{
        grade = grade_field;
    }


    width = numbers_table.rows[rowId].cells[0].lastChild.value;
    output_length = numbers_table.rows[rowId].cells[1].lastChild.value;
    var lami_check = numbers_table.rows[rowId];
    lamination = numbers_table.rows[rowId].cells[2].lastElementChild.selectedOptions[0].innerHTML;
    packet_name = numbers_table.rows[rowId].cells[3].lastChild.value;
    packet_nos = numbers_table.rows[rowId].cells[4].lastChild.value;


    if(lamination == "No Lamination"){
        lami_type = " ";
    }else{
        lamination = lamination.split('-');
        lami_type = lamination[0].toUpperCase() + "LAMINATION";
    }

    newHTML = html.replace('%numbers%', packet_nos);
    newHTML = newHTML.replace('%grade%', grade);
    newHTML = newHTML.replace('%smpl_no%', smpl_no);
    newHTML = newHTML.replace('%customer%', customer);
    newHTML = newHTML.replace('%machine%', machine);
    newHTML = newHTML.replace('%mill_id%', mill_id);
    newHTML = newHTML.replace('%prod_date%', prod_date);
    newHTML = newHTML.replace('%mill%', mill);
    newHTML = newHTML.replace('%mat_type%', material_type);

    size = thickness + " X " + width + " X " + output_length;
    newHTML = newHTML.replace('%size%', size);
    newHTML = newHTML.replace('%packet_no%', packet_name);
    newHTML = newHTML.replace('%lamination%', lami_type);

    //var fg_table =
    id = document.getElementById('fg_table').rows.length;
    newHTML = newHTML.replace('%id%', id);


    document.getElementById('fg_table').insertAdjacentHTML('beforeend', newHTML);


    /*for(j=1;j<width_table.rows.length;j++){
        width = width_table.rows[j].cells[0].lastChild.value;
        width_name = width_table.rows[j].cells[1].lastChild.value;

        width_part_name = width_name + part_name;
        newNEWHTML = newHTML.replace('%coil_name%', width_part_name);

        newNEWHTML = newNEWHTML.replace('%coil_name%', width_part_name);
        newNEWHTML = newNEWHTML.replace('%id%', id);
        document.getElementById('fg_table').insertAdjacentHTML('beforeend', newNEWHTML);
        id = id +1;
    }*/


}

// This function is to get the details for the sticker ready from the page
function make_label_slit(){
    var width_table = document.getElementById('numbers_pkts1');
    var parts_table = document.getElementById('part_tbl');
    var newHTML = '';
    var newNEWHTML = '';
    var id =1;
    var part_length,part_name, width, width_name, width_part_name, size, prod_date;
    var html = '<tr id= %id%><td>%smpl_no%</td><td>%prod_date%</td><td>%customer%</td><td>%machine%</td><td>%size%</td><td>%coil_length%</td><td>%coil_name%</td><td>%mill_id%</td><td>%grade%</td><td>%mill%</td><td><input type="text" id="comment" name="comment"></td><td><input type = "button" class="btn btn-default" value="Print" onclick="print_label()"></td></tr>'

    // If customer is TSDPL; 2nd customer field has to be added
    var customer = document.getElementById("customer").value;
    customer = cust_name_for_label(customer);
    if (customer == "TSDPL"){
        html = '<tr id= %id%><td>%smpl_no%</td><td>%prod_date%</td><td>%customer%</td><td>%machine%</td><td>%size%</td><td>%coil_length%</td><td>%coil_name%</td><td>%mill_id%</td><td>%grade%</td><td>%mill%</td><td><input type="text" id="comment" name="comment"></td><td><input type="text" id="customer2nd" name="customer2nd"></td><td><input type = "button" class="btn btn-default" value="Print" onclick="print_label()"></td></tr>'
    }
    var thickness = document.getElementById("thickness").value;
    var mill_id = document.getElementById("mill_id").value;
    var grade_field = document.getElementById("grade").value;
    var smpl_no = document.getElementById("smpl_no").value;
    var mill_name = document.getElementById("mill").value;
    mill_name = mill_name.split(' ');
    var mill = mill_name[0];


    //var customer2 = document.getElementById("customer2").value;

    var prod_date = document.getElementById("processing_date").value;
    prod_date = change_date_format(prod_date);
    if (grade_field.includes("GRADE")){
        grade = grade_field.split("GRADE").pop();
        grade = grade.slice(1);
    }
    else{
        grade = grade_field;
    }

    for(i=1;i<parts_table.rows.length;i++){
        part_length = parts_table.rows[i].cells[0].lastChild.value;
        part_name = parts_table.rows[i].cells[1].lastChild.value;
        newHTML = html.replace('%coil_length%', part_length);
        newHTML = newHTML.replace('%grade%', grade);
        newHTML = newHTML.replace('%smpl_no%', smpl_no);
        newHTML = newHTML.replace('%customer%', customer);
        newHTML = newHTML.replace('%machine%', "Slitting");
        newHTML = newHTML.replace('%mill_id%', mill_id);
        newHTML = newHTML.replace('%prod_date%', prod_date);

        for(j=1;j<width_table.rows.length;j++){
            width = width_table.rows[j].cells[0].lastChild.value;
            width_name = width_table.rows[j].cells[1].lastChild.value;
            size = thickness + " x " + width + " x Coil";
            width_part_name = width_name + part_name;
            newNEWHTML = newHTML.replace('%coil_name%', width_part_name);
            newNEWHTML = newNEWHTML.replace('%size%', size);
            newNEWHTML = newNEWHTML.replace('%coil_name%', width_part_name);
            newNEWHTML = newNEWHTML.replace('%id%', id);
            document.getElementById('fg_table').insertAdjacentHTML('beforeend', newNEWHTML);
            id = id +1;
        }

    }

}

function setting_done_change(){
    var setting_done_yes = document.getElementById("setting_done_yes").checked;
    var setting_done_no = document.getElementById("setting_done_no").checked;

    console.log(setting_done_yes);
    console.log(setting_done_no);

    if(setting_done_yes == true){
        document.getElementById("setting_date").value = "";
        document.getElementById("setting_date").readOnly = false;
        document.getElementById("setting_start_time").value = "";
        document.getElementById("setting_start_time").readOnly = false;
        document.getElementById("setting_end_time").value = "";
        document.getElementById("setting_end_time").readOnly = false;
        document.getElementById("setting_time").value = "";

    }
    if(setting_done_no == true){
        document.getElementById("setting_date").value = "2001-01-01";
        document.getElementById("setting_date").readOnly = true;
        document.getElementById("setting_start_time").value = "00:00";
        document.getElementById("setting_start_time").readOnly = true;
        document.getElementById("setting_end_time").value = "00:00";
        document.getElementById("setting_end_time").readOnly = true;
        document.getElementById("setting_time").value = "0";

    }

}

function check_slitter_numbers(tableID){
    var table = document.getElementById(tableID);
    var i, slitter_lst, slitter_lst_array, row, flag;
    var rowCount = table.rows.length;
    flag = 0;

    for (i=1; i< rowCount; i++){
        row = table.rows[i];
        slitter_lst = row.cells[1].lastElementChild.value;
        slitter_lst_array = slitter_lst.split(' ');
        for(j=0;j<slitter_lst_array.length;j++){
            if(Number(slitter_lst_array[j]) > 50){
                alert('Please check slitter numbers');
                //document.getElementById('slitter_number').focus();
                flag = 1;
            }
        }
    }
    if(flag == 1){ return false;}
    else {return true;}
}

function validateForm(){
// 1. If slitting check if all slitter numbers < 50
// 2. Processed weight cannot be empty


// First step check for all the nulls and empty fields

    var total_processed_wt = document.getElementById('total_processed_wt').value;
    if (total_processed_wt == ""){
        alert('Processed weight is empty. Please check!');
        return false;
    }
    var check_slitters = check_slitter_numbers('slitting_cutters');
    if(check_slitters == false){
        return false;
    }

}

