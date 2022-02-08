var orderController = (function () {
   var Order = function(id, operation, stage_no, input_width, input_length, fg_wip, output_width, output_length, lamination, tolerance, i_dia, processing_wt, wt_per_pkt, numbers, no_of_pkts, no_per_pkt, packing, remarks){
        this.id = id;
        this.operation = operation;
        this.stage_no = stage_no;
        this.input_width = input_width;
        this.input_length = input_length;
        this.fg_wip = fg_wip;
        this.output_width = output_width;
        this.output_length = output_length;
        this.lamination = lamination;
        this.tolerance = tolerance;
        this.i_dia = i_dia;
        this.processing_wt = processing_wt;
        this.wt_per_pkt = wt_per_pkt;
        this.numbers = numbers;
        this.no_of_pkts = no_of_pkts;
        this.nos_per_pkt = no_per_pkt;
        this.packing = packing;
        this.remarks = remarks;
   };

    var Input_size = function(input_size, weight, stage_no){
        this.input_size = input_size;
        this.weight = weight;
        this.stage_no = stage_no;
    };

    var data = {
        allOrders: {
            CTL: [],
            Slitting: [],
            Mini_Slitting: [],
            Narrow_CTL: [],
            Reshearing: [],
            Lamination: [],
            Levelling: []
        },
        totals: {
            operation_prc_wt: [],
            scrap: []
            },
        input_material: [],
        max_stage_no : number = 0
        };


    var calculate_op_proc_wt = function(){
        // for each stage the total of processed weights
    };

   return{
          addOrder: function(input){
                var newOrder, id, input_material;

                // Create new ID
                if (data.allOrders[input.operation].length > 0) {
                    id = data.allOrders[input.operation][data.allOrders[input.operation].length - 1].id + 1;
                } else {
                    id = 0;
                }

                // split input material to get input width and length. 0 is  width and 1 is length
                input_material = input.input_material.split(" x ");

                // Create new order item
                newOrder = new Order(id, input.operation, input.stage_no, input_material[0], input_material[1],
                input.fg_wip, input.cut_width, input.cut_length, input.lamination, input.tolerance, input.i_dia,
                input.processing_wt, input.wt_per_pkt, input.numbers, input.no_of_pkts, input.nos_per_pkt,
                input.packing, input.remarks);

                // Add it to the array based on the operation
                data.allOrders[input.operation].push(newOrder);

                //Return the new Order
                return newOrder;

            },

        makeOrderString: function(){
        var orderString ="";
        var input, i;

          if (data.allOrders['CTL'].length > 0) {
              for(i=0;i<data.allOrders['CTL'].length;i++){
                  input = data.allOrders['CTL'][i];
                  //input_material = input.input_material.split(" x ");
                  orderString += "" + input.operation + "," + input.stage_no + "," + input.input_width + "," +
                  input.input_length + "," + input.fg_wip + "," +  input.output_width + "," + input.output_length + "," +
                  input.lamination + "," +  input.tolerance + "," + input.i_dia + "," + input.processing_wt + "," +
                  input.wt_per_pkt + "," + input.numbers + "," +  input.no_of_pkts + "," + input.nos_per_pkt + "," +
                  input.packing + "," +  input.remarks + "^";
              }
          }
          if (data.allOrders['Slitting'].length > 0) {
              for(i=0;i<data.allOrders['Slitting'].length;i++){
                  input = data.allOrders['Slitting'][i];
                  //input_material = input.input_material.split(" x ");
                  orderString += "" + input.operation + "," + input.stage_no + "," + input.input_width + "," +
                  input.input_length + "," + input.fg_wip + "," +  input.output_width + "," + input.output_length + "," +
                  input.lamination + "," +  input.tolerance + "," + input.i_dia + "," + input.processing_wt + "," +
                  input.wt_per_pkt + "," + input.numbers + "," +  input.no_of_pkts + "," + input.nos_per_pkt + "," +
                  input.packing + "," +  input.remarks + "^";
              }
          }
          if (data.allOrders['Mini_Slitting'].length > 0) {
              for(i=0;i<data.allOrders['Mini_Slitting'].length;i++){
                  input = data.allOrders['Mini_Slitting'][i];
                  //input_material = input.input_material.split(" x ");
                  orderString += "" + input.operation + "," + input.stage_no + "," + input.input_width + "," +
                  input.input_length + "," + input.fg_wip + "," +  input.output_width + "," + input.output_length + "," +
                  input.lamination + "," +  input.tolerance + "," + input.i_dia + "," + input.processing_wt + "," +
                  input.wt_per_pkt + "," + input.numbers + "," +  input.no_of_pkts + "," + input.nos_per_pkt + "," +
                  input.packing + "," +  input.remarks + "^";
              }
          }
          if (data.allOrders['Narrow_CTL'].length > 0) {
              for(i=0;i<data.allOrders['Narrow_CTL'].length;i++){
                  input = data.allOrders['Narrow_CTL'][i];
                  //input_material = input.input_material.split(" x ");
                  orderString += "" + input.operation + "," + input.stage_no + "," + input.input_width + "," +
                  input.input_length + "," + input.fg_wip + "," +  input.output_width + "," + input.output_length + "," +
                  input.lamination + "," +  input.tolerance + "," + input.i_dia + "," + input.processing_wt + "," +
                  input.wt_per_pkt + "," + input.numbers + "," +  input.no_of_pkts + "," + input.nos_per_pkt + "," +
                  input.packing + "," +  input.remarks + "^";
              }
          }
          if (data.allOrders['Reshearing'].length > 0) {
              for(i=0;i<data.allOrders['Reshearing'].length;i++){
                  input = data.allOrders['Reshearing'][i];
                  //input_material = input.input_material.split(" x ");
                  orderString += "" + input.operation + "," + input.stage_no + "," + input.input_width + "," +
                  input.input_length + "," + input.fg_wip + "," +  input.output_width + "," + input.output_length + "," +
                  input.lamination + "," +  input.tolerance + "," + input.i_dia + "," + input.processing_wt + "," +
                  input.wt_per_pkt + "," + input.numbers + "," +  input.no_of_pkts + "," + input.nos_per_pkt + "," +
                  input.packing + "," +  input.remarks + "^";
              }
          }
          if (data.allOrders['Lamination'].length > 0) {
              for(i=0;i<data.allOrders['Lamination'].length;i++){
                  input = data.allOrders['Lamination'][i];
                  //input_material = input.input_material.split(" x ");
                  orderString += "" + input.operation + "," + input.stage_no + "," + input.input_width + "," +
                  input.input_length + "," + input.fg_wip + "," +  input.output_width + "," + input.output_length + "," +
                  input.lamination + "," +  input.tolerance + "," + input.i_dia + "," + input.processing_wt + "," +
                  input.wt_per_pkt + "," + input.numbers + "," +  input.no_of_pkts + "," + input.nos_per_pkt + "," +
                  input.packing + "," +  input.remarks + "^";
              }
          }
          return orderString;
        },


       deleteSize: function(operation, ID){
                var ids, index;

                //This returns an array of the IDs to an array ids
                ids = data.allOrders[operation].map(function(current) {
                    return current.id;
                });

                // This returns the index of the ID element
                index = ids.indexOf(ID);

                // This deletes the element at the position = index and 1 element
                if(index !== -1){
                    data.allOrders[operation].splice(index,1);
                }



       },

       getSize: function(operation,ID){
           var ids, index;

                //This returns an array of the IDs to an array ids
                ids = data.allOrders[operation].map(function(current) {
                    return current.id;
                });

                // This returns the index of the ID element
                index = ids.indexOf(ID);

                // This deletes the element at the position = index and 1 element
                if(index !== -1){
                    return data.allOrders[operation][index];
                }
       },

        newInputSize: function(input_size, wt, mc_stage_no){
            var newInput;

            newInput = new Input_size(input_size, wt, (parseFloat(mc_stage_no) + 1));

            data.input_material.push(newInput);

            return data.input_material;

            },

        // This updates the array input size. The input width and length are searched for in the array
        // and the wt of the input is updated accordingly.
        updateInputSize : function(input_width, input_length, processing_wt, sign){

            var ip_size, currentInputMaterial, input_size,i,weight;

            ip_size = input_width + " x " + input_length;

            for(i=0;i<data.input_material.length;i++){
                    if(data.input_material[i].input_size === ip_size){
                        if(sign === "minus"){
                            weight =data.input_material[i].weight-processing_wt;
                            data.input_material[i].weight = weight.toFixed(3);
                        }if(sign === "plus"){
                            weight = parseFloat(data.input_material[i].weight) + parseFloat(processing_wt);
                            data.input_material[i].weight = weight.toFixed(3);
                        }
                    }
                }


            },

        returnInputSize: function(){
            return data.input_material;
        },
       testing: function() {
            console.log(data);
        },

       getMaxStageNo: function(){
           return data.max_stage_no;
       },
       incrementMaxStageNo : function(){
           data.max_stage_no +=1;
           return data.max_stage_no;
       }



        };
})();


var UIController = (function() {
   var DOMStrings= {
       orderForm: '.order_form',
       smpl_no : '.smpl_no',
       customer : '.customer',
       grade : '.grade',
       thickness : '.thickness',
       mc_weight : '.available_wt',
       mc_width : '.width',
       mc_length : 'length',
       coilProcWtID : 'processing_wt',
       order_date : '.order_date',
       expected_date : '.expected_date',
       currentOperation : '.current_op_name',
       currentStageNo : '.current_op_stage',
       currentInputMaterial : '.current_op_ip_mtrl',
       currentFG_WIP : '.fg_wip',
       currentWidth : '.cut_width',
       currentWidthHdr : '.cut_width_hdr',
       currentLength : '.cut_length',
       currentLengthHdr : '.cut_length_hdr',
       currentLami : '.lami',
       currentLamiHdr : '.lami_hdr',
       currentTolerance : '.tol',
       currentIDia : '.iDia',
       currentIdiaHdr : '.iDia_hdr',
       currentProcWt : '.prc_wt',
       currentProcWtHdr : '.prc_wt_hdr',
       currentWtPerPkt : '.wt_per_pkt',
       currentWtPerPktHdr : '.wt_per_pkt_hdr',
       currentNumbers : '.numbers',
       currentNumbersHdr : '.numbers_hdr',
       currentNoOfPkts : '.no_of_pkts',
       currentNoOfPktsHdr : '.no_of_pkts_hdr',
       currentNoPerPkt : '.no_per_pkt',
       currentNoPerPktHdr : '.no_per_pkt_hdr',
       currentPkg : '.packing',
       currentPkgHdr : '.packing_hdr',
       currentOpProcWt : '.processing_wt_for_op',
       currentOpProcWtHdr : '.processing_wt_for_op_hdr',
       currentAvailableWidthHdr: '.available_width_hdr',
       currentAvailableWidth: '.available_width',
       currentNoOfParts_:'.no_of_parts',
       currentNoOfPartsHdr:'.no_of_parts_hdr',
       currentRemarks : '.remarks',
       addSizeBtn : '.add_size_btn',
       addOpBtn:'.add_op_btn',
       CTL_table : '.CTL_table',
       Slitting_table : '.Slitting_table',
       Narrow_CTL_table : '.Narrow_CTL_table',
       Reshearing_table : '.Reshearing_table',
       Mini_Slitting_table : '.Mini_Slitting_table',
       Lamination_table : '.Lamination_table',
       Levelling_table : '.Levelling_table',
       operationProcessingWt : '.op_processing_wt',
       operationScrap : '.total_scrap',
       sizesTable : '.sizes_table',
       submitBtn : '.submit_btn',
       orderString : '.order_string'
   };

   return{
        getDOMstrings: function() {
                return DOMStrings;
        },

       getInput: function(){
           return{
               stage_no : parseFloat(document.querySelector(DOMStrings.currentStageNo).value),
               operation : document.querySelector(DOMStrings.currentOperation).value,
               input_material : document.querySelector(DOMStrings.currentInputMaterial).value,
               fg_wip : document.querySelector(DOMStrings.currentFG_WIP).value,
               cut_width : parseFloat(document.querySelector(DOMStrings.currentWidth).value),
               cut_length : parseFloat(document.querySelector(DOMStrings.currentLength).value),
               lamination : document.querySelector(DOMStrings.currentLami).value,
               tolerance : document.querySelector(DOMStrings.currentTolerance).value,
               i_dia : parseFloat(document.querySelector(DOMStrings.currentIDia).value),
               processing_wt : parseFloat(document.querySelector(DOMStrings.currentProcWt).value),
               wt_per_pkt : parseFloat(document.querySelector(DOMStrings.currentWtPerPkt).value),
               numbers : parseFloat(document.querySelector(DOMStrings.currentNumbers).value),
               nos_per_pkt : parseFloat(document.querySelector(DOMStrings.currentNoPerPkt).value),
               no_of_pkts : parseFloat(document.querySelector(DOMStrings.currentNoOfPkts).value),
               packing : document.querySelector(DOMStrings.currentPkg).value,
               remarks : document.querySelector(DOMStrings.currentRemarks).value
           };
       },

       addListOrder : function(newOrder, operation){
           var html, newHTML, element;

           if(operation === "CTL"){
               element = DOMStrings.CTL_table;
               html = '<tr id="size-CTL-%id%"><td>%stage_no%</td><td>%fg_wip%</td><td>%input_material%</td><td hidden>%op_width%</td><td>%op_length%</td><td>%lamination%</td><td>%tolerance%</td><td hidden>%i_dia%</td><td>%proc_wt%</td><td>%numbers%</td><td>%nos_per_packet%</td><td>%no_of_pkts%</td><td>%packing%</td><td>%remarks%</td><td><input type="button" class="item__delete--btn" value="Delete"></button></td><td><input type="button" class="item__edit--btn" value="Edit"></button></td></tr>';

           }
           if(operation === "Narrow_CTL"){
               element = DOMStrings.Narrow_CTL_table;
               html = '<tr id="size-Narrow_CTL-%id%"><td>%stage_no%</td><td>%fg_wip%</td><td>%input_material%</td><td hidden>%op_width%</td><td>%op_length%</td><td hidden>%lamination%</td><td>%tolerance%</td><td hidden>%i_dia%</td><td>%proc_wt%</td><td>%numbers%</td><td>%nos_per_packet%</td><td>%no_of_pkts%</td><td>%packing%</td><td>%remarks%</td><td><input type="button" class="item__delete--btn" id="del_size" name="del_size" value="Delete"></button></td><td><input type="button" class="item__edit--btn" id="edit_size" name="edit_size" value="Edit"></button></td></tr>';

           }
           if(operation === "Reshearing"){
               element = DOMStrings.Reshearing_table;
               html = '<tr id="size-Reshearing-%id%"><td>%stage_no%</td><td>%fg_wip%</td><td>%input_material%</td><td>%op_width%</td><td>%op_length%</td><td hidden>%lamination%</td><td>%tolerance%</td><td hidden>%i_dia%</td><td>%proc_wt%</td><td>%numbers%</td><td>%nos_per_packet%</td><td>%no_of_pkts%</td><td>%packing%</td><td>%remarks%</td><td><input type="button" class="item__delete--btn" id="del_size" name="del_size" value="Delete"></button></td><td><input type="button" class="item__edit--btn" id="edit_size" name="edit_size" value="Edit"></button></td></tr>';

           }
           if(operation === "Slitting"){
               element = DOMStrings.Slitting_table;
               html = '<tr id="size-Slitting-%id%"><td>%stage_no%</td><td>%fg_wip%</td><td>%input_material%</td><td>%op_width%</td><td hidden>%op_length%</td><td hidden>%lamination%</td><td>%tolerance%</td><td>%i_dia%</td><td>%proc_wt%</td><td>%numbers%</td><td>%nos_per_packet%</td><td>%no_of_pkts%</td><td>%packing%</td><td>%remarks%</td><td><input type="button" class="item__delete--btn" id="del_size" name="del_size" value="Delete"></button></td><td><input type="button" class="item__edit--btn" id="edit_size" name="edit_size" value="Edit"></button></td></tr>';

           }
           if(operation === "Mini_Slitting"){
               element = DOMStrings.Mini_Slitting_table;
               html = '<tr id="size-Mini_Slitting-%id%"><td>%stage_no%</td><td>%fg_wip%</td><td>%input_material%</td><td>%op_width%</td><td hidden>%op_length%</td><td hidden>%lamination%</td><td>%tolerance%</td><td>%i_dia%</td><td>%proc_wt%</td><td>%numbers%</td><td>%nos_per_packet%</td><td>%no_of_pkts%</td><td>%packing%</td><td>%remarks%</td><td><input type="button" class="item__delete--btn" id="del_size" name="del_size" value="Delete"></button></td><td><input type="button" class="item__edit--btn" id="edit_size" name="edit_size" value="Edit"></button></td></tr>';

           }
           if(operation === "Lamination"){
               element = DOMStrings.Lamination_table;
               html = '<tr id="size-Lamination-%id%"><td>%stage_no%</td><td>%fg_wip%</td><td>%input_material%</td><td>%op_width%</td><td>%op_length%</td><td>%lamination%</td><td>%tolerance%</td><td hidden>%i_dia%</td><td>%proc_wt%</td><td>%numbers%</td><td>%nos_per_packet%</td><td>%no_of_pkts%</td><td>%packing%</td><td>%remarks%</td><td><input type="button" class="item__delete--btn" id="del_size" name="del_size" value="Delete"></button></td><td><input type="button" class="item__edit--btn" id="edit_size" name="edit_size" value="Edit"></button></td></tr>';

           }
           if(operation === "Levelling"){
               element = DOMStrings.Levelling_table;
               html = '<tr id="size-Levelling-%id%"><td>%stage_no%</td><td>%fg_wip%</td><td>%input_material%</td><td>%op_width%</td><td>%op_length%</td><td hidden>%lamination%</td><td>%tolerance%</td><td hidden>%i_dia%</td><td>%proc_wt%</td><td>%numbers%</td><td>%nos_per_packet%</td><td>%no_of_pkts%</td><td>%packing%</td><td>%remarks%</td><td><input type="button" class="item__delete--btn" id="del_size" name="del_size" value="Delete"></button></td><td><input type="button" class="item__edit--btn" id="edit_size" name="edit_size" value="Edit"></button></td></tr>';

           }

           newHTML = html.replace('%stage_no%',newOrder.stage_no);
           newHTML = newHTML.replace('%id%', newOrder.id);
           newHTML = newHTML.replace('%fg_wip%', newOrder.fg_wip);
           newHTML = newHTML.replace('%input_material%', newOrder.input_width + " x " +  newOrder.input_length);
           newHTML = newHTML.replace('%op_width%', newOrder.output_width);
           newHTML = newHTML.replace('%op_length%', newOrder.output_length);
           newHTML = newHTML.replace('%lamination%', newOrder.lamination);
           newHTML = newHTML.replace('%tolerance%', newOrder.tolerance);
           newHTML = newHTML.replace('%i_dia%', newOrder.i_dia);
           newHTML = newHTML.replace('%proc_wt%', newOrder.processing_wt);
           newHTML = newHTML.replace('%numbers%', newOrder.numbers);
           newHTML = newHTML.replace('%nos_per_packet%', newOrder.nos_per_pkt);
           newHTML = newHTML.replace('%no_of_pkts%', newOrder.no_of_pkts);
           newHTML = newHTML.replace('%packing%', newOrder.packing);
           newHTML = newHTML.replace('%remarks%', newOrder.remarks);

           // Insert the HTML into the DOM
            document.querySelector(element).insertAdjacentHTML('beforeend', newHTML);
       },

       deleteListSize : function(ID){
           var el = document.getElementById(ID);
            el.parentNode.removeChild(el);

       },

       clearSizeFields: function(){
           document.querySelector(DOMStrings.currentFG_WIP).value = "FG";
           document.querySelector(DOMStrings.currentWidth).value = "";
           document.querySelector(DOMStrings.currentLength).value = "";
           document.querySelector(DOMStrings.currentLami).value = "No Lamination";
           document.querySelector(DOMStrings.currentTolerance).value = "";
           //document.querySelector(DOMStrings.currentIDia).value = "";
           document.querySelector(DOMStrings.currentProcWt).value = "";
           document.querySelector(DOMStrings.currentWtPerPkt).value = "";
           document.querySelector(DOMStrings.currentNumbers).value = "";
           document.querySelector(DOMStrings.currentNoPerPkt).value = "";
           document.querySelector(DOMStrings.currentNoOfPkts).value = "";
           document.querySelector(DOMStrings.currentPkg).value = "";
           document.querySelector(DOMStrings.currentRemarks).value ="";
           document.querySelector(DOMStrings.currentPkg).hidden = false;
           document.querySelector(DOMStrings.currentPkgHdr).hidden = false;

       },


       // This refreshes the input size drop down in the UI
       refreshInputSize: function(newInput, mother_size, fromFunction){
          var element, html, newHTML,i, firstOption, mother_size_, DOM;

           element = document.querySelector(DOMStrings.currentInputMaterial);
           // This removes the "Select Input" option from the drop down
           while (document.querySelector(DOMStrings.currentInputMaterial).firstChild) {
                document.querySelector(DOMStrings.currentInputMaterial).removeChild(document.querySelector(DOMStrings.currentInputMaterial).firstChild);
            }

           // IN add operation Select Input has to be added. Else, the same input size has to be maintained as input material
           if(fromFunction === "addOperation"){
                firstOption = '<option selected disabled>Select Input</option>';
                document.querySelector(DOMStrings.currentInputMaterial).insertAdjacentHTML('beforeend', firstOption);
           }

           // The array newInput populates the dropdown
           for (i=0;i<newInput.length;i++){


                html = '<option value="%input_size%" %sel% %disabled%>%input_size%    %wt% MT</option>';

                newHTML = html.replace('%input_size%', newInput[i].input_size);
                newHTML = newHTML.replace('%input_size%', newInput[i].input_size);
                newHTML = newHTML.replace('%wt%', newInput[i].weight);

               //If all the material used then the user should not be able to select it in the input material
               if(newInput[i].weight === "0.000"){
                   newHTML = newHTML.replace('%disabled%', 'disabled');
               }else{
                   newHTML = newHTML.replace('%disabled%', '');
                   }
                 // If the mother size is the input size, it should be automatically selected.
                if(mother_size == newInput[i].input_size){
                   if(fromFunction !== "addOperation"){
                     newHTML = newHTML.replace('%sel%', 'selected');
                 }

                   // Width of CTL size is set only on change of input material. When we add size, the user does not change input material,
                   // so we are setting the width here.
                   if(document.querySelector(DOMStrings.currentOperation).value === "Narrow_CTL" || document.querySelector(DOMStrings.currentOperation).value === "CTL"){
                        mother_size_  = mother_size.split(" x ");
                        document.querySelector(DOMStrings.currentWidth).value = mother_size_[0];
                   }
               }else{
                   newHTML = newHTML.replace('%sel%', "");
               }

                document.querySelector(DOMStrings.currentInputMaterial).insertAdjacentHTML('beforeend', newHTML);
            }





       },

       checkOperationDetails: function(){
           var flag;
           flag=true;

           if(document.querySelector(DOMStrings.currentOperation === "") && document.querySelector(DOMStrings.currentInputMaterial === "")){
               flag = false;
           }
           return flag;
       },

       populateSizeUI: function(size_details){
           document.querySelector(DOMStrings.currentOperation).value = size_details.operation;
           document.querySelector(DOMStrings.currentStageNo).value = size_details.stage_no;
           document.querySelector(DOMStrings.currentInputMaterial).value = size_details.input_width + " x " + size_details.input_length;
           document.querySelector(DOMStrings.currentIDia).value = size_details.i_dia;
           document.querySelector(DOMStrings.currentNoOfParts_).value = size_details.no_of_pkts;
           document.querySelector(DOMStrings.currentFG_WIP).value = size_details.fg_wip;
           document.querySelector(DOMStrings.currentWidth).value = size_details.output_width;
           document.querySelector(DOMStrings.currentLength).value = size_details.output_length;
           document.querySelector(DOMStrings.currentTolerance).value = size_details.tolerance;
           document.querySelector(DOMStrings.currentLami).value = size_details.lamination;
           document.querySelector(DOMStrings.currentProcWt).value = size_details.processing_wt;
           document.querySelector(DOMStrings.currentWtPerPkt).value = size_details.wt_per_pkt;
           document.querySelector(DOMStrings.currentNumbers).value = size_details.numbers;
           document.querySelector(DOMStrings.currentNoPerPkt).value = size_details.nos_per_pkt;
           document.querySelector(DOMStrings.currentNoOfPkts).value = size_details.no_of_pkts;
           document.querySelector(DOMStrings.currentPkg).value = size_details.packing;
           document.querySelector(DOMStrings.currentRemarks).value = size_details.remarks;
       },

       clearOperationFields: function(){


           document.querySelector(DOMStrings.currentOperation).selectedIndex = 0;


           firstOption = '<option selected disabled>Select Input</option>';
           document.querySelector(DOMStrings.currentInputMaterial).insertAdjacentHTML('afterbegin', firstOption);

            //UIController.refreshInputSize("","","addOperation");

           document.querySelector(DOMStrings.currentIDia).selectedIndex = 0;

           document.querySelector(DOMStrings.currentNoOfParts_).value = "";

           document.querySelector(DOMStrings.currentAvailableWidth).value = "";

           document.querySelector(DOMStrings.currentOpProcWt).value = "";

       }



   };
})();

var controller = (function(orderCtrl, UICtrl) {
   var setupEventListeners = (function(){
      var DOM = UICtrl.getDOMstrings();
       document.getElementById('expected_date').addEventListener("focusout",checkExpectedDate);

       //document.querySelector(DOM.orderForm).addEventListener("load", formOnLoad);

       window.addEventListener("load", formOnLoad);

       document.getElementById(DOM.coilProcWtID).addEventListener("change", onChangeCoilProcessingWt);

       // Commented out for now because the alert box is not going
       //document.getElementById(DOM.coilProcWtID).addEventListener("focusout", onFocusOutCoilProcessingWt);

       document.querySelector(DOM.currentOperation).addEventListener("change", onChangeOperation);

       document.querySelector(DOM.currentInputMaterial).addEventListener("change", onChangeInputMaterial);

       document.querySelector(DOM.currentFG_WIP).addEventListener("change", onChangeFG_WIP);

       document.querySelector(DOM.currentWidth).addEventListener("change", onChangeWidth);

       document.querySelector(DOM.currentLength).addEventListener("change", onChangeLength);
       document.querySelector(DOM.currentProcWt).addEventListener("change", onChangeLength);

       document.querySelector(DOM.currentNumbers).addEventListener("change", onChangeNumbers);

       document.querySelector(DOM.currentWtPerPkt).addEventListener("change", function(event){
           if(document.querySelector(DOM.currentOperation).value === "CTL" || document.querySelector(DOM.currentOperation).value === "Narrow_CTL" || document.querySelector(DOM.currentOperation).value === "Reshearing" || document.querySelector(DOM.currentOperation).value === "Levelling" || document.querySelector(DOM.currentOperation).value === "Lamination"){
               onChangeWtPerPkt();
           }
       });

       document.querySelector(DOM.currentNoOfPkts).addEventListener("change", function(event){
           if(document.querySelector(DOM.currentOperation).value === "Slitting" || document.querySelector(DOM.currentOperation).value === "Mini_Slitting"){
               onChangeNoOfParts();
           }
       });

       document.querySelector(DOM.addSizeBtn).addEventListener('click', addSize);

       document.querySelector(DOM.addOpBtn).addEventListener('click', addOperation);

       document.querySelector(DOM.sizesTable).addEventListener('click', deleteEditSize);

       document.getElementById('order').addEventListener('submit', function(event){
           //event.preventDefault();
            onSubmit();
       });
   });

    var formOnLoad = function(){
        var DOM = UICtrl.getDOMstrings();
        var input_size, length_of_coil, ip_size;
        console.log('Hello');
        document.getElementById("processing_wt").focus();



        // set all fields to default values
        document.querySelector(DOM.currentWidth).value = document.querySelector(DOM.mc_width).value;
        document.querySelector(DOM.currentStageNo).value = orderController.incrementMaxStageNo();


        //calculate length of coil
        if(parseInt(document.getElementById('length').value) == 0){
            console.log(document.getElementById('length').value);

            length_of_coil = (parseFloat(document.querySelector(DOM.mc_weight).value))/parseFloat(document.querySelector(DOM.mc_width).value)
            /parseFloat(document.querySelector(DOM.thickness).value)/0.00000785;
            console.log((document.querySelector(DOM.mc_weight).value));
            document.getElementById('length_of_coil').value = Math.round(length_of_coil);

        }

    };

    var checkExpectedDate = function(){
      // Check if Expected Date > Order Date > Incoming Date

        var order_date = new Date(document.getElementById("order_date").value);
        var expected_date = new Date(document.getElementById("expected_date").value);
        var coil_proc_wt = document.getElementById("processing_wt").value;
        var date_check = true;

         if (order_date > expected_date)
         {
            alert("Order date cannot be greater than expected date!");
            document.getElementById("order_date").focus();
            document.getElementById("expected_date").value = null;
         }

        if (coil_proc_wt === ""){
            document.getElementById("processing_wt").focus();
            alert("Please enter Coil processing weight before proceeding");

        }
    };

    var onChangeOperation = function(){
        console.log('Change Operation');
        var coil_proc_wt, DOM, input_material,i,ip;
        DOM = UICtrl.getDOMstrings();

        // If coil processing weight not entered, it will ask you to enter it now
        coil_proc_wt = document.getElementById("processing_wt").value;
        if (coil_proc_wt === ""){
            document.getElementById("processing_wt").focus();

            alert("Please enter Coil processing weight before proceeding");

        }

        // This part disable selection of coils for reshearing and sheets for CTL and slitting
        input_material = document.querySelector(DOM.currentInputMaterial);
        for(i=0;i<input_material.length;i++){
            ip = input_material[i].value;
            ip = ip.split(" x ");
            if(document.querySelector(DOM.currentOperation).value === "Narrow_CTL" || document.querySelector(DOM.currentOperation).value === "CTL" || document.querySelector(DOM.currentOperation).value === "Slitting" || document.querySelector(DOM.currentOperation).value === "Mini_Slitting"){
                if(parseFloat(ip[1]) != 0){
                    input_material[i].disabled = true;
                }else{
                    input_material[i].disabled = false;
                }
            }
            if(document.querySelector(DOM.currentOperation).value === "Reshearing" || document.querySelector(DOM.currentOperation).value === "Levelling" || document.querySelector(DOM.currentOperation).value === "Lamination"){
                if(parseFloat(ip[1]) == 0){
                    input_material[i].disabled = true;
                }else{
                    input_material[i].disabled = false;
                }
            }
        }



        //For CTL, make width hidden, lamination should appear
        if(document.querySelector(DOM.currentOperation).value === "Narrow_CTL" || document.querySelector(DOM.currentOperation).value === "CTL"){
            document.querySelector(DOM.currentLength).hidden = false;
            document.querySelector(DOM.currentLengthHdr).hidden = false;

            //document.querySelector(DOM.currentWidth).value = document.querySelector(DOM.mc_width).value;
            document.querySelector(DOM.currentWidth).readOnly = true;
            //document.querySelector(DOM.currentWidthHdr).hidden = true;

            if(document.querySelector(DOM.currentOperation).value === "CTL"){
                document.querySelector(DOM.currentLami).hidden = false;
                document.querySelector(DOM.currentLamiHdr).hidden = false;
            }else{
                document.querySelector(DOM.currentLami).hidden = true;
                document.querySelector(DOM.currentLamiHdr).hidden = true;
            }

            document.querySelector(DOM.currentProcWt).readOnly = false;
            document.querySelector(DOM.currentProcWtHdr).hidden = false;
            document.querySelector(DOM.currentProcWt).hidden = false;


            document.querySelector(DOM.currentWtPerPktHdr).innerHTML = "<b>Weight/pkt (in MT)</b>";
            document.querySelector(DOM.currentNumbersHdr).innerHTML = "<b>Numbers</b>";
            document.querySelector(DOM.currentNumbers).readOnly = true;
            document.querySelector(DOM.currentNoOfPkts).readOnly = true;
            document.querySelector(DOM.currentNoPerPkt).readOnly = true;
            document.querySelector(DOM.currentWtPerPkt).readOnly = false;


            document.querySelector(DOM.currentNoPerPktHdr).innerHTML = "<b>No.s/pkt</b>";
            document.querySelector(DOM.currentNoOfPktsHdr).innerHTML = "<b>No. of pkts</b>";

            /*document.querySelector(DOM.currentOpProcWt).hidden = true;
            document.querySelector(DOM.currentOpProcWtHdr).hidden = true;

            document.querySelector(DOM.currentIDia).hidden = true;
            document.querySelector(DOM.currentIdiaHdr).hidden = true;*/


            document.querySelector('.current_op_slitting').hidden = true;

            //numbers was moved to before length for slitting, moving it back to no_per_packet
            var numbers = document.querySelector('.numbers_curr_size');
            var parent = numbers.parentNode;
            var no_per_pakt = document.querySelector('.no_per_pkt_curr_size');
            parent.insertBefore(numbers,no_per_pakt);
            var no_of_pakts = document.querySelector('.no_of_pkts_curr_size');
            var packing = document.querySelector('.packing_curr_size');
            parent.insertBefore(no_of_pakts,packing);
        }

        // For Slitting, change headings, make length and lami hidden
        if(document.querySelector(DOM.currentOperation).value === "Slitting" || document.querySelector(DOM.currentOperation).value === "Mini_Slitting"){
            document.querySelector(DOM.currentWidth).readOnly = false;
            //document.querySelector(DOM.currentWidthHdr).hidden = false;
            document.querySelector(DOM.currentWidth).value = '';

            document.querySelector(DOM.currentLength).hidden = true;
            document.querySelector(DOM.currentLength).value = '0.0';
            document.querySelector(DOM.currentLengthHdr).hidden = true;

            document.querySelector(DOM.currentLami).hidden = true;
            document.querySelector(DOM.currentLamiHdr).hidden = true;

            document.querySelector(DOM.currentProcWt).hidden = true;
            document.querySelector(DOM.currentProcWtHdr).hidden = true;

            /*document.querySelector(DOM.currentOpProcWt).hidden = false;
            //document.querySelector(DOM.currentOpProcWt).required = true;
            document.querySelector(DOM.currentOpProcWtHdr).hidden = false;

            document.querySelector(DOM.currentIDia).hidden = false;
            document.querySelector(DOM.currentIdiaHdr).hidden = false;

            document.querySelector(DOM.currentAvailableWidth).hidden = false;
            document.querySelector(DOM.currentAvailableWidthHdr).hidden = false;

            document.querySelector(DOM.currentNoOfParts_).hidden = false;
            document.querySelector(DOM.currentNoOfPartsHdr).hidden = false;*/

            document.querySelector('.current_op_slitting').hidden = false;



            document.querySelector(DOM.currentWtPerPktHdr).innerHTML = "<b>Weight/Part (in MT)</b>";
            document.querySelector(DOM.currentNumbersHdr).readOnly = true;
            document.querySelector(DOM.currentNumbersHdr).innerHTML = "<b>No. of Slits</b>";

            document.querySelector(DOM.currentNoPerPktHdr).innerHTML = "<b>Length Per Part (in metres)</b>";
            document.querySelector(DOM.currentNoOfPktsHdr).innerHTML = "<b>No. of Parts</b>";

            document.querySelector(DOM.currentNumbers).readOnly = false;
            document.querySelector(DOM.currentNoOfPkts).readOnly = true;
            document.querySelector(DOM.currentNoPerPkt).readOnly = true;

            document.querySelector(DOM.currentWtPerPkt).readOnly = true;

            //Changing order of no. of slits for better usability
            //var current_sizes = document.querySelector('.current_sizes');
            var no_of_slits = document.querySelector('.numbers_curr_size');
            var no_of_parts = document.querySelector('.no_of_pkts_curr_size')
            var parent = no_of_slits.parentNode;
            var length = document.querySelector('.cut_length_curr_size');
            parent.insertBefore(no_of_slits,length);
            parent.insertBefore(no_of_parts,length);

        }

        // for Reshearing, hide lami
        if(document.querySelector(DOM.currentOperation).value === "Reshearing"){
            document.querySelector(DOM.currentWidth).readOnly = false;
            //document.querySelector(DOM.currentWidthHdr).hidden = false;
            document.querySelector(DOM.currentWidth).value = '';

            document.querySelector(DOM.currentLength).hidden = false;
            document.querySelector(DOM.currentLengthHdr).hidden = false;

            document.querySelector(DOM.currentLami).hidden = true;
            document.querySelector(DOM.currentLamiHdr).hidden = true;

            document.querySelector(DOM.currentProcWt).readOnly = false;
            document.querySelector(DOM.currentProcWtHdr).hidden = false;
            document.querySelector(DOM.currentProcWt).hidden = false;


            document.querySelector(DOM.currentWtPerPktHdr).innerHTML = "<b>Weight/pkt (in MT)</b>";
            document.querySelector(DOM.currentNumbersHdr).innerHTML = "<b>Numbers</b>";

            document.querySelector(DOM.currentNumbers).readOnly = true;
            document.querySelector(DOM.currentNoOfPkts).readOnly = true;
            document.querySelector(DOM.currentNoPerPkt).readOnly = true;
            document.querySelector(DOM.currentWtPerPkt).readOnly = false;

            document.querySelector(DOM.currentNoPerPktHdr).innerHTML = "<b>No.s/pkt</b>";
            document.querySelector(DOM.currentNoOfPktsHdr).innerHTML = "<b>No. of pkts</b>";

            /*document.querySelector(DOM.currentOpProcWt).hidden = true;
            document.querySelector(DOM.currentOpProcWtHdr).hidden = true;

            document.querySelector(DOM.currentIDia).hidden = true;
            document.querySelector(DOM.currentIdiaHdr).hidden = true;*/

            document.querySelector('.current_op_slitting').hidden = true;

            //numbers was moved to before length for slitting, moving it back to no_per_packet
            var no_of_slits = document.querySelector('.numbers_curr_size');
            var parent = no_of_slits.parentNode;
            var no_per_pakt = document.querySelector('.no_per_pkt_curr_size');
            parent.insertBefore(no_of_slits,no_per_pakt);
            var no_of_pakts = document.querySelector('.no_of_pkts_curr_size');
            var packing = document.querySelector('.packing_curr_size');
            parent.insertBefore(no_of_pakts,packing);
        }

        //For Lamination and Levelling, the size should not change
        if(document.querySelector(DOM.currentOperation).value === "Lamination" || document.querySelector(DOM.currentOperation).value === "Levelling"){
            document.querySelector(DOM.currentLength).hidden = false;
            document.querySelector(DOM.currentLengthHdr).hidden = false;

            //document.querySelector(DOM.currentWidth).value = document.querySelector(DOM.mc_width).value;
            //document.querySelector(DOM.currentLength).value = document.querySelector(DOM.mc_length).value;
            document.querySelector(DOM.currentWidth).readOnly = true;
            document.querySelector(DOM.currentLength).readOnly = true;
            //document.querySelector(DOM.currentWidthHdr).hidden = true;

            if(document.querySelector(DOM.currentOperation).value === "Lamination"){
                document.querySelector(DOM.currentLami).hidden = false;
                document.querySelector(DOM.currentLamiHdr).hidden = false;
            }else{
                document.querySelector(DOM.currentLami).hidden = true;
                document.querySelector(DOM.currentLamiHdr).hidden = true;
            }

            document.querySelector(DOM.currentProcWt).readOnly = false;
            document.querySelector(DOM.currentProcWtHdr).hidden = false;
            document.querySelector(DOM.currentProcWt).hidden = false;


            document.querySelector(DOM.currentWtPerPktHdr).innerHTML = "<b>Weight/pkt (in MT)</b>";
            document.querySelector(DOM.currentNumbersHdr).innerHTML = "<b>Numbers</b>";
            document.querySelector(DOM.currentNumbers).readOnly = true;
            document.querySelector(DOM.currentNoOfPkts).readOnly = true;
            document.querySelector(DOM.currentNoPerPkt).readOnly = true;
            document.querySelector(DOM.currentWtPerPkt).readOnly = false;


            document.querySelector(DOM.currentNoPerPktHdr).innerHTML = "<b>No.s/pkt</b>";
            document.querySelector(DOM.currentNoOfPktsHdr).innerHTML = "<b>No. of pkts</b>";

            /*document.querySelector(DOM.currentOpProcWt).hidden = true;
            document.querySelector(DOM.currentOpProcWtHdr).hidden = true;

            document.querySelector(DOM.currentIDia).hidden = true;
            document.querySelector(DOM.currentIdiaHdr).hidden = true;*/


            document.querySelector('.current_op_slitting').hidden = true;

            //numbers was moved to before length for slitting, moving it back to no_per_packet
            var numbers = document.querySelector('.numbers_curr_size');
            var parent = numbers.parentNode;
            var no_per_pakt = document.querySelector('.no_per_pkt_curr_size');
            parent.insertBefore(numbers,no_per_pakt);
            var no_of_pakts = document.querySelector('.no_of_pkts_curr_size');
            var packing = document.querySelector('.packing_curr_size');
            parent.insertBefore(no_of_pakts,packing);
        }


    };

    var onChangeInputMaterial = function(){
        var DOM, input_mtrl;
        DOM = UICtrl.getDOMstrings();
        input_mtrl = document.querySelector(DOM.currentInputMaterial).value;
        input_mtrl = input_mtrl.split(" x ");
        console.log(document.querySelector(DOM.currentOperation).value);
        if(document.querySelector(DOM.currentOperation).value === "Slitting" || document.querySelector(DOM.currentOperation).value === "Mini_Slitting"){

                document.querySelector(DOM.currentAvailableWidth).value = input_mtrl[0];
           }
        if(document.querySelector(DOM.currentOperation).value === "Narrow_CTL" || document.querySelector(DOM.currentOperation).value === "CTL"){
            document.querySelector(DOM.currentWidth).value = input_mtrl[0];
        }
        if(document.querySelector(DOM.currentOperation).value === "Levelling" || document.querySelector(DOM.currentOperation).value === "Lamination"){
            document.querySelector(DOM.currentWidth).value = input_mtrl[0];
            document.querySelector(DOM.currentLength).value = input_mtrl[1];
        }
    };

    var onChangeFG_WIP = function(){
      console.log('Change FG');
        var DOM = UICtrl.getDOMstrings();
        //HIde packing, number of packing type, make number of packets value to 1
        if(document.querySelector(DOM.currentFG_WIP).value === "WIP"){
            document.querySelector(DOM.currentPkg).hidden = true;
            document.querySelector(DOM.currentPkgHdr).hidden = true;
            document.querySelector(DOM.currentPkg).required = false;
            //document.querySelector(DOM.currentNoOfPkts).value = "1";

        }
        if(document.querySelector(DOM.currentFG_WIP).value === "FG"){
            document.querySelector(DOM.currentPkg).hidden = false;
            document.querySelector(DOM.currentPkgHdr).hidden = false;
            document.querySelector(DOM.currentPkg).required = true;
            document.querySelector(DOM.currentPkg).value = " ";
            //document.querySelector(DOM.currentNoOfPkts).value = "1";

        }
    };

    var onChangeWidth = function(){
        var DOM = UICtrl.getDOMstrings();

        if(UICtrl.checkOperationDetails){
            //check if width < coil width

            //For slitting and mini slitting check if processing wt is entered after width is changed
            if(document.querySelector(DOM.currentOperation).value === "Slitting" || document.querySelector(DOM.currentOperation).value === "Mini_Slitting"){
                console.log(document.querySelector(DOM.currentOpProcWt).value);
                if(document.querySelector(DOM.currentOpProcWt).value === ""){
                    alert("Please enter Processing Weight for the coil before proceeding");
                    document.querySelector(DOM.currentOpProcWt).focus();
                }
                if(document.querySelector(DOM.currentNumbers).value !== "" && document.querySelector(DOM.currentNoOfPkts).value !== ""){
                    onChangeNoOfParts();
                }
            }else{

                if(document.querySelector(DOM.currentLength).value !== "" && document.querySelector(DOM.currentProcWt).value !== "" && document.querySelector(DOM.currentWtPerPkt).value !== ""){
                    onChangeWtPerPkt();
                }
            }
        }else{
            alert("Please enter operation details");
        }
    };

    //if length or processing wt is changed for non slitting operations after first flow, then wt etc have to be recalculated
    var onChangeLength = function(){
        var DOM = UICtrl.getDOMstrings();
        if(document.querySelector(DOM.currentOperation).value === "Slitting" || document.querySelector(DOM.currentOperation).value === "Mini_Slitting"){
            /*console.log(document.querySelector(DOM.currentOpProcWt).value);
            if(document.querySelector(DOM.currentOpProcWt).value === ""){
                alert("Please enter Processing Weight for the coil before proceeding");
                document.querySelector(DOM.currentOpProcWt).focus();
            }
            if(document.querySelector(DOM.currentNumbers).value !== "" && document.querySelector(DOM.currentNoOfPkts).value !== ""){
                onChangeNoOfParts();
            }*/
        }else{

            if(document.querySelector(DOM.currentLength).value !== "" && document.querySelector(DOM.currentProcWt).value !== "" && document.querySelector(DOM.currentWtPerPkt).value !== ""){
                onChangeWtPerPkt();
            }
        }
    };

    //if no. of slits is changed for slitting operations after first flow, then wt etc have to be recalculated
    var onChangeNumbers = function(){
        var DOM = UICtrl.getDOMstrings();
        if(document.querySelector(DOM.currentOperation).value === "Slitting" || document.querySelector(DOM.currentOperation).value === "Mini_Slitting"){
            document.querySelector(DOM.currentNoOfPkts).value = document.querySelector(DOM.currentNoOfParts_).value;
            document.querySelector(DOM.currentLength).value = "0.0";
            onChangeNoOfParts();


        }else{

            /*if(document.querySelector(DOM.currentLength).value !== "" && document.querySelector(DOM.currentProcWt).value !== "" && document.querySelector(DOM.currentWtPerPkt).value !== ""){
                onChangeWtPerPkt();
            }*/
        }
    };


    var onChangeWtPerPkt = function(){
      //calculate numbers, number of packets, numbers per packet for CTL, NCTl and Reshearing
        var width, length, thickness, processing_wt, numbers, wt_per_pkt, number_of_pkts, numbers_per_pkt, flag, operation;
        var ms_width, ms_length, numbers_per_ms_sheet, ms_numbers, input_mtrl;
        var DOM = UICtrl.getDOMstrings();
        flag = true;
        operation = (document.querySelector(DOM.currentOperation).value);
        width = parseFloat(document.querySelector(DOM.currentWidth).value);
        length = parseFloat(document.querySelector(DOM.currentLength).value);
        thickness = parseFloat(document.querySelector(DOM.thickness).value);
        processing_wt = parseFloat(document.querySelector(DOM.currentProcWt).value);
        wt_per_pkt = parseFloat(document.querySelector(DOM.currentWtPerPkt).value);
        input_mtrl = document.querySelector(DOM.currentInputMaterial).value
        input_mtrl = input_mtrl.split(" x ");
        ms_width = parseFloat(input_mtrl[0]);
        ms_length = parseFloat(input_mtrl[1]);


        if(isNaN(length)){
            alert("Please enter length");
            document.querySelector(DOM.currentLength).focus();
            flag = false;
        }
        if(isNaN(width)){
            alert("Please enter width");
            document.querySelector(DOM.currentWidth).focus();
            flag = false;
        }

        if(flag){
            if (operation != "Reshearing"){
                numbers = Math.round(processing_wt*1000/thickness/width/length/0.00000785);

            }
            // This is because for reshearing has to be calculated based on no. of sheets per mother sheet
            else{
                ms_numbers = Math.round(processing_wt*1000/thickness/ms_width/ms_length/0.00000785);
                numbers_per_ms_sheet = Math.round(ms_width*ms_length/width/length);
                numbers = ms_numbers * numbers_per_ms_sheet;
            }

            number_of_pkts = Math.round(processing_wt/wt_per_pkt);
            numbers_per_pkt = Math.round(numbers/number_of_pkts);

            document.querySelector(DOM.currentNumbers).value = numbers;
            document.querySelector(DOM.currentNoOfPkts).value = number_of_pkts;
            document.querySelector(DOM.currentNoPerPkt).value = numbers_per_pkt;
        }

    };

    var onChangeNoOfParts = function(){
        // This function was initially called when no of parts in size was changed. But, the coil can have only one no. of parts
        // So, we placed it in operation and copy the no of parts from there. So now, this function is called when no of slits is changed
        //calculate length/part and weight/coil for slitting and mini slitting
        var wt_of_slit,length_of_slit, length_per_part, wt_per_part, processing_wt, input_material, ip_width;
        var DOM = UICtrl.getDOMstrings();

        input_material = document.querySelector(DOM.currentInputMaterial).value;
        input_material = input_material.split(" x ");
        ip_width = parseFloat(input_material[0]);
        currentWidth = parseFloat(document.querySelector(DOM.currentWidth).value);

        //This is wt of each individual slit for full coil
        wt_of_slit = parseFloat(document.querySelector(DOM.currentOpProcWt).value) * parseFloat(document.querySelector(DOM.currentWidth).value) / ip_width ;
        length_of_slit = wt_of_slit/parseFloat(document.querySelector(DOM.currentWidth).value)
            /parseFloat(document.querySelector(DOM.thickness).value)/0.00000785;

        length_per_part = length_of_slit/(parseFloat(document.querySelector(DOM.currentNoOfPkts).value));
        wt_per_part = parseFloat(document.querySelector(DOM.thickness).value) * parseFloat(document.querySelector(DOM.currentWidth).value) * length_per_part * 0.00000785;

        processing_wt = wt_of_slit * parseFloat(document.querySelector(DOM.currentNumbers).value);
        document.querySelector(DOM.currentProcWt).value = processing_wt.toFixed(3);
        document.querySelector(DOM.currentWtPerPkt).value = wt_per_part.toFixed(3);
        document.querySelector(DOM.currentNoPerPkt).value = length_per_part.toFixed(0);

    };

    //On change of coil processing wt, check if value is less than mother coil weight, else add size and coil
    // processing wt to list of input mtrl
    var onChangeCoilProcessingWt = function(){
        var input_size, length_of_coil, ip_size, coil_proc_wt, mc_wt;
        var DOM = UICtrl.getDOMstrings();

        //coil_proc_wt = parseFloat(document.querySelector('processing_wt').value);
        coil_proc_wt = parseFloat(document.getElementById(DOM.coilProcWtID).value);
        mc_wt = parseFloat(document.querySelector(DOM.mc_weight).value);

        if(coil_proc_wt>mc_wt){
            alert('Please check processing wt. Processing wt cannot be greater than available weight');
            document.getElementById(DOM.coilProcWtID).focus();
        }else{
            // Add input_size to data
            ip_size = document.querySelector(DOM.mc_width).value + " x " + document.getElementById('length').value;
            input_size = orderCtrl.newInputSize(ip_size, parseFloat(document.getElementById("processing_wt").value), 0);

            //Add input_size to UI
            UICtrl.refreshInputSize(input_size,"","addOperation");
        }
        //Select operation will be enabled only after Coil processing weight is entered
        if(coil_proc_wt>0){
            document.querySelector(DOM.currentOperation).disabled = false;
        }



    };


    var onFocusOutCoilProcessingWt = function(){
        var DOM = UICtrl.getDOMstrings();

        //coil_proc_wt = parseFloat(document.querySelector('processing_wt').value);
        coil_proc_wt = (document.getElementById(DOM.coilProcWtID).value);

        if (coil_proc_wt === ""){

            alert('Please enter processing wt before proceeding');
            document.getElementById(DOM.coilProcWtID).value = " ";
            document.getElementById(DOM.coilProcWtID).focus();
            document.getElementById(DOM.coilProcWtID).value = "";
        }
        if(coil_proc_wt>0){
            document.querySelector(DOM.currentOperation).disabled = false;
        }
    };

    var checkValidInputs = function(input){
        //Check if all the input fields have valid inputs like processing wt, width<mc_width, wt of size<mc_wt and coil proc wt, etc
        var DOM,ip_mtrl_wt,ip_mtrl_selected;

        DOM = UICtrl.getDOMstrings();

        ip_mtrl_selected = document.querySelector(DOM.currentInputMaterial).options[document.querySelector(DOM.currentInputMaterial).selectedIndex].text;

        ip_mtrl_selected = ip_mtrl_selected.split(' ');
        ip_mtrl_wt = parseFloat(ip_mtrl_selected[3]);
        if(ip_mtrl_wt * 1.05 < input.processing_wt){
            alert('Processing Wt is greater than input material weight');
            return false;
        }

        return true;
    };

    var addSize = function(){
        var DOM, input, new_input_size, new_input, available_width, width_used, new_width;

        DOM = UICtrl.getDOMstrings();

        // Get field input data
        input = UICtrl.getInput();

        if(document.querySelector(DOM.currentFG_WIP).value === "FG"){
                if(document.querySelector(DOM.currentPkg).value === ""){
                    alert("Please enter packing type");
                    document.querySelector(DOM.currentPkg).focus();
                    return false;
                }
        }

        if(checkValidInputs(input)){
            //Add item to order Controller
            newOrder = orderCtrl.addOrder(input);

            // Add order to UI in appropriate table
            UICtrl.addListOrder(newOrder, newOrder.operation);

            // Clear input fields
            UICtrl.clearSizeFields();

            //update input material when output is FG
            orderCtrl.updateInputSize(newOrder.input_width, newOrder.input_length, newOrder.processing_wt, "minus");

            if(newOrder.fg_wip === "WIP"){
                new_input_size = newOrder.output_width + " x " + newOrder.output_length;
                new_input = orderCtrl.newInputSize(new_input_size, newOrder.processing_wt);


            }else{
                new_input = orderCtrl.returnInputSize();
            }


            UICtrl.refreshInputSize(new_input, input.input_material, "addSize");



            // if slitting or mini slitting, change available width = (width * no. of slits)
            if(document.querySelector(DOM.currentOperation).value === "Slitting" || document.querySelector(DOM.currentOperation).value === "Mini_Slitting"){
                width_used = newOrder.output_width * newOrder.numbers;
                available_width = parseFloat(document.querySelector(DOM.currentAvailableWidth).value);
                new_width = available_width - width_used;
                if(new_width>=0){
                    document.querySelector(DOM.currentAvailableWidth).value = new_width;
                }else{
                    alert("Please check width");
                    document.querySelector(DOM.currentWidth).focus();
                }
            }
            document.querySelector(DOM.currentFG_WIP).focus();
        }
    };

    var addOperation = function(){
        var DOM;

        DOM = UICtrl.getDOMstrings();
        //Clear all fields and Increase stage number

        UICtrl.clearSizeFields();
        UICtrl.clearOperationFields();

        //Increment stage no
        document.querySelector(DOM.currentStageNo).value = orderController.incrementMaxStageNo();


        //Store available width



        //For slitting see if processing weight = wt of all slit coils

        //Manage balance wt in input material
    };

    var deleteEditSize = function(event){
        var sizeID, splitID, operation, ID,to_do, input_material, processing_wt, i, size_details, newInput, mother_size;

        sizeID = event.target.parentNode.parentNode.id;



        console.log(event.target.className);

        to_do = event.target.className;

        if(sizeID && to_do){
            splitID = sizeID.split('-');
            if(splitID[0] === "size"){
                operation = splitID[1];
                ID = parseInt(splitID[2]);
            }

            size_details = orderCtrl.getSize(operation,ID);

            if(to_do === "item__delete--btn"){


                // delete item from array
                orderCtrl.deleteSize(operation, ID);

                // delete item from UI
                UICtrl.deleteListSize(sizeID);


                // update input size
                orderCtrl.updateInputSize(size_details.input_width, size_details.input_length, size_details.processing_wt, "plus");
                newInput = orderCtrl.returnInputSize();
                mother_size = size_details.input_width + " x " + size_details.input_length;
                UICtrl.refreshInputSize(newInput, mother_size, "addSize");

            }if(to_do === "item__edit--btn"){

                //update UI with the size details
                UICtrl.populateSizeUI(size_details);

                // delete item from array
                orderCtrl.deleteSize(operation, ID);

                // delete item from UI
                UICtrl.deleteListSize(sizeID);

                //get UI changes for UI
                onChangeOperation();

                // update input size
                orderCtrl.updateInputSize(size_details.input_width, size_details.input_length, size_details.processing_wt, "plus");
                newInput = orderCtrl.returnInputSize();
                mother_size = size_details.input_width + " x " + size_details.input_length;
                UICtrl.refreshInputSize(newInput, mother_size, "addSize");


            }
         }

        };

    var onSubmit = function(){
        //alert('submit clicked');
        var orderString, DOM,url, print_order_string;
        DOM = UICtrl.getDOMstrings();
        orderString = orderCtrl.makeOrderString();
        console.log(orderString);
        document.querySelector(DOM.orderString).value = orderString;

        /*print_order_string = document.querySelector(DOM.smpl_no).value + "," + document.querySelector(DOM.grade).value + "," + document.querySelector(DOM.customer).value + "," + document.querySelector(DOM.order_date).value + "," + document.querySelector(DOM.expected_date).value
        url = 'print_order?print=' + print_order_string
        window.open(url)*/
    };

    return {
        init: function() {

            setupEventListeners();
        }
    };
})(orderController,UIController);

controller.init();



/*function setFocusToTextBox(){
    document.getElementById("processing_wt").focus();
}




//http://jsfiddle.net/7AeDQ/ - source of code
//http://viralpatel.net/blogs/dynamically-add-remove-rows-in-html-table-using-javascript/
// This function is to add a row. mm_list is an array of input material possible based on the order.
// It is populated if a row is entered as WIP, in the format of 'width x length"
// http://jsfiddle.net/jackwanders/kGgkE/ source for dynamically populating input material drop down
	var mm_list = [];


	function addRow(tableID)
	 {

			var table = document.getElementById(tableID);

			var rowCount = table.rows.length;
			var row = table.insertRow(rowCount);

			var last_row = document.getElementById(tableID).rows[rowCount-1];
			/*last_row.cells[5].lastChild.value;

			var cut_length = document.getElementById("cut_length").value;
			var cut_width = document.getElementById("cut_width").value;
			var size_no = document.getElementById("stage_no").value;*/
/*			var new_input_material = ""

			if(last_row.cells[10].lastElementChild.value == "WIP"){
			    new_input_material = last_row.cells[4].lastChild.value + " x " + last_row.cells[5].lastChild.value;
			    mm_list.push(new_input_material);
    		    var sel = document.getElementById('input_material');
                i = mm_list.length-1;
                var opt = document.createElement('option');
                opt.innerHTML = mm_list[i];
                opt.value = mm_list[i];
                sel.appendChild(opt);
            }




			var colCount = table.rows[1].cells.length;

			for(var i=0; i<colCount; i++) {

				var newcell	= row.insertCell(i);

				newcell.innerHTML = table.rows[1].cells[i].innerHTML;
				//alert(newcell.childNodes);
				switch(newcell.childNodes[0].type) {
					case "text":
							newcell.childNodes[0].value = "";
							break;
					case "checkbox":
							newcell.childNodes[0].checked = false;
							break;
					case "select-one":
							newcell.childNodes[0].selectedIndex = 0;
							break;
				}
			}
    }

    function addRowModifyOrder(tableID)
	 {

			var table = document.getElementById(tableID);

			var rowCount = table.rows.length;
			var row = table.insertRow(rowCount);
			var colCount = table.rows[2].cells.length;

			for(var i=0; i<colCount; i++) {

				var newcell	= row.insertCell(i);

				newcell.innerHTML = table.rows[2].cells[i].innerHTML;
				//alert(newcell.childNodes);
				switch(newcell.lastElementChild.type) {
					case "text":
							newcell.lastElementChild.value = "";
							break;
					case "checkbox":
							newcell.childNodes[0].checked = false;
							break;
					case "select-one":
							newcell.childNodes[0].selectedIndex = 0;
							break;
                    case "number":
                            newcell.childNodes[0].value = 0;
							break;

				}
			}
		}

    function deleteRow(tableID)
    {
			try {
			var table = document.getElementById(tableID);
			var rowCount = table.rows.length;


			for(var i=1; i<rowCount; i++) {
				var row = table.rows[i];
				var chkbox = row.cells[0].childNodes[0];
				if(null != chkbox && true == chkbox.checked) {
					if(rowCount <= 1) {
						alert("Cannot delete all the rows.");
						break;
					}
					table.deleteRow(i);
					rowCount--;
					i--;
				}
			}
			}catch(e) {
				alert(e);
			}
	}

    // Function to delete row. No change taken straight from source
    function deleteRowModifyOrder(tableID)
    {
			try {
			var table = document.getElementById(tableID);
			var rowCount = table.rows.length;


			for(var i=1; i<rowCount; i++) {
				var row = table.rows[i];
				var chkbox = row.cells[0].childNodes[0];
				//var chkbox = row.childNodes[0];
				if(null != chkbox && true == chkbox.checked) {
					if(rowCount <= 1) {
						alert("Cannot delete all the rows.");
						break;
					}
					table.deleteRow(i);
					rowCount--;
					i--;
				}
			}
			}catch(e) {
				alert(e);
			}
	}

// After input material is selected from drop down. The cut length and cut width set based on CTL or slitting operations selected.
    function  after_input_material(th, tableID){
        var table = document.getElementById(tableID);

		var rowCount = th.parentNode.parentNode.rowIndex;
		var last_row = document.getElementById(tableID).rows[rowCount];
        var answer = last_row.cells[1].lastElementChild.value;

        var input_material = (last_row.cells[3].lastElementChild.value).split(" x ");
        ms_width = input_material[0];
        ms_length = input_material[1];

         if(answer == "Slitting" || answer == "Mini Slitting")
            {
                if(ms_length != 0){
                //alert("The input material is not a coil. Please re-enter input material");
                //alert("The input material is not a coil. Please re-enter input material");
                }
                last_row.cells[5].lastChild.value = 0;
            }
         if(answer == "CTL" || answer == "CTL - 1 side lamination" || answer == "CTL - 2 side lamination" || answer == "Narrow CTL")
            {
                    if(ms_length != 0){
                        //alert("The input material is not a coil. Please re-enter input material");
                    }
                    last_row.cells[4].lastChild.value = ms_width;

            }


    }


    //The place holders of some fields are changed based on the operation selected
    function on_select_operation(th, tableID)
    {
            var table = document.getElementById(tableID);

			var rowCount = th.parentNode.parentNode.rowIndex;

			var last_row = document.getElementById(tableID).rows[rowCount];

            var answer = last_row.cells[1].lastElementChild.value;

            var input_material = (last_row.cells[3].lastElementChild.value).split(" x ");
            ms_width = input_material[0];
            ms_length = input_material[1];

            if(answer == "Slitting" || answer == "Mini Slitting")
            {
                last_row.cells[7].lastChild.placeholder="No. of slits";
                last_row.cells[11].lastChild.placeholder="No. of parts";
                last_row.cells[12].lastChild.placeholder="Length/Part";
                last_row.cells[5].lastChild.value = "0";
                last_row.cells[5].lastChild.readOnly = true;
                if(ms_length != 0){
                alert("The input material is not a coil. Please re-enter input material");
                }
                //last_row.cells[6].lastChild.readOnly = true;
            }
            else
            {
                if(answer == "CTL" || answer == "CTL - 1 side lamination" || answer == "CTL - 2 side lamination" || answer == "Narrow CTL")
                {
                    if(ms_length != 0){
                        alert("The input material is not a coil. Please re-enter input material");
                    }
                    last_row.cells[4].lastChild.value = ms_width;
                    last_row.cells[5].lastChild.readOnly = false;

                }
                last_row.cells[11].lastChild.placeholder="No.s/packet";
                last_row.cells[12].lastChild.placeholder="No. of packets";
            }
	}


    // Fields like packing type, no of packets and no.s / packet disabled or enabled based on FG or WIP selected
    function fg_or_no_fg(th,tableID)
    {
		    var table = document.getElementById(tableID);

			var rowCount = th.parentNode.parentNode.rowIndex;

			var last_row = document.getElementById(tableID).rows[rowCount];

            var answer = last_row.cells[10].lastElementChild.value;
            var operation = last_row.cells[1].lastElementChild.value;
            fg_wt = Number(document.getElementById("total_fg").value);
            var process_weight = Number(document.getElementById("processing_wt").value);
            var total_fg = 0;


		    if(answer == "FG" )
		    {

                last_row.cells[11].lastChild.readOnly = false;
                last_row.cells[12].lastChild.readOnly = false;
                last_row.cells[13].lastChild.readOnly = false;
                output_wt = Number(last_row.cells[6].lastElementChild.value);
                total_fg = (fg_wt + output_wt).toFixed(3)
                document.getElementById("total_fg").value = total_fg;
            }
            else
            {
                if(operation != "Slitting" && operation != "Mini Slitting"){
                    last_row.cells[11].lastChild.readOnly = true;
                    last_row.cells[11].lastChild.value = "0"
                    last_row.cells[12].lastChild.readOnly = true;
                    last_row.cells[12].lastChild.value = "0"
                    last_row.cells[13].lastChild.readOnly = true;
                }
                if(operation == "Slitting" || operation == "Mini Slitting"){
                    last_row.cells[11].lastChild.readOnly = false;
                    last_row.cells[12].lastChild.readOnly = false;
                }
		        last_row.cells[13].lastChild.placeholder = "Packing"
		        last_row.cells[13].lastChild.value = " "

            }
    }


    // numbers or length calculated after weight entered
    function calculate_numbers(th, tableID){
           var table = document.getElementById(tableID);

			var rowCount = th.parentNode.parentNode.rowIndex;

			var last_row = document.getElementById(tableID).rows[rowCount];

            var weight = Number(last_row.cells[6].lastChild.value);
            var cut_length = Number(last_row.cells[5].lastChild.value);
            var cut_width = Number(last_row.cells[4].lastChild.value);
            var thickness = Number(document.getElementById("thickness").value);

            var answer = last_row.cells[1].lastElementChild.value;
            var numbers = 0;

            if (answer == "Slitting" || answer == "Mini Slitting"){
                //numbers =  (weight*1000/(cut_width * thickness)/0.00000785)/1000;
            }
            else{
                if (answer == "Reshearing")
                {
                   var input_material = (last_row.cells[3].lastElementChild.value).split(" x ");
                    ms_width = input_material[0];
                    ms_length = input_material[1];
                    if (ms_width==0 || ms_length==0)
                     {
                        alert("Please check input material for reshearing")
                        return false;
                     }
                }
                numbers = weight*1000/(cut_length * cut_width * thickness)/0.00000785;
            }

            last_row.cells[7].lastChild.value = numbers.toFixed(0);
            return true;

    }






    // No of packets calculated based on no.s per packet and total numbers selected
    function calculate_no_of_packets(th, tableID){
            var table = document.getElementById(tableID);

		    var rowCount = th.parentNode.parentNode.rowIndex;
		    var last_row = document.getElementById(tableID).rows[rowCount];
            var answer = last_row.cells[1].lastElementChild.value;

            var weight = Number(last_row.cells[6].lastChild.value);
            var cut_length = Number(last_row.cells[5].lastChild.value);
            var cut_width = Number(last_row.cells[4].lastChild.value);
            var thickness = Number(document.getElementById("thickness").value);
            var input_material = (last_row.cells[3].lastElementChild.value).split(" x ");
            ms_width = Number(input_material[0]);
            ms_length = input_material[1];

            var coil_length = 0;
            var length_per_part = 0
            var no_of_parts = Number(last_row.cells[11].lastChild.value);



            if (answer == "Slitting" || answer == "Mini Slitting"){
                var no_of_slits = Number(last_row.cells[7].lastChild.value);
                var weight_per_coil = weight/no_of_slits;
                coil_length = (weight_per_coil * 1000)/(thickness * cut_width * 0.00000785)/1000;
                length_per_part = coil_length/no_of_parts;
                last_row.cells[12].lastChild.value = length_per_part.toFixed(2);
            }

            else{
                if (last_row.cells[10].lastElementChild.value == "FG"){
                var numbers = Number(last_row.cells[7].lastChild.value);
                var no_per_packet = Number(last_row.cells[11].lastChild.value);
                var no_of_packets = numbers / no_per_packet;
                last_row.cells[12].lastChild.value = no_of_packets.toFixed(0);
                }
            }
    }

    function check_stage_weight(tableID)
    {
        var table = document.getElementById(tableID);
		var rowCount = table.rows.length;
		var current_row = document.getElementById(tableID).rows[0];
		var stage_weight = [0];
		var stage_number = 0;
		var mother_weight = Number(document.getElementById("processing_wt").value);
		var fg_wt = 0;


		for(i=1;i<rowCount;i++)
		{
		   current_row = document.getElementById(tableID).rows[i];
		   stage_number = parseInt(current_row.cells[2].lastChild.value);
		   if(stage_weight[stage_number])
		    stage_weight[stage_number] += Number(current_row.cells[6].lastChild.value);
           else
            stage_weight[stage_number] = Number(current_row.cells[6].lastChild.value);
           if(current_row.cells[10].lastElementChild.value == "FG")
            fg_wt += Number(current_row.cells[6].lastChild.value);
      	}
        document.getElementById("total_fg").value = fg_wt;

      	for(i=1;i<=stage_weight.length;i++)
      	{
      	    if(stage_weight[i]>mother_weight)
      	    {
      	        alert("The processing weight of stage "+ i + " is greater than processing weight. Please re-check");
      	        return false;
      	    }
      	}

    }

    function validate_form(tableID){
         var fg_return_value = true;
         var stage_wt_return_value =  check_stage_weight(tableID);

         var fg_wt = Number(document.getElementById("total_fg").value);
         var process_weight = Number(document.getElementById("processing_wt").value);
         // This is to check that FG cannot be greater than processing weight entered
         if (fg_wt > process_weight)
         {
              alert("Total FG greater than processing weight. Please check");
              fg_return_value =  false;
         }

         // This is to check that FG and processing weight * 95% match
         if (fg_wt < (0.95*process_weight))
         {
                alert("Total FG is less than processing weight. Please check");
                fg_return_value = false;
         }

         var order_date = new Date(document.getElementById("order_date").value);
         var expected_date = new Date(document.getElementById("expected_date").value);
         var date_check = true;

         if (order_date>expected_date)
         {
            date_check = false;
            alert("Order date cannot be greater than expected date!");
         }

         if (fg_return_value == false || stage_wt_return_value == false || date_check == false)
            return false;
         else
            return true;
    }



    function select_operation(operation){
        switch(operation){
        case "ctl":
            document.getElementById('operation').selectedIndex = "0";
            break;
        case "ctl_single_lami":
            document.getElementById('operation').selectedIndex = "1";
            break;
        case "ctl_double_lami":
            document.getElementById('operation').selectedIndex = "2";
            break;
        case "slitting":
            document.getElementById('operation').selectedIndex = "3";
            break;
        case "mini_slitting":
            document.getElementById('operation').selectedIndex = "4";
            break;
        case "nctl":
            document.getElementById('operation').selectedIndex = "5";
            break;
        case "reshearing":
            document.getElementById('operation').selectedIndex = "6";
        }
    }*/