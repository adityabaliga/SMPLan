function make_label_old(smpl_no, customer){
    //var t = th;
    var queryString = decodeURIComponent(window.location.search);
    var url = window.location.href;
    queryString = queryString.substring(1);
    var queries = queryString.split(";");




    queries[2] = queries[2].replace('x', ' X ');
    var width_length = queries[2].split('X');
    if(width_length[1].trim() == '0'){
        width_length[1] = 'Coil';
    }

    var size = ' X ' +  width_length[0] + ' X ' + width_length[1];

    var smpl_no = queries[0].split('=');
    document.getElementById('lbl_smpl_no').value = smpl_no[1];
    document.getElementById('lbl_prod_date').value = queries[5];
    document.getElementById('lbl_machine').value = queries[1].replace('+',' ');
    document.getElementById('lbl_size').value += size;
    document.getElementById('lbl_customer').value = cust_name_for_label(document.getElementById('lbl_customer').value);
    document.getElementById('lbl_numbers').value = queries[4];
    document.getElementById('lbl_packet_name').value = queries[3];

    var grade_field = document.getElementById("lbl_grade").value;
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
    if (grade_field.length > 0){
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
                grade = grade.replaceAll(' ','');
            }
            if((grade_field[i].toUpperCase()).includes("COATING")){
                coating = grade_field[i].split("COATING").pop();
                coating = coating.replaceAll(':','');
                coating = coating.replaceAll(' ','');
            }

            if((grade_field[i].toUpperCase()).includes("SCAMS NO")){
                scams_no = grade_field[i].split("SCAMS NO").pop();
                scams_no = scams_no.replaceAll(':','');
                scams_no = scams_no.replaceAll(' ','');
            }
        }
    }
    else if(grade_field == ''){
        grade = 'N/A';
    }
    else{
        grade = grade_field;
    }

    document.getElementById('lbl_grade').value = grade.trimEnd();
    document.getElementById('lbl_mat_type').value = material_type.trimEnd();
    document.getElementById('lbl_scams_no').value = scams_no.trimEnd();

    var customer = document.getElementById('lbl_customer').value;
    var size = queries[2].split('X');
    var width = size[0];
    var output_length = size[1];

    if (customer.startsWith("HONDA") || customer.startsWith("TTSSI")){
        var honda_part_num = honda_part_no(Number(width), Number(output_length));
        honda_part_num = honda_part_num.split(';');
        document.getElementById('lbl_part_no').value = honda_part_num[0];
        if(honda_part_num[1] != 0){
            document.getElementById('lbl_net_wt').value = Math.round(Number(honda_part_num[1]) * Number(queries[4]));
        }
        document.getElementById('lbl_coating').value = honda_part_num[2];
    }

    /*var new_page;
    var data = "";
    data = smpl_no + '&' + customer;
    new_page = window.open('make_label_hist?' + data);*/
}

//This is to call functions in processing.js
//cust_name_for_label();