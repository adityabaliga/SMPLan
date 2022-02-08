//Disable Submit button once submit is pressed
window.addEventListener('beforeunload', function (e) {
  document.getElementById("submit").disabled = true;
});


function full_dispatch(th, tableID)
{
    var table = document.getElementById(tableID);

    var rowCount = th.parentNode.parentNode.rowIndex;

	var last_row = document.getElementById(tableID).rows[rowCount];

    var full_disp = last_row.cells[7].lastElementChild.checked;

    if (full_disp == true)
    {
        last_row.cells[8].lastElementChild.value = last_row.cells[3].lastElementChild.value;
        last_row.cells[9].lastElementChild.value = last_row.cells[4].lastElementChild.value;

    }
    else
    {
        last_row.cells[8].lastElementChild.value = '';
        last_row.cells[9].lastElementChild.value = '';
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
        last_row.cells[7].lastChild.disabled = false;
        last_row.cells[8].lastChild.readOnly = false;
        last_row.cells[9].lastChild.readOnly = false;
        last_row.cells[10].lastChild.readOnly = false;
        last_row.cells[11].lastChild.readOnly = false;

        last_row.cells[8].lastChild.required = true;
        last_row.cells[9].lastChild.required = true;
        last_row.cells[10].lastChild.required = true;
        last_row.cells[11].lastChild.value = ' ';
	}
	else
	{
	    last_row.cells[7].lastChild.disabled = true;
	    last_row.cells[7].lastChild.checked = false;
	    last_row.cells[8].lastChild.readOnly = true;
	    last_row.cells[8].lastChild.value = '';
        last_row.cells[9].lastChild.readOnly = true;
        last_row.cells[9].lastChild.value = '';
        total_dispatch_wt(tableID);
        last_row.cells[10].lastChild.readOnly = true;
        last_row.cells[11].lastChild.readOnly = true;

	}
}

function check_numbers(th, tableID)
{
    var table = document.getElementById(tableID);

    var rowCount = th.parentNode.parentNode.rowIndex;

	var last_row = document.getElementById(tableID).rows[rowCount];



    numbers = parseInt(last_row.cells[3].lastElementChild.value);
    dispatch_nos = parseInt(last_row.cells[8].lastElementChild.value);

    if(dispatch_nos > numbers)
    {
        alert('Dispatch numbers cannot be more than available numbers!');
        last_row.cells[3].lastElementChild.value = '';
    }
    else
    {
        qty = last_row.cells[4].lastElementChild.value;
        dispatch_qty = qty/numbers * dispatch_nos;
        last_row.cells[9].lastElementChild.value = dispatch_qty.toFixed(3);
        last_row.cells[9].lastElementChild.readOnly = true;
        total_dispatch_wt(tableID);
    }
 }

function total_dispatch_wt(tableID){
        var total_disp_wt, row;

        total_disp_wt = 0.0;
        var table = document.getElementById(tableID);

        var rowCount = table.rows.length;

        for(i=1;i<rowCount;i++){
            row = table.rows[i];
            total_disp_wt = total_disp_wt + Number(row.cells[9].lastElementChild.value);
        }

        document.getElementById("total_disp_wt").value = total_disp_wt.toFixed(3);
}