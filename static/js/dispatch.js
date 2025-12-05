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
var defective_pos=8;


//Disable Submit button once submit is pressed
/*window.addEventListener('beforeunload', function (e) {
  document.getElementById("submit").disabled = true;
});*/

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
        last_row.cells[no_of_pkts_pos].lastElementChild.value = '1';

    }
    else
    {
        last_row.cells[dispatch_nos_pos].lastElementChild.value = '';
        last_row.cells[dispatch_qty_pos].lastElementChild.value = '';
        last_row.cells[no_of_pkts_pos].lastElementChild.value = '';
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
        /*last_row.cells[full_dispatch_pos].lastChild.disabled = false;
        last_row.cells[dispatch_nos_pos].lastChild.readOnly = false;
        last_row.cells[dispatch_qty_pos].lastChild.readOnly = false;
        last_row.cells[no_of_pkts_pos].lastChild.readOnly = false;*/
        last_row.cells[defective_pos].lastChild.readOnly = false;

        /*last_row.cells[dispatch_nos_pos].lastChild.required = true;
        last_row.cells[dispatch_qty_pos].lastChild.required = true;
        last_row.cells[no_of_pkts_pos].lastChild.required = true;*/
        last_row.cells[defective_pos].lastChild.value = ' ';
        last_row.style.backgroundColor = "lightgreen";
	}
	else
	{
	    /*last_row.cells[full_dispatch_pos].lastChild.disabled = true;
	    last_row.cells[full_dispatch_pos].lastChild.checked = false;
	    last_row.cells[dispatch_nos_pos].lastChild.readOnly = true;
	    last_row.cells[dispatch_nos_pos].lastChild.value = '';
        last_row.cells[dispatch_qty_pos].lastChild.readOnly = true;
        last_row.cells[dispatch_qty_pos].lastChild.value = '';

        last_row.cells[no_of_pkts_pos].lastChild.readOnly = true;*/
        last_row.cells[defective_pos].lastChild.readOnly = true;
        last_row.style.backgroundColor = "transparent";

	}
	total_dispatch_wt(tableID);
}

function enable_transfer(th, tableID)
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

        last_row.cells[no_of_pkts_pos].lastChild.readOnly = true;
        last_row.cells[defective_pos].lastChild.readOnly = true;


	}
	total_dispatch_wt(tableID);
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

        var selected_rows = document.querySelectorAll('.select_smpl:checked')

        selected_rows.forEach(checkbox => {
                // Find the parent row
                const row = checkbox.closest('tr');

                // Find the weight cell in the same row
                const weightCell = row.querySelector('.dispatch_wt');

                // Parse the weight and add to total
                total_disp_wt += parseFloat(weightCell.value);
            });


        total_packets = document.querySelectorAll('.select_smpl:checked').length;


        document.getElementById("total_disp_wt").value = total_disp_wt.toFixed(3);
        document.getElementById("total_packets").value = total_packets;
}

function display_honda_pkts(){
    var selectedSize = document.getElementById('selected_size').value;
    var packets = document.querySelectorAll(".packet-list");

    packets.forEach(row => {
                const rowSize = row.getAttribute("data-size");
                if (selectedSize === "all" || rowSize === selectedSize) {
                    row.style.display = "table-row";
                } else {
                    row.style.display = "none";
                }
            });


}

function display_smpl_no(){
    var selectedSMPL = document.getElementById('selected_smpl_no').value;
    var packets = document.querySelectorAll(".packet-list");

    packets.forEach(row => {
                const rowSize = row.getAttribute("data-smpl_no");
                if (selectedSMPL === "all" || rowSize === selectedSMPL) {
                    row.style.display = "table-row";
                } else {
                    row.style.display = "none";
                }
            });


}

//This function adds the selected packets to the table below.
function addPackets(){
    const selectedTable = document.getElementById("dispatch_list_selected").getElementsByTagName("tbody")[0];
    const selectedItems = document.querySelectorAll(".select_packet:checked");
    let currentSerialNumber = selectedTable.getElementsByTagName("tr").length + 1;
    var total_disp_wt = parseFloat(document.getElementById("total_disp_wt").value);

    selectedItems.forEach(item => {
                const cs_id = item.getAttribute("data-csid");
                const smpl_no = item.getAttribute("data-smpl_no");
                const pkt_no = item.getAttribute("data-pkt_no");
                const size1 = item.getAttribute("data-size1");
                const numbers = item.getAttribute("data-numbers");
                const weight = item.getAttribute("data-weight");

                // Check if the item is already in the selected table to avoid duplicates
                if (!isDuplicate(cs_id)) {
                    const newRow = selectedTable.insertRow();

                    // Add Serial Number cell
                    const serialCell = newRow.insertCell(0);
                    serialCell.textContent = currentSerialNumber++;

                    newRow.insertCell(1).textContent = cs_id;
                    newRow.insertCell(2).textContent = smpl_no;

                    newRow.insertCell(3).textContent = pkt_no;
                    newRow.insertCell(4).textContent = size1;
                    newRow.insertCell(5).textContent = numbers;
                    newRow.insertCell(6).textContent = weight;

                    total_disp_wt += parseFloat(weight);
                }

                // Uncheck the item after adding
                item.checked = false;
            });
            document.getElementById("total_disp_wt").value = total_disp_wt.toFixed(3);

}

function isDuplicate(cs_id) {
            const selectedTable = document.getElementById("dispatch_list_selected").getElementsByTagName("tbody")[0];
            const rows = selectedTable.getElementsByTagName("tr");

            for (let i = 0; i < rows.length; i++) {
                const cells = rows[i].getElementsByTagName("td");
                if (cells[1].textContent === cs_id) {
                    return true;  // Duplicate found
                }
            }
            return false;  // No duplicate found
}

//This function generates a list of cs IDs to be passed on the python
function get_cs_id_list(){
         const selectedTable = document.getElementById("dispatch_list_selected").getElementsByTagName("tbody")[0];
         const rows = selectedTable.getElementsByTagName("tr");
         var cs_id_list = '';

        for (let i = 0; i < rows.length; i++) {
            const cells = rows[i].getElementsByTagName("td");
            cs_id_list += cells[1].textContent;
            cs_id_list += ',';
        }

        document.getElementById('cs_id_list').value = cs_id_list;


 }

//This function checks the size of the table loads details of the sizes from the json and populates the table
function get_size_details(){
    const table = document.getElementById('dispatch_list');
    const rows = table.getElementsByTagName("tbody")[0].getElementsByTagName("tr");


    for(let i=0;i<rows.length;i++){
        const cells = rows[i].getElementsByTagName("td");
        const size = cells[6].textContent + ' x ' + cells[7].textContent;

        cells[10].textContent = Number(cells[10].textContent) * 1000;

        // This part loads the json and populates the table based on the size
        fetch("/static/honda_sizes.json")
            .then(response => response.json())
            .then(data => {
                if(data[size]){
                    //cells[0].textContent = i+1;
                    cells[2].textContent = data[size].part_name;
                    cells[9].textContent = data[size].wt_per_sheet;
                    cells[10].textContent = (Number(data[size].wt_per_sheet) * Number(cells[8].textContent));
                    cells[10].textContent = Math.round(cells[10].textContent);


                    cells[13].textContent = data[size].coating;
                    cells[17].textContent = data[size].pallet;

                    //This function runs after addTotalRow, so this check is added to keep Gross Wt empty
                    // for merged packets

                    if(cells[0].textContent != ''){
                        cells[11].textContent = data[size].gross_wt;
                    }else{
                        cells[11].textContent = '';
                    }
                }
        });

    }
    addTotalRow();

}

//This function checks if size has changed in the table, if yes it will add a row and add the total for the size
function addTotalRow(){
    const table = document.getElementById('dispatch_list');
    const rows = table.getElementsByTagName("tbody")[0].getElementsByTagName("tr");
    const firstRow = rows[0].getElementsByTagName("td");
    let currentSize = firstRow[6].textContent + ' x ' + firstRow[7].textContent;
    var serialNumber = 0;
    let currentSizeTotal  = 0;
    var prevPktNumbers = 0;
    var currentWt = 0;
    var currentNos = 0;
    let currentNosTotal = 0;


    for(let i=0;i<rows.length;i++){
        var cells = rows[i].getElementsByTagName("td");
        const size = cells[6].textContent + ' x ' + cells[7].textContent;

        // This part is to add a row and total at the end of the size list
        if (size != currentSize){
             currentSizeTotal = Math.round(currentSizeTotal*1000)/1000;

             insertTotalRow(table, i+2, currentSizeTotal, currentNosTotal, cells.length)
             currentSizeTotal = 0;
             currentNosTotal = 0;

             serialNumber = -1;
             currentSize = size;

            prevPktNumbers = 0;
        }else{
         currentWt= Number(cells[10].textContent.trim());
         currentNos = Number(cells[8].textContent.trim());



        currentSizeTotal += currentWt;
        currentNosTotal += currentNos;

        }


        // This part is for merge packets, to skip serial number and gross wt for next row
        // if total of 2 consecutive rows = lotQty (300 or 450)
        var numbers = parseInt(cells[8].textContent);
        const lotQty = 300;


        //If K3CA then change lot quantity to 450
        if(firstRow[2].textContent.includes("K3CA")){
            lotQty = 450;
        }

        if(numbers < lotQty  && prevPktNumbers != 0){
            if ( i< rows.length -1){
                const nextRow = rows[i+1].getElementsByTagName("td");
                const nextPktNumbers = parseInt(nextRow[8].textContent);

                const nextSize = nextRow[6].textContent + ' x ' + nextRow[7].textContent;

                if (numbers + nextPktNumbers == lotQty){
                    nextRow[0].textContent = '';
                    nextRow[16].textContent = '';

                    serialNumber += 1;
                    cells[0].textContent = serialNumber;


                }else if(size != nextSize){
                    serialNumber += 1;
                    cells[0].textContent = serialNumber;
                }
            }
        }else{
                serialNumber += 1;
                cells[0].textContent = serialNumber;
            }
        prevPktNumbers = numbers;

        }
        // Insert total row after the last row, this is for the last size listed
        insertTotalRow(table, rows.length + 2, currentSizeTotal, currentNosTotal, cells.length)


}

function insertTotalRow(table, index, total_wt, total_nos,  no_of_cells){
    const newRow = table.insertRow(index);

    for (let i=0;i<no_of_cells; i++){
    const cell = newRow.insertCell(0);
    cell.textContent = "";
    }
    newRow.cells[10].textContent = (total_wt);
    newRow.cells[8].textContent = (total_nos);

}

function generateExcelHondaDispatch() {
  // Get the table element by its ID
   var table = document.getElementById('dispatch_list');

  var workbook = XLSX.utils.table_to_book(table, { sheet: 'Sheet1' });

  var dispatch_date = document.getElementById('dispatch_date').value;
  var veh_no = document.getElementById('vehicle_no').value;
  var customer = document.getElementById('customer').value;
  var customer_file_name = customer.split(' ');
  var file_name = customer_file_name[0] + '_' + dispatch_date + veh_no + '.xlsx';


    header = "DISPATCH LIST - " + dispatch_date + "  VEHICLE NO: " + veh_no + "   CUSTOMER: " + customer;

    var ws = workbook.Sheets[workbook.SheetNames[0]];

    // Define the new row to add at the top
    var newRow = [[header]]; // You can customize this as needed

    // Add the new row at the top (cell A1) of the existing sheet
    XLSX.utils.sheet_add_aoa(ws, newRow, { origin: 0 });

    ws['!cols'] = [
      { wch: 10 }, // Column A width (optional)
      { wch: 12 }, // Column B width = 12
      { wch: 10 }, // Column C width (optional)
      // Add more columns as needed
    ];



  XLSX.writeFile(workbook, file_name);



}

const userPins = {
            Manjappa: "2305",
            Kartik: "8751",
            Kiran: "9019",
            Govardhan: "7259",
            Jeevan: "5213",
            Chandu: "1999",
            Aditya: "0509",
            Chandrashekar: "7973"
};

 function validatePin(event) {
            const selectedUser = document.getElementById("entry_by").value;
            const enteredPin = document.getElementById("pinInput").value;
            const errorMessage = document.getElementById("errorMessage");
            const successMessage = document.getElementById("successMessage");

            // Reset messages
            errorMessage.style.display = "none";
            successMessage.style.display = "none";

            // Validate user selection
            if (!selectedUser) {
                errorMessage.textContent = "Please select a user!";
                errorMessage.style.display = "block";
                return false;
                //document.getElementById('submit').disabled = true;
            }

            // Validate PIN format
            if (!/^\d{4}$/.test(enteredPin)) {
                errorMessage.textContent = "PIN must be 4 digits!";
                errorMessage.style.display = "block";
                event.preventDefault();
                //document.getElementById('submit').disabled = true;
                return false;
            }

            // Check if PIN matches
            if (userPins[selectedUser] === enteredPin) {
                successMessage.style.display = "block";
                //document.getElementById("pinInput").value = ""; // Clear PIN input
                // Here you can add code to allow access to the page content
            } else {
                //message.alert("Invalid PIN!");
                errorMessage.textContent = "Invalid PIN!";
                errorMessage.style.display = "block";
                event.preventDefault();
                return false;

            }
            return true;
        }

