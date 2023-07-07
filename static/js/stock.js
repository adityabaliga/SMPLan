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
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'HTID_Stock_.xlsx';
  a.click();
}