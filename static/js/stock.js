function generateExcel(tablename) {
  // Get the table element by its ID
  var table = document.getElementById(tablename);

  // Create a workbook
  var wb = XLSX.utils.book_new();

  // Get the rows from the table
  var rows = table.getElementsByTagName('tr');

  // Create a dictionary to hold worksheets
  var sheets = {};

  //get the heading row
  var head_row = rows[0];
  var head_row_data = [];
    var head_cells = head_row.cells;
    for (var j = 0; j < head_cells.length; j++) {
      head_row_data.push(head_cells[j].innerText);
    }


  // Iterate over each row and extract the data
  for (var i = 1; i < rows.length; i++) {
    var row = rows[i];


    // Get the value of the field for determining the worksheet
    var fieldValue = (row.querySelector('.status').innerHTML).trim();

    // If the worksheet for the field value doesn't exist, create a new one
    if (!sheets[fieldValue]) {
      sheets[fieldValue] = [];
      sheets[fieldValue].push(head_row_data);
    }

    // Extract row data and add it to the corresponding worksheet
    var rowData = [];
    var cells = row.cells;
    for (var j = 0; j < cells.length; j++) {
        if (j === 10) {
                // Remove any currency symbols, commas, and convert to number
                let cellValue = cells[j].textContent.replace(/[^\d.-]/g, '');

                 // Parse the number to ensure proper formatting
                let numValue = parseFloat(cellValue);

                // If it's a valid number, use it directly
                rowData.push(isNaN(numValue) ? cellValue : numValue);
            }else if (j === 9) {
                // Remove any currency symbols, commas, and convert to number
                let cellValue = cells[j].textContent.replace(/[^\d.-]/g, '');

                 // Parse the number to ensure proper formatting
                let numValue = parseInt(cellValue);

                // If it's a valid number, use it directly
                rowData.push(isNaN(numValue) ? cellValue : numValue);
            }
            else{
            rowData.push(cells[j].innerText);
        }
    }
    sheets[fieldValue].push(rowData);
  }



   // Add worksheets to the workbook
  for (var sheetName in sheets) {
    var ws = XLSX.utils.aoa_to_sheet(sheets[sheetName]);

    XLSX.utils.book_append_sheet(wb, ws, sheetName);

  }



  // Generate the binary data of the Excel file
  var wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });

  // Convert the binary data to a Blob
  var blob = new Blob([wbout], { type: 'application/octet-stream' });

  // Create a download link and trigger the download
  // Get the current date
    var currentDate = new Date();

    // Format the date to yyyy-mm-dd
    var year = currentDate.getFullYear();
    var month = String(currentDate.getMonth() + 1).padStart(2, '0');
    var day = String(currentDate.getDate()).padStart(2, '0');
    var formattedDate = day + '-' + month + '-' + year;

  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  var file_name = 'HTID_Stock_' + formattedDate + '.xlsx';
  a.download = file_name;
  a.click();
}

function generateInvoiceCheckExcel() {
  // Get the table element by its ID
   var table = document.getElementById('invoice_check');

  var workbook = XLSX.utils.table_to_book(table, { sheet: 'Sheet1' });

   var currentDate = new Date();
  var year = currentDate.getFullYear();
  var month = String(currentDate.getMonth() + 1).padStart(2, '0');
  var day = String(currentDate.getDate()).padStart(2, '0');
  var formattedDate = day + '-' + month + '-' + year;

  var file_name = 'Inv_check_' + formattedDate + '.xlsx';

  XLSX.writeFile(workbook, file_name);



}

function _generateExcelTSDPL(tablename) {
  // Get the table element by its ID
   var table = document.getElementById(tablename);

   /****
        This complicated bit is done because when the excel was downloaded excel was messing with some of the dates
        This caused some dates to be displayed as General formatting and some as Date format.
        This function does the following
        1. Storing the original date value in a data attribute
        2. Converting dates to Excel serial numbers during export
        3. Setting the proper date format in the Excel worksheet
    ****/

   // Create a copy of the table to modify for Excel export
  const tableCopy = table.cloneNode(true);

  // Modify the date cells in the copy
  const dateColumnIndex = 1;
  const rows = tableCopy.getElementsByTagName('tr');

  const weightColumnIndex = 17;

  for (let i = 1; i < rows.length; i++) {
    const cell = rows[i].cells[dateColumnIndex];
    const dateStr = cell.getAttribute('data-value');

    const wt_cell = rows[i].cells[weightColumnIndex];
    const wt_str = wt_cell.firstChild.data;

    if (dateStr) {
      // Convert to Excel serial number format
      const day = parseInt(dateStr.substring(0, 2));
      const month = parseInt(dateStr.substring(3, 5)) - 1; // Month is 0-based
      const year = parseInt(dateStr.substring(7, 10));

      const date = new Date(year, month, day);
      // Excel date serial number (days since 1900)
      const excelDate = 25569 + Math.floor((date.getTime() / (1000 * 60 * 60 * 24)));

      // Set the cell value to the Excel serial number
      cell.textContent = excelDate;
    }

    wt_cell.dataset.value = parseFloat(wt_str);

  }


  var workbook = XLSX.utils.table_to_book(tableCopy, {raw: true});

   // Set date format for the column
  const ws = workbook.Sheets[workbook.SheetNames[0]];
  const range = XLSX.utils.decode_range(ws['!ref']);

  for (let R = range.s.r + 1; R <= range.e.r; R++) {
    const cell_address = XLSX.utils.encode_cell({ r: R, c: dateColumnIndex });
    const wt_cell_address = XLSX.utils.encode_cell({ r: R, c: weightColumnIndex });

    if (!ws[cell_address]) continue;

    // Set number format to date
    if (!ws[cell_address].z) {
      ws[cell_address].z = 'dd/mm/yyyy';
    }

  if (!ws[wt_cell_address]) continue;
  if (!ws[wt_cell_address].z) {
    // Example number formats:
    ws[wt_cell_address].z = '#,##0.000';
  }
  }

  var currentDate = new Date();
  var year = currentDate.getFullYear();
  var month = String(currentDate.getMonth() + 1).padStart(2, '0');
  var day = String(currentDate.getDate()).padStart(2, '0');
  var formattedDate = day + '-' + month + '-' + year;

  var file_name = 'TSDPL_stock_' + formattedDate + '.xlsx';

  XLSX.writeFile(workbook, file_name);



}

function generateExcelTSDPL(tablename) {
  // Get the table element by its ID
  var table = document.getElementById(tablename);

  // Create a workbook
  var wb = XLSX.utils.book_new();

  // Get the rows from the table
  var rows = table.getElementsByTagName('tr');

  // Create a dictionary to hold worksheets
  var sheets = [];


  // Iterate over each row and extract the data
  for (var i = 0; i < rows.length; i++) {
    var row = rows[i];



    // Extract row data and add it to the corresponding worksheet
    var rowData = [];
    var cells = row.cells;
    for (var j = 0; j < cells.length; j++) {
        if (j === 17 & i>0) {
                // Remove any currency symbols, commas, and convert to number
                let cellValue = cells[j].textContent.replace(/[^\d.-]/g, '');

                 // Parse the number to ensure proper formatting
                let numValue = parseFloat(cellValue);

                // If it's a valid number, use it directly
                rowData.push(isNaN(numValue) ? cellValue : numValue);

            }else{
            rowData.push(cells[j].innerText);
        }
    }
    sheets.push(rowData);
  }



   // Add worksheets to the workbook

    var ws = XLSX.utils.aoa_to_sheet(sheets);

    XLSX.utils.book_append_sheet(wb, ws, 'Stock');





  // Generate the binary data of the Excel file
  var wbout = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });

  // Convert the binary data to a Blob
  var blob = new Blob([wbout], { type: 'application/octet-stream' });

  // Create a download link and trigger the download
  // Get the current date
    var currentDate = new Date();

    // Format the date to yyyy-mm-dd
    var year = currentDate.getFullYear();
    var month = String(currentDate.getMonth() + 1).padStart(2, '0');
    var day = String(currentDate.getDate()).padStart(2, '0');
    var formattedDate = day + '-' + month + '-' + year;

  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  var file_name = 'TSDPL_Stock_' + formattedDate + '.xlsx';
  a.download = file_name;
  a.click();
}