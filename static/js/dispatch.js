/*SMPL No.</th>
                <th>Packet Name</th>
                <th>Thickness</th>
                <th>Width x Length</th>
                <th>Numbers</th>
                <th>Weight (in MT)</th>
                <th>Grade</th>
                <th>Status</th>
                <th>Full Dispatch</th>
                <th>Dispatch Numbers</th>
                <th>Dispatch Qty (in MT)</th>
                <th>No. of packets</th>
                <th>Defective</th>
*/
var smpl_no_pos = 0;
var packet_name_pos = 1;
var thickness_pos = 2;
var size_pos = 3;
var numbers_pos = 4;
var weight_pos = 5;
var grade_pos = 6;
var status_pos=7;
var full_dispatch_pos = 8;
var dispatch_nos_pos = 9;
var dispatch_qty_pos = 10;
var no_of_pkts_pos = 11;
var defective_pos=12;


//Disable Submit button once submit is pressed
window.addEventListener('beforeunload', function (e) {
  document.getElementById("submit").disabled = true;
});

function checkbox_enable(){
    var dispatch_table = document.getElementById("dispatch_list");
    var dispatch_wt = document.getElementById("total_disp_wt").value;
    var qty, dispatch_qty, numbers;
    for(i=1;i<dispatch_table.rows.length;i++){
        dispatch_table.rows[i].cells[0].childNodes[0].checked = true;
        dispatch_table.rows[i].cells[defective_pos].lastChild.value = ' ';
        dispatch_table.rows[i].cells[defective_pos].lastChild.readOnly = false;

        qty = dispatch_table.rows[i].cells[weight_pos].lastElementChild.value;
        numbers = dispatch_table.rows[i].cells[numbers_pos].lastElementChild.value;
        dispatch_nos = dispatch_table.rows[i].cells[dispatch_nos_pos].lastElementChild.value;
        dispatch_qty = qty/numbers * dispatch_nos;
        dispatch_table.rows[i].cells[dispatch_qty_pos].lastElementChild.value = dispatch_qty.toFixed(3);
        dispatch_table.rows[i].cells[dispatch_qty_pos].lastElementChild.readOnly = true;
        //total_dispatch_wt(tableID);

    }
    total_dispatch_wt("dispatch_list");

}


function full_dispatch(th, tableID)
{
    var table = document.getElementById(tableID);

    var rowCount = th.parentNode.parentNode.rowIndex;

	var last_row = document.getElementById(tableID).rows[rowCount];

    var full_disp = last_row.cells[full_dispatch_pos].lastElementChild.checked;

    if (full_disp == true)
    {
        last_row.cells[dispatch_nos_pos].lastElementChild.value = last_row.cells[numbers_pos].lastElementChild.value;
        last_row.cells[dispatch_qty_pos].lastElementChild.value = last_row.cells[weight_pos].lastElementChild.value;

    }
    else
    {
        last_row.cells[dispatch_nos_pos].lastElementChild.value = '';
        last_row.cells[dispatch_qty_pos].lastElementChild.value = '';
    }
    total_dispatch_wt(tableID);
}

function enable_dispatch(th, tableID)
{
    var table = document.getElementById(tableID);

    var rowCount = th.parentNode.parentNode.rowIndex;

	var last_row = document.getElementById(tableID).rows[rowCount];

	var dispatch_on = last_row.cells[0].lastElementChild.checked;

	if(dispatch_on == true)
	{
        last_row.cells[full_dispatch_pos].lastChild.disabled = false;
        last_row.cells[dispatch_nos_pos].lastChild.readOnly = false;
        last_row.cells[dispatch_qty_pos].lastChild.readOnly = false;
        last_row.cells[no_of_pkts_pos].lastChild.readOnly = false;
        last_row.cells[defective_pos].lastChild.readOnly = false;

        last_row.cells[dispatch_nos_pos].lastChild.required = true;
        last_row.cells[dispatch_qty_pos].lastChild.required = true;
        last_row.cells[no_of_pkts_pos].lastChild.required = true;
        last_row.cells[defective_pos].lastChild.value = ' ';
	}
	else
	{
	    last_row.cells[full_dispatch_pos].lastChild.disabled = true;
	    last_row.cells[full_dispatch_pos].lastChild.checked = false;
	    last_row.cells[dispatch_nos_pos].lastChild.readOnly = true;
	    last_row.cells[dispatch_nos_pos].lastChild.value = '';
        last_row.cells[dispatch_qty_pos].lastChild.readOnly = true;
        last_row.cells[dispatch_qty_pos].lastChild.value = '';
        total_dispatch_wt(tableID);
        last_row.cells[no_of_pkts_pos].lastChild.readOnly = true;
        last_row.cells[defective_pos].lastChild.readOnly = true;

	}
}

function check_numbers(th, tableID)
{
    var table = document.getElementById(tableID);

    var rowCount = th.parentNode.parentNode.rowIndex;

	var last_row = document.getElementById(tableID).rows[rowCount];



    numbers = parseInt(last_row.cells[numbers_pos].lastElementChild.value);
    dispatch_nos = parseInt(last_row.cells[dispatch_nos_pos].lastElementChild.value);

    if(dispatch_nos > numbers)
    {
        alert('Dispatch numbers cannot be more than available numbers!');
        last_row.cells[numbers_pos].lastElementChild.value = '';
    }
    else
    {
        qty = last_row.cells[weight_pos].lastElementChild.value;
        dispatch_qty = qty/numbers * dispatch_nos;
        last_row.cells[dispatch_qty_pos].lastElementChild.value = dispatch_qty.toFixed(3);
        last_row.cells[dispatch_qty_pos].lastElementChild.readOnly = true;
        total_dispatch_wt(tableID);
    }
 }

function total_dispatch_wt(tableID){
        var total_disp_wt, row, total_packets;

        total_disp_wt = 0.0;
        total_packets = 0;
        var table = document.getElementById(tableID);

        var rowCount = table.rows.length;

        for(i=1;i<rowCount;i++){
            row = table.rows[i];
            total_disp_wt = total_disp_wt + Number(row.cells[dispatch_qty_pos].lastElementChild.value);
            total_packets = total_packets + Number(row.cells[no_of_pkts_pos].lastElementChild.value);
        }

        document.getElementById("total_disp_wt").value = total_disp_wt.toFixed(3);
        document.getElementById("total_packets").value = total_packets;
}