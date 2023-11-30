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
    else{
        cust_split = customer.split(' ');
        if(cust_split.length >=2){
            customer = cust_split[0] + ' ' + cust_split[1];
        }
        cust_name = customer.toUpperCase();
    }

    return cust_name;
}


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

function make_label_old(smpl_no, customer){
    //var t = th;
    var queryString = decodeURIComponent(window.location.search);
    var url = window.location.href;
    queryString = queryString.substring(1);
    var queries = queryString.split(";");

    queries[2] = queries[2].replace('x', ' X ');
    var width_length = queries[2].split('X');
    var coil_length = 0;
    var packet_wt = document.getElementById('lbl_pkt_wt').value;
    var thickness = document.getElementById('lbl_size').value;
    var numbers_for_lbl = queries[4];

    if(width_length[1].trim() == '0'){
        width_length[1] = 'Coil';
        //if material is coil, numbers should show length
        var material_density = 0.00000785;
        coil_length = packet_wt/Number(thickness)/Number(width_length[0])/material_density;
        numbers_for_lbl = coil_length.toFixed(0);
    }

    var size = ' X ' +  width_length[0] + ' X ' + width_length[1];

    var smpl_no = queries[0].split('=');
    document.getElementById('lbl_smpl_no').value = smpl_no[1];
    document.getElementById('lbl_prod_date').value = queries[5];

    document.getElementById('lbl_size').value += size;
    document.getElementById('lbl_customer').value = cust_name_for_label(document.getElementById('lbl_customer').value);
    document.getElementById('lbl_numbers').value = numbers_for_lbl;
    document.getElementById('lbl_packet_name').value = queries[3];
    document.getElementById('lbl_mat_status').value = queries[6];

    document.getElementById('lbl_machine').value = queries[1].replaceAll('+',' ');
    //Need to remove Lami type from machine and add it to Lami field
    machine = queries[1];
    if(queries[1].includes("Both")){

        machine = machine.split("Both");
        lbl_machine = machine[0];
        lami = "Both " + machine[1];

        document.getElementById('lbl_lamination').value = lami.replaceAll('+',' ');
        document.getElementById('lbl_machine').value = lbl_machine.replaceAll('+',' ');
    }
    if(queries[1].includes("Single")){

        machine = machine.split("Single");
        lbl_machine = machine[0];
        lami = "Single " + machine[1];

        document.getElementById('lbl_lamination').value = lami.replaceAll('+',' ');
        document.getElementById('lbl_machine').value = lbl_machine.replaceAll('+',' ');
    }

    var qc_name = queries[8].replace('+', ' ');
    qc_name = qc_name.replace('.', '');

    document.getElementById('lbl_qc_name').value = qc_name;

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
    }else{
            material_type = document.getElementById('lbl_mat_type').value;

            material_type = material_type.replaceAll('COIL','');
            material_type = material_type.replaceAll('SHEETS','');
            material_type = material_type.replaceAll('.','');


            grade = document.getElementById('lbl_grade').value;
            scams_no = document.getElementById('lbl_scams_no').value;
            if(scams_no == 'None'){
                scams_no = '';
            }
            coating = document.getElementById('lbl_coating').value;
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