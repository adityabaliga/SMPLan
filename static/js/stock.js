function generateExcel() {
  // Get the table element by its ID
  var table = document.getElementById('htid_stock');

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
      rowData.push(cells[j].innerText);
    }
    sheets[fieldValue].push(rowData);
  }

      // Get the column indexes that need number formatting
  var numberFormatColumns  = [9, 10]; // Example: columns 2 and 4

   // Add worksheets to the workbook
  for (var sheetName in sheets) {
    var ws = XLSX.utils.aoa_to_sheet(sheets[sheetName]);
    // Set number formatting for the specified columns
    /*var range = XLSX.utils.decode_range(ws['!ref']);
    for (var row = range.s.r + 1; row <= range.e.r; row++) {
    for (var col = range.s.c; col <= range.e.c; col++) {
      var cellAddress = XLSX.utils.encode_cell({ r: row, c: col });
      if (numberFormatColumns.includes(col)) {
        var cellValue = ws[cellAddress].v;

        ws[cellAddress].z = '#,##0.000'; // Set number formatting for the column
        var trimmedValue = parseFloat(cellValue);
        ws[cellAddress].v = trimmedValue.toFixed(3);
      }
    }
  }*/

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