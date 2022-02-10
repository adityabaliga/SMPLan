from decimal import Decimal
from flask_login import LoginManager, login_user, current_user, logout_user
from file_uploader import FileUploader
from flask import Flask, render_template, request, Markup

from user import User
from current_stock import CurrentStock
from incoming import Incoming
from order import Order
from order_detail import OrderDetail
from processing import Processing
from processing_detail import ProcessingDetail
from slitter_usage import SlitterUsage
from dispatch_header import DispatchHeader
from dispatch_detail import DispatchDetail
from slitter_batch import SlitterBatch
import time


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)


# Clicking on http://127.0.0.1:5000/ (the home page), this will redirect you to login page
@app.route('/')
def home(message=""):
    return render_template('/home.html', message=message)


@login_manager.user_loader
def user_loader(username):
    return User.get(username)


# Login page. Authenticates user and then proceeds
# Sources for login and logout functions
# http://gouthamanbalaraman.com/blog/minimal-flask-login-example.html
# https://realpython.com/blog/python/using-flask-login-for-user-management-with-flask/
# https://flask-login.readthedocs.io/en/latest/#flask_login.LoginManager
@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        pwd = request.form['password']
    else:
        username = request.args.get('username')
        pwd = request.args.get('password')
    user = User.get(username)
    if pwd == user.password:
        login_user(user, remember=True)
        return render_template('/main_menu.html')
    else:
        return render_template('/unsuccessful_login.html')


# This is for the user to logout. Redirects back to the login page
@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return render_template('/home.html')


# Main Menu page. Once logged in, the user will always come back to this after his operations done
@app.route('/main_menu')
def main_menu(message=""):
    user = current_user
    try:
        if user.username is not None:
            return render_template('/main_menu.html', current_user=user, message=message)
    # In case the user is not logged in => no username is detected, the user cannot reach the main menu page and is
    # redirected to the login page
    except AttributeError:
        return render_template('/home.html', message="Please login first")


# If login fail, will be redirected to login page with message
@app.route('/unsuccessful_login')
def unsuccessful_login():
    return render_template('/home.html', message="Wrong details! Please retry!")


# This is to load the change password page. The message returned if old password is incorrect
@app.route('/change_password_form')
def change_password_form(message=""):
    return render_template('/change_password.html', message=message)


# Change password on submit. Checks if old password is correct and then updates user with new password
@app.route('/change_pwd', methods=['POST', 'GET'])
def change_pwd():
    if request.method == 'POST':
        old_pwd = request.form['old_password']
        new_pwd = request.form['new_password']

    else:
        old_pwd = request.args.get('username')
        new_pwd = request.args.get('new_password')

    user = current_user
    user = User.get(user.username)
    if old_pwd == user.password:
        user.update_pwd(new_pwd)
    else:
        return render_template('/change_password.html', message="Password is incorrect. Please re-enter details")
    logout_user()
    return render_template('/home.html', message="Please login again")

@app.route('/change_unit', methods=['GET', 'POST'])
def change_unit():
    unit = ""
    if request.method == 'POST':
        unit = request.form['unit']

    if request.method == 'GET':
        unit = request.args.get('unit')

    user = current_user
    if unit == '1':
        current_user.unit = 1
    if user == '2':
        current_user.unit = 2

    return render_template('/main_menu.html')


# This is for incoming of smpl coil. The details are got from the xml file generated from Tally.
# The filename is to be entered here
@app.route('/incoming_input_smpl', methods=['GET', 'POST'])
def incoming_input_smpl():
    return render_template('/incoming_enter_xml.html')


# This is for incoming of TR coil.
@app.route('/incoming_input_tr', methods=['GET', 'POST'])
def incoming_input_tr():
    return render_template('/incoming_for_tr.html')


# XML filename to be entered. After filename given, a table is generated with all the details populated in
#  incoming_review_after_upload_form.html. The user gets a chance to review the details and enter remarks, if any.
@app.route('/smpl_incoming', methods=['GET', 'POST'])
def smpl_incoming():

    if request.method == 'POST':
        
        xml_filename = request.files['xml_filename']

    else:
        xml_filename = request.args.get('xml_filename')

    incoming_lst = Incoming.fromfile(xml_filename)
    # The details got from the XML file are updated to the database. The details are displayed for review and if any
    # remarks are to be entered
    for incoming_coil in incoming_lst:
        incoming_coil.savetodb()
    return render_template('incoming_review_after_upload_form.html', incoming_lst=incoming_lst)


# The remarks are recovered. SMPL No is made a hidden field in the HTML to map the remarks and the SMPL
# This is then updated to the DB and then redirects to the main menu
@app.route('/submit_smpl_incoming', methods=['GET', 'POST'])
def submit_smpl_incoming():
    incoming_remarks = []
    smpl_nos = []
    if request.method == 'POST':
        incoming_remarks = request.form.getlist('remarks')
        smpl_nos = request.form.getlist('smpl_nos')
    for remark, smpl_no in zip(incoming_remarks, smpl_nos):
        Incoming.update_remarks_by_smpl_no(remark, smpl_no)

    if request.method == 'GET':
        pass
    return render_template('/main_menu.html', message="Incoming details updated")


# This will take details for TR coils that are entered manually and then commits to DB
@app.route('/tr_incoming_commit', methods=['GET', 'POST'])
def tr_incoming_commit():
    smpl_no = ""
    if request.method == 'POST':
        tr_prefix = request.form['tr_prefix']
        smpl_no = tr_prefix + request.form['smpl_no']
        smpl_no = smpl_no.replace(" ", "")
        customer = request.form['customer']
        incoming_date = request.form['incoming_date']
        thickness = Decimal(request.form['thickness'])
        width = Decimal(request.form['width'])
        length = (request.form['length'])
        material_type = request.form['material_type']
        interal_dia = request.form['internal_dia']
        grade = request.form['grade']
        final_grade = material_type + '. ID:' + interal_dia + '. GRADE: ' + grade
        weight = Decimal(request.form['weight'])
        numbers = int((request.form['numbers']))
        mill = request.form['mill']
        mill_id = request.form['mill_id']
        incoming_remarks = request.form['remarks']
        unit = request.form['unit']
        _incoming = Incoming(smpl_no, customer, incoming_date, thickness, width, length, final_grade, weight, numbers, mill,
                             mill_id, incoming_remarks, unit)
        _incoming.savetodb()

    return render_template('/main_menu.html', message="Incoming details for " + smpl_no + " entered.")


# This function is to place raw material on hold. A list is obtained from current_stock table and displayed.
# The user has to pick from this list
@app.route('/rm_onhold', methods=['GET', 'POST'])
def rm_onhold():
    cs_return_lst = CurrentStock.rm_list_for_hold()
    cs_obj_lst = []
    cs_id_lst = []

    for cs_id, cs in cs_return_lst:
        cs_id_lst.append(cs_id)
        cs_obj_lst.append(cs)

    if cs_obj_lst:
        return render_template('rm_on_hold_pick_smpl.html', cs_lst=zip(cs_id_lst, cs_obj_lst))
    else:
        return render_template('/main_menu.html', message="No raw material available to put on hold")


# Once the RM to be placed on hold is selected. The status in current_stock is updated to RM - On Hold. With remarks
#  updated in Incoming
@app.route('/put_on_hold', methods=['GET', 'POST'])
def put_on_hold():
    hold_remarks = ""
    smpl = ""
    if request.method == 'POST':
        smpl = request.form['select_smpl']
        hold_remarks = request.form['remarks']

    if request.method == 'GET':
        smpl = request.args.get('select_smpl')
        hold_remarks = request.args.get('remarks')

    smpl_details = smpl.split(',')
    smpl_no = smpl_details[1]
    cs_id = smpl_details[0]
    CurrentStock.update_status_cls(cs_id, "RM - On Hold")
    hold_remarks = " Put hold because " + hold_remarks + " on " + time.strftime("%d/%m/%Y")
    Incoming.update_remarks(hold_remarks, smpl_no)
    return render_template('/main_menu.html', message=smpl_no + " placed on hold")


# This function is to unhold the raw material. The list of rm which is currently on hold is displayed
@app.route('/rm_unhold', methods=['GET', 'POST'])
def rm_unhold():
    cs_return_lst = CurrentStock.rm_list_for_unhold()
    cs_obj_lst = []
    cs_id_lst = []

    for cs_id, cs in cs_return_lst:
        cs_id_lst.append(cs_id)
        cs_obj_lst.append(cs)
    if cs_obj_lst:
        return render_template('rm_undo_hold.html', cs_lst=zip(cs_id_lst, cs_obj_lst))
    else:
        return render_template('/main_menu.html', message="No raw material is currently on hold")


# The selected SMPL in removed from hold. The remarks are updated in incoming table.
@app.route('/put_on_unhold', methods=['GET', 'POST'])
def put_on_unhold():
    unhold_remarks = ""
    smpl = ""
    if request.method == 'POST':
        smpl = request.form['select_smpl']
        unhold_remarks = request.form['remarks']

    if request.method == 'GET':
        smpl = request.args.get('select_smpl')
        unhold_remarks = request.args.get('remarks')

    smpl_details = smpl.split(',')
    smpl_no = smpl_details[1]
    cs_id = smpl_details[0]
    CurrentStock.update_status_cls(cs_id, "RM")
    unhold_remarks = " Removed from hold because " + unhold_remarks + " on " + time.strftime("%d/%m/%Y")
    Incoming.update_remarks(unhold_remarks, smpl_no)
    return render_template('/main_menu.html')


# In this function, the user can select the smpl to be transferred to the other unit.

@app.route('/transfer_material', methods=['GET', 'POST'])
def transfer_material():
    if current_user.unit == 1 or current_user.unit == 2:
        cs_return_lst = CurrentStock.get_stock('All', current_user.unit)
    else:
        return render_template('/transfer_pick_unit.html', stock_type='All')

    cs_obj_lst = []
    cs_id_lst = []

    for cs_id, cs in cs_return_lst:
        cs_id_lst.append(cs_id)
        cs_obj_lst.append(cs)

    if cs_obj_lst:
        return render_template('transfer_material.html', cs_lst=zip(cs_id_lst, cs_obj_lst))
    else:
        return render_template('/main_menu.html', message="No Raw material to transfer")


@app.route('/transfer_pick_unit', methods=['GET', 'POST'])
def transfer_pick_unit():
    stock_type = ""
    unit = ""
    if request.method == 'POST':
        unit = request.form['select_unit']
        stock_type = request.form['stock_type']
    if request.method == 'GET':
        unit = request.args.get('select_unit')
        stock_type = request.args.get('stock_type')

    cs_return_lst = CurrentStock.get_stock(stock_type,unit)

    cs_obj_lst = []
    cs_id_lst = []

    for cs_id, cs in cs_return_lst:
        cs_id_lst.append(cs_id)
        cs_obj_lst.append(cs)

    if cs_obj_lst:
        return render_template('transfer_material.html', cs_lst=zip(cs_id_lst, cs_obj_lst), unit = unit)
    else:
        return render_template('/main_menu.html', message="No Raw material to transfer")


# On selection and submit, the unit is changed in current_stock and remarks are updated in incoming about the transfer
# and when it was transferred
@app.route('/transfer_submit', methods=['GET', 'POST'])
def transfer_submit():
    smpl = ""
    unit = ""
    transfer_remarks = ""
    if request.method == 'POST':
        smpl = request.form['select_smpl']
        unit = request.form['unit']
        transfer_remarks = request.form['remarks']

    if request.method == 'GET':
        smpl = request.args.get('select_smpl')
        unit = request.args.get('unit')
        transfer_remarks = request.args.get('remarks')

    smpl_details = smpl.split(',')
    smpl_no = smpl_details[1]
    cs_id = smpl_details[0]
    CurrentStock.transfer_material_cls(cs_id, unit)
    transfer_remarks = " Transferred to Unit " + unit + " for " + transfer_remarks + " on " + time.strftime("%d/%m/%Y")
    Incoming.update_remarks(transfer_remarks, smpl_no)
    return render_template('/main_menu.html')


# pick smpl for uploading documents
@app.route('/upload_pick_smpl', methods=['GET', 'POST'])
def upload_pick_smpl(message=""):
    return render_template('/upload_pick_smpl.html', message=message)


# Check if entered SMPL for uploading documents exist and then forward to uploading page
@app.route('/upload_pick_smpl_submit', methods=['GET', 'POST'])
def upload_smpl_submit():
    smpl_no = ""
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']
    if request.method == 'GET':
        smpl_no = request.args.get('smpl_no')

    smpl_no = smpl_no.replace(" ", "")
    incoming = Incoming.load_smpl_by_smpl_no(smpl_no)

    if incoming:
        return render_template('/upload_documents.html', incoming=incoming)

    else:
        return render_template('/upload_pick_smpl.html', message="SMPL no. does not exist. Please re-check")


@app.route('/upload_docs_submit', methods=['GET', 'POST'])
def upload_docs_submit():
    return_file_list = ""
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']
        if 'cust_order_files[]' in request.files:
            files = request.files.getlist("cust_order_files[]")
            file_type = "cust_order"
            return_file_list += FileUploader.upload_files(smpl_no, file_type, files)
        if 'smpl_order_files[]' in request.files:
            files = request.files.getlist("smpl_order_files[]")
            file_type = "smpl_order"
            return_file_list += FileUploader.upload_files(smpl_no, file_type, files)
        if 'prod_rprt_files[]' in request.files:
            files = request.files.getlist("prod_rprt_files[]")
            file_type = "prod_rprt"
            return_file_list += FileUploader.upload_files(smpl_no, file_type, files)

    if len(return_file_list) > 1:
        return render_template('/upload_pick_smpl.html', message="These files were not uploaded. Please check the file "
                                                                 "extension and retry" + return_file_list)
    else:
        return render_template('/main_menu.html', message='Files uploaded successfully')


# A smpl list is got whose status is RM. The list is sent to the html
@app.route('/smpl_for_order', methods=['GET', 'POST'])
def smpl_for_order():
    smpl_lst = CurrentStock.smpl_list_for_place_order('SMPL')
    if smpl_lst:
        return render_template('order_pick_smpl.html', smpl_lst=smpl_lst)
    else:
        return render_template('/main_menu.html', message="No material to place order")


# A smpl list is got whose status is RM. The list is sent to the html
@app.route('/tr_for_order', methods=['GET', 'POST'])
def tr_for_order():
    smpl_lst = CurrentStock.smpl_list_for_place_order('TR')
    if smpl_lst:
        return render_template('order_pick_smpl.html', smpl_lst=smpl_lst)
    else:
        return render_template('/main_menu.html', message="No material to place order")


# Loaded from order_pick_smpl.html
# the smpl_no is retrieved from the page. The details of the smpl_no are loaded from the db and details sent to order.html
@app.route('/order', methods=['GET', 'POST'])
def order():
    smpl_no = ""
    if request.method == 'POST':
        smpl_no = request.form['select_smpl']

    if request.method == 'GET':
        smpl_no = request.args.get('select_smpl')
    incoming = Incoming.load_smpl_by_smpl_no(smpl_no)
    current_stock = CurrentStock.load_smpl_by_smplno(smpl_no, incoming.length, incoming.width)
    for cs_id, _current_stock in current_stock:
        cs = _current_stock

    return render_template('order.html', smpl_no=smpl_no, customer=incoming.customer, thickness=incoming.thickness,
                           width=incoming.width, length=incoming.length, grade=incoming.grade,
                           weight=cs.weight , numbers=incoming.numbers)


# from order.html. The details retrieved from the page and loaded to db in to order and order_detail
@app.route('/submit_order', methods=['GET', 'POST'])
def submit_order():
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']

        order_date = request.form['order_date']
        expected_date = request.form['expected_date']
        processing_wt = request.form['processing_wt']
        available_wt = request.form['available_wt']
        customer = request.form['customer']
        available_numbers = request.form['available_numbers']
        thickness = request.form['thickness']
        width = request.form['width']
        length = request.form['length']
        grade = request.form['grade']
        header_remarks = request.form['hdr_remarks']
        order_string = request.form['order_string']

        order_string_lst = order_string.split('^')

        '''ms_width_lst = []
        ms_length_lst = []
        operation_lst = request.form.getlist('Reshearing_table')
        input_material_lst = request.form.getlist('input_material')
        cut_width_lst = request.form.getlist('cut_width')
        cut_length_lst = request.form.getlist('cut_length')
        processing_wt_op_lst = request.form.getlist('weight')
        numbers_lst = request.form.getlist('numbers')
        positive_tolerance_lst = request.form.getlist('positive_tolerance')
        negative_tolerance_lst = request.form.getlist('negative_tolerance')
        fg_yes_no_lst = request.form.getlist('fg_yes_no')
        no_per_packet_lst = request.form.getlist('no_per_packet')
        no_of_packets_lst = request.form.getlist('no_of_packets')
        packing_type_lst = request.form.getlist('packing_type')
        remarks_lst = request.form.getlist('remarks')
        stage_no_lst = request.form.getlist('stage_no')'''


    # This is saved to order_header. The id generated is retrieved for order_detail
    order = Order(smpl_no, order_date, expected_date, processing_wt, "Open",header_remarks)
    _order_id = order.save_to_db()

    '''for input_material in input_material_lst:
        mother_material = input_material.split(' x ')
        ms_width_lst.append(mother_material[0])
        ms_length_lst.append(mother_material[1])

    for _operation, ms_width, ms_length, cut_width, cut_length, processing_wt_op, numbers, fg_yes_no, no_per_packet, no_of_packets, packing_type, remarks, stage_no, positive_tolerance, negative_tolerance in zip(
            operation_lst, ms_width_lst, ms_length_lst, cut_width_lst, cut_length_lst, processing_wt_op_lst,
            numbers_lst, fg_yes_no_lst, no_per_packet_lst, no_of_packets_lst, packing_type_lst, remarks_lst,
            stage_no_lst, positive_tolerance_lst, negative_tolerance_lst):'''
    for order_str in order_string_lst:
        # Status of stage 1 has to be in Ready so it can be picked up for processing.
        # The other stages are marked as not ready
        order_dtl_str = order_str.split(',')
        if len(order_dtl_str) > 16:
            _operation = order_dtl_str[0]
            stage_no = order_dtl_str[1]
            ms_width = order_dtl_str[2]
            ms_length = order_dtl_str[3]
            fg_yes_no = order_dtl_str[4]
            cut_width = order_dtl_str[5]
            cut_length = order_dtl_str[6]
            lamination = order_dtl_str[7]
            tolerance = order_dtl_str[8]
            internal_dia = order_dtl_str[9]
            processing_wt_op = order_dtl_str[10]
            wt_per_pkt = order_dtl_str[11]
            numbers = order_dtl_str[12]
            no_per_packet = order_dtl_str[14]
            no_of_packets = order_dtl_str[13]
            packing_type = order_dtl_str[15]
            remarks = order_dtl_str[16]




            if stage_no == '1':
                status = "Ready"
            else:
                status = "Not Ready"

            order_detail = OrderDetail(_order_id, smpl_no, _operation, ms_width, ms_length, cut_width, cut_length,
                                       processing_wt_op, numbers, fg_yes_no, no_per_packet, no_of_packets, packing_type,
                                       remarks, status, stage_no, tolerance, lamination, wt_per_pkt, internal_dia)
            order_detail.save_to_db()

    # This part is for half cut.
    # If the processing weight is less than available weight. It is assumed that the coil is going to be half cut.
    # The half cut coil is given a new smpl no. which is old smpl_no +_H. The wt and no.s for the half cut coil are calculated
    # This is then added to incoming with the same details of the mother coil and new smpl_no
    if Decimal(processing_wt) < Decimal(available_wt):
        new_wt = Decimal(available_wt) - Decimal(processing_wt)
        if Decimal(length) > 0:
            new_nos = int(new_wt / (thickness * width * length * 0.00000785))
        if Decimal(length) == 0:
            new_nos = 1
        new_smpl_no = smpl_no + "_H"
        incoming = Incoming.load_smpl_by_smpl_no(smpl_no)
        incoming_new = Incoming(new_smpl_no,customer,incoming.incoming_date,thickness,width,length,grade,new_wt,new_nos,
                                incoming.mill,incoming.mill_id,incoming.remarks, incoming.unit)
        incoming_new.savetodb()
        rm_status = CurrentStock.change_wt(smpl_no, width, length, new_wt, new_nos, "minus")


    # The status of the smpl is updated in current_stock
    cs = CurrentStock(smpl_no, customer, available_wt, available_numbers, thickness, width, length, "RM", grade,"X")
    cs.update_status("Order")

    return render_template('/main_menu.html', message="Order for " + smpl_no + " created.")


@app.route('/print_order', methods=['GET', 'POST'])
def print_order():
    print_order_string = request.query_string
    print_order_string = print_order_string.decode("utf-8")
    print_order_string = print_order_string.replace('%20', ' ')

    temp_print_order_lst = print_order_string.split('=')
    temp_print_order_string = temp_print_order_lst[1]
    print_order_lst = temp_print_order_string.split(',')


    return render_template('/print_order.html', smpl_no = temp_print_order_string)



# Select smpl for modifying the order from current_stock where the status is Order
@app.route('/smpl_for_modify_order', methods=['GET', 'POST'])
def smpl_for_modify_order():
    smpl_lst = CurrentStock.smpl_list_for_modify_order()
    if smpl_lst:
        return render_template('order_pick_smpl_for_view_delete.html', smpl_lst=smpl_lst)
    else:
        return render_template('/main_menu.html', message="No open orders for modification")


@app.route('/view_order', methods=['GET', 'POST'])
def view_order():
    smpl_no = ""
    order_detail_lst = []
    order_lst = []
    _order_detail_lst = []
    order_detail_for_print_lst = []
    order_detail_by_stage_and_op_lst = []
    operation_lst = []
    ms_lst = []
    proc_wt_lst = []
    stage_no_lst = []

    if request.method == 'POST':
        smpl_no = request.form['select_smpl']

    if request.method == 'GET':
        smpl_no = request.args.get('select_smpl')

    incoming = Incoming.load_smpl_by_smpl_no(smpl_no)
    order_lst = Order.history_load_from_db(smpl_no)

    for order_id, _order in order_lst:
        _order_detail_lst = OrderDetail.load_from_db(smpl_no,order_id)
        order = _order

    for order_detail_id, order_detail in _order_detail_lst:
        order_detail_lst.append(order_detail)


    i=0
    while len(order_detail_lst) >0:
        operation = order_detail_lst[i].operation
        stage_no = order_detail_lst[i].stage_no
        # order_detail_by_stage_and_op_lst.append(order_detail)
        ms = str(order_detail_lst[i].ms_width) + " x " + str(order_detail_lst[i].ms_length)
        proc_wt = 0
        for order_detail2 in order_detail_lst:
            if order_detail2.operation == operation and stage_no == order_detail2.stage_no:
                order_detail_by_stage_and_op_lst.append(order_detail2)
                proc_wt += order_detail2.processing_wt
                # order_detail_lst.remove(order_detail2)
        order_detail_for_print_lst.append(order_detail_by_stage_and_op_lst)
        operation_lst.append(operation)
        stage_no_lst.append(stage_no)
        ms_lst.append(ms)
        proc_wt_lst.append(proc_wt)
        for order_detail3 in order_detail_by_stage_and_op_lst:
            order_detail_lst.remove(order_detail3)
        order_detail_by_stage_and_op_lst = []


    return render_template('view_order.html', smpl_no=smpl_no, customer=incoming.customer, thickness=incoming.thickness,
                           width=incoming.width, length=incoming.length, grade=incoming.grade,
                           weight=incoming.weight, numbers=incoming.numbers, order=order,
                           order_detail_lst=zip(order_detail_for_print_lst, operation_lst, ms_lst,proc_wt_lst, stage_no_lst))


# To load orders by machine to chose for processing
@app.route('/orders_by_machine', methods=['GET', 'POST'])
def orders_by_machine():
    operation = ""
    customer_type = ""
    cs_id_lst = []
    cs_lst = []
    if request.method == 'POST':
        operation = request.form['select_operation']
        customer_type =  request.form['type']

    if request.method == 'GET':
        operation = request.args.get('select_operation')
        customer_type = request.args.get('type')

    if current_user.unit == 1 or current_user.unit == 2:
        smpl_for_processing_lst = CurrentStock.smpl_list_for_processing(operation, customer_type, str(current_user.unit))
        for cs_id, cs in smpl_for_processing_lst:
            cs_lst.append(cs)
            cs_id_lst.append(cs_id)
        '''order_detail_lst = OrderDetail.smpl_lst_by_operation("Ready", operation, customer_type, )
        cs_lst = []
        order_return_lst = []
        expected_date_lst = []
        _cs_lst = []
        cs_id_lst = []
        for order_detail in order_detail_lst:
            _cs_lst = CurrentStock.load_smpl_by_smplno(order_detail.smpl_no, order_detail.ms_length,
                                                       order_detail.ms_width)
            for cs_id, cs in _cs_lst:
                if str(cs.unit) == str(current_user.unit):
                    cs_lst.append(cs)
                    cs_id_lst.append(cs_id)
            # cs_lst.append(
                #   CurrentStock.load_smpl_by_smplno(order_detail.smpl_no, order_detail.ms_length, order_detail.ms_width))
            # order_return_lst = Order.load_from_db(order_detail.smpl_no, "Open")
            # Expected date got from order and displayed in dd/mm/YYYY format
            # for order_id, order in order_return_lst:
            #    expected_date_lst.append(order.expected_date.strftime('%d/%m/%Y'))

        # This list are which are in Not ready state. This is to indicate the total pressure that is there on the machine
        # order_detail_not_ready_list = OrderDetail.smpl_lst_by_operation("Not Ready", operation)
        cs_not_ready_lst = []
        order_not_ready_lst = []
        expected_date_for_not_ready_lst = []
        for order_detail in order_detail_not_ready_list:
            cs = CurrentStock.load_smpl_by_smplno(order_detail.smpl_no, order_detail.ms_length, order_detail.ms_width)
            if str(cs.unit) == str(current_user.unit):
                cs_not_ready_lst.append()
            # cs_not_ready_lst.append(
            #   CurrentStock.load_smpl_by_smplno(order_detail.smpl_no, order_detail.ms_length, order_detail.ms_width))
            order_not_ready_lst = Order.load_from_db(order_detail.smpl_no, "Open")
            for order_id, _order in order_not_ready_lst:
                expected_date_for_not_ready_lst.append(_order.expected_date.strftime('%d/%m/%Y'))'''

    if current_user.unit == 0:
        return render_template('/processing_pick_unit.html', operation=operation, type = customer_type)


    if cs_lst:
        return render_template('processing_pick_smpl.html', cs_lst=zip(cs_id_lst, cs_lst), operation=operation)
    else:
        return render_template('/main_menu.html', message="No raw material or WIP available!")


@app.route('/processing_pick_unit', methods=['GET', 'POST'])
def processing_pick_unit():
    operation = ""
    unit = ""
    customer_type = ""
    if request.method == 'POST':
        unit = request.form['select_unit']
        operation = request.form['operation']
        customer_type = request.form['type']
    if request.method == 'GET':
        unit = request.args.get('select_unit')
        operation = request.args.get('operation')
        customer_type = request.args.get('type')
    # order_detail_lst = OrderDetail.smpl_lst_by_operation("Ready", operation)

    cs_lst=[]
    cs_id_lst=[]
    smpl_for_processing_lst = CurrentStock.smpl_list_for_processing(operation, customer_type, unit)
    for cs_id, cs in smpl_for_processing_lst:
        cs_lst.append(cs)
        cs_id_lst.append(cs_id)

    '''for order_detail in order_detail_lst:
        #cs_lst.append(CurrentStock.load_smpl_by_smplno(order_detail.smpl_no, order_detail.ms_length, order_detail.ms_width))
        _cs_lst = CurrentStock.load_smpl_by_smplno(order_detail.smpl_no, order_detail.ms_length, order_detail.ms_width)
        for cs_id, cs in _cs_lst:
            if str(cs.unit) == str(unit):
                cs_lst.append(cs)
                cs_id_lst.append(cs_id)

        # order_return_lst = Order.load_from_db(order_detail.smpl_no, "Open")
        # Expected date got from order and displayed in dd/mm/YYYY format
        # for order_id, order in order_return_lst:
         #   expected_date_lst.append(order.expected_date.strftime('%d/%m/%Y'))

    # This list are which are in Not ready state. This is to indicate the total pressure that is there on the machine
    # order_detail_not_ready_list = OrderDetail.smpl_lst_by_operation("Not Ready", operation)
    _cs_not_ready_lst = []
    cs_id_not_ready_lst = []
    cs_not_ready_lst = []
    order_not_ready_lst = []
    expected_date_for_not_ready_lst = []
    for order_detail in order_detail_not_ready_list:
        _cs_not_ready_lst = CurrentStock.load_smpl_by_smplno(order_detail.smpl_no, order_detail.ms_length,
                                                             order_detail.ms_width)
        for cs_id, cs in _cs_not_ready_lst:
            cs_id_not_ready_lst.append(cs_id)
            cs_not_ready_lst.append(cs)
        order_not_ready_lst = Order.load_from_db(order_detail.smpl_no, "Open")
        for order_id, _order in order_not_ready_lst:
            expected_date_for_not_ready_lst.append(_order.expected_date.strftime('%d/%m/%Y'))'''

    if cs_lst:
        return render_template('processing_pick_smpl.html', cs_lst=zip(cs_id_lst,cs_lst), operation=operation)
    else:
        return render_template('/main_menu.html', message="No raw material or WIP available!")


@app.route('/processing_search', methods=['GET', 'POST'])
def processing_search():
    operation=""
    return render_template('/processing_search.html')


@app.route('/processing_search_list', methods=['GET', 'POST'])
def processing_search_list():
    operation = ""
    smpl_no = ""
    cs_id_lst = []
    cs_lst = []
    if request.method == 'POST':
        operation = request.form['select_operation']
        smpl_no = request.form['smpl_no']

    if request.method == 'GET':
        operation = request.args.get('select_operation')
        smpl_no = request.args.get('smpl_no')


    smpl_for_processing_search_lst = CurrentStock.smpl_for_processing_search_lst(operation, smpl_no,str(current_user.unit))

    if smpl_for_processing_search_lst:
        for cs_id, cs in smpl_for_processing_search_lst:
            cs_lst.append(cs)
            cs_id_lst.append(cs_id)

        return render_template('processing_pick_smpl.html', cs_lst=zip(cs_id_lst,cs_lst), operation=operation)

    else:
        return render_template('/main_menu.html', message="No raw material or WIP available!")

# Function to load details of raw material and order for the smpl selected
@app.route('/processing_load', methods=['GET', 'POST'])
def processing_load():
    operation = ""
    cs_rm_id = ""
    if request.method == 'POST':
        cs_rm_id = request.form['select_smpl']
        operation = request.form['operation']
    if request.method == 'GET':
        cs_rm_id = request.args.get('select_smpl')
        operation = request.args.get('operation')

    cs_rm = CurrentStock.load_smpl_by_id(cs_rm_id)
    incoming = Incoming.load_smpl_by_smpl_no(cs_rm.smpl_no)

    processing_detail_lst = ProcessingDetail.load_from_db(cs_rm.smpl_no, operation)

    '''order_return_lst = Order.load_from_db(smpl_no=cs_rm.smpl_no, status="Open")
    order_id_lst = []
    order_lst = []
    for order_id, order in order_return_lst:
        order_id_lst.append(order_id)
        order_lst.append(order)

    order_id = order_id_lst[0]
    order = order_lst[0]
    numbers = 0
    _scrap = 0
    order_detail_lst = OrderDetail.load_from_db(cs_rm.smpl_no, order_id)

    order_detail_lst_by_operation = []
    order_detail_id_lst_by_operation = []
    total_order_wt = 0
    for order_detail_id, order_detail in order_detail_lst:
        if order_detail.operation.startswith(operation) and order_detail.status == 'Ready' and order_detail.ms_width == cs_rm.width and order_detail.ms_length == cs_rm.length:
            order_detail_lst_by_operation.append(order_detail)
            order_detail_id_lst_by_operation.append(order_detail_id)
            numbers += order_detail.numbers
            stage_no = order_detail.stage_no
            ms_width = order_detail.ms_width
            total_order_wt += order_detail.processing_wt
            _scrap += (order_detail.cut_width * order_detail.numbers)'''

    '''completed_processing_wt_lst = []
    completed_processing_numbers_lst = []
    total_completed_proc_wt = 0
   
        completed_processing_wt = 0.0
        completed_processing_numbers = 0
        for processing_detail in processing_detail_lst:
            if cs_rm.smpl_no == processing_detail.smpl_no and operation == processing_detail.operation:
                completed_processing_wt += float(processing_detail.processed_wt)
                completed_processing_numbers += int(processing_detail.processed_numbers)
        completed_processing_wt_lst.append(completed_processing_wt)
        total_completed_proc_wt += completed_processing_wt
        completed_processing_numbers_lst.append(completed_processing_numbers)
    total_completed_proc_wt = round(total_completed_proc_wt,3)'''

    if operation == "CTL":
        unit = current_user.unit
        return render_template('processing_ctl.html', incoming=incoming, operation=operation,
                               processing_details_lst=processing_detail_lst, cs_rm=cs_rm, cs_rm_id=cs_rm_id)
        ''', order=order,
                               order_detail_lst=zip(order_detail_id_lst_by_operation,order_detail_lst_by_operation),
                               _order_detail_lst=zip(order_detail_id_lst_by_operation, order_detail_lst_by_operation),
                               numbers=numbers, order_id=order_id, stage_no=stage_no, total_order_wt = total_order_wt,
                               total_completed_proc_wt = total_completed_proc_wt,
                               completed_processing_details_lst = zip(order_detail_lst_by_operation,
                                                                                completed_processing_wt_lst,
                                                                                completed_processing_numbers_lst))'''

    if operation == "Narrow_CTL":
        return render_template('processing_nctl.html', incoming=incoming, operation=operation,
                               processing_details_lst=processing_detail_lst, cs_rm=cs_rm, cs_rm_id=cs_rm_id)
        ''', order=order,
                               order_detail_lst=zip(order_detail_id_lst_by_operation,order_detail_lst_by_operation),
                               _order_detail_lst=zip(order_detail_id_lst_by_operation, order_detail_lst_by_operation),
                               numbers=numbers, order_id=order_id, stage_no=stage_no, total_order_wt = total_order_wt,
                               total_completed_proc_wt = total_completed_proc_wt,
                               completed_processing_details_lst = zip(order_detail_lst_by_operation,
                                                                                completed_processing_wt_lst,
                                                                                completed_processing_numbers_lst))'''

    if operation == 'Slitting' or operation == 'Mini_Slitting':
        # if operation == 'Slitting':
        #    _operation = 'Slitting'
        # if operation == 'Mini_Slitting':
        #    _operation = 'Mini_Slitting'
        return render_template('processing_slit.html', incoming=incoming, operation=operation,
                               processing_details_lst=processing_detail_lst, cs_rm=cs_rm, cs_rm_id=cs_rm_id)
        '''
        , order=order,
                               order_detail_lst=zip(order_detail_id_lst_by_operation,order_detail_lst_by_operation),
                               _order_detail_lst=zip(order_detail_id_lst_by_operation, order_detail_lst_by_operation),
                               numbers=numbers, order_id=order_id, total_order_wt = total_order_wt,
                               total_completed_proc_wt = total_completed_proc_wt,
                               completed_processing_details_lst = zip(order_detail_lst_by_operation,
                                                                                completed_processing_wt_lst,
                                                                                completed_processing_numbers_lst))'''

    if operation == 'Reshearing':
        return render_template('processing_reshearing.html', incoming=incoming, operation=operation,
                               processing_details_lst=processing_detail_lst, cs_rm=cs_rm, cs_rm_id=cs_rm_id)
        ''', order=order,
                               order_detail_lst=zip(order_detail_id_lst_by_operation,order_detail_lst_by_operation),
                               _order_detail_lst=zip(order_detail_id_lst_by_operation, order_detail_lst_by_operation),
                               numbers=numbers, order_id=order_id, stage_no=stage_no, total_order_wt = total_order_wt,
                               total_completed_proc_wt = total_completed_proc_wt,
                               completed_processing_details_lst = zip(order_detail_lst_by_operation,
                                                                                completed_processing_wt_lst,
                                                                                completed_processing_numbers_lst))'''

    if operation == 'Lamination':
        return render_template('processing_lamination.html', incoming=incoming, operation=operation,
                               processing_details_lst=processing_detail_lst, cs_rm=cs_rm, cs_rm_id=cs_rm_id)
        ''', order=order,
                               order_detail_lst=zip(order_detail_id_lst_by_operation,order_detail_lst_by_operation),
                               _order_detail_lst=zip(order_detail_id_lst_by_operation, order_detail_lst_by_operation),
                               numbers=numbers, order_id=order_id, stage_no=stage_no, total_order_wt = total_order_wt,
                               total_completed_proc_wt = total_completed_proc_wt,
                               completed_processing_details_lst = zip(order_detail_lst_by_operation,
                                                                                completed_processing_wt_lst,
                                                                                completed_processing_numbers_lst))'''


# 1. Get processing and processing details from the screen
# 2. Reduce the qty from mother material and update/insert cut material in current_stock
# 3. Check if stage is complete. If yes, change status of next stage in order detail to ready and current stage to
# completed
# 4. If all stages complete, the mark order closed
@app.route("/submit_processing", methods=['GET', 'POST'])
def submit_processing():
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']
        operation = request.form['operation']
        #order_id = request.form['order_id']

        input_size = request.form['input_material']
        output_width_lst = request.form.getlist('output_width')
        output_length_lst = request.form.getlist('output_length')
        #order_detail_id_lst = request.form.getlist('order_detail_id')

        fg_yes_no_lst = request.form.getlist('fg_yes_no')

        actual_no_of_pieces_lst = request.form.getlist('actual_no_of_pieces')
        packet_name_lst = request.form.getlist('packet_name')
        processed_wt_lst = request.form.getlist('processed_wt')
        remarks_lst = request.form.getlist('remarks')

        machine = request.form['machine']
        temp_machine = machine
        #I had originally wanted to keep operation in processing and machine in processing_detail diff
        #but this separation is only useful for unit 2 CTL where lamination causes an issue
        if machine.startswith('CTL 2'):
            operation = 'CTL 2'
            op_for_hdr = 'CTL 2'
        else:
            op_for_hdr = machine

        processing_date = request.form['processing_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        processing_time = request.form['processing_time']
        customer = request.form['customer']
        thickness = float(request.form['thickness'])
        grade = request.form['grade']

        no_of_qc = request.form['no_of_qc']
        no_of_helpers = request.form['no_of_helpers']
        names_of_qc = request.form['names_of_qc']
        #names_of_helpers = request.form['names_of_helpers']
        #name_of_packer = request.form['name_of_packer']

        setting_date = request.form['setting_date']
        setting_start_time = request.form['setting_start_time']
        setting_end_time = request.form['setting_end_time']
        setting_time = request.form['setting_time']

        #total_processed_wt = Decimal(request.form['total_processed_wt'])
        total_processed_wt = Decimal(request.form['total_processed_wt'])
        #balance_proc_wt = Decimal(request.form['balance_wt'])
        total_cuts = int(request.form['total_cuts'])
        rm_wt = Decimal(request.form['input_weight'])
        cs_rm_id = request.form['cs_rm_id']


        # Processing object created and saved to db
        processing = Processing(smpl_no, op_for_hdr, processing_date, start_time, end_time, setting_start_time,
                                setting_end_time, processing_time, setting_time, no_of_qc, no_of_helpers, names_of_qc, 
                                setting_date, total_processed_wt, total_cuts)
        processing_id = processing.save_to_db()

        # Slitting/Mini Slitting and CTL/Reshearing/NCTL are managed differently
        if operation == "CTL" or operation == "CTL 2" or operation == "Reshearing" or operation == "Narrow_CTL" or operation == "Lamination" or operation=="Levelling":
            lamination_lst = request.form.getlist('lamination')
            for output_width, output_length, actual_no_of_pieces, packet_name, processed_wt, \
                lamination, fg_yes_no, remarks in zip(output_width_lst, output_length_lst, actual_no_of_pieces_lst,
                                                                       packet_name_lst, processed_wt_lst,
                                                                        lamination_lst, fg_yes_no_lst, remarks_lst):
                ip_size = input_size.split('x')
                ms_width = ip_size[0]
                ms_length = ip_size[1]

                if lamination != "no-lami" and lamination != "No Lamination":
                    machine = temp_machine + " " + lamination

                if processed_wt != '' and Decimal(processed_wt) > 0.0:
                    # Get mother size and cut size from the screen. Create processing detail and then update to db
                    processing_detail = ProcessingDetail(smpl_no, operation, machine, processing_id, output_width,
                                                         output_length, actual_no_of_pieces,
                                                         packet_name, remarks, processed_wt, ms_width,
                                                         ms_length)
                    processing_detail.save_to_db()

                    if operation == "Reshearing":
                        # For reshearing, the mother material no. of pieces consumed have to be calculated and scrap
                        # per mother piece has to be calculated and subtracted from the weight
                        ms_weight = round((Decimal(thickness) * Decimal(ms_width) * Decimal(ms_length) * Decimal(0.00000785)),3)
                        output_weight = round((Decimal(thickness) * Decimal(output_length) * Decimal(output_width) * Decimal(0.00000785)),3)
                        # Calculate no of pieces got per mother sheet and then divide by no of output pieces to get
                        # no. of mother sheets consumed
                        no_of_pieces_per_ms = round((ms_weight/output_weight),0)
                        no_of_ms_consumed = round((int(actual_no_of_pieces)/no_of_pieces_per_ms),0)

                        # I am not handling scrap as of now because I don't know if the balance width is to be returned
                        # as balance or scrap. I have to think of how to do this.
                        # For scrap per mother sheet
                        #scrap_per_ms = (ms_weight - (output_weight*no_of_pieces_per_ms))
                        #total_scrap = Decimal(scrap_per_ms) * Decimal(no_of_ms_consumed) / Decimal(1000)

                        # the weight of RM to be reduced is the weight of FG + the scrap generated
                        #rm_processed_wt = Decimal(processed_wt) + round(total_scrap,3)

                        rm_processed_wt = Decimal(processed_wt)

                    elif operation == "Narrow_CTL":
                        no_of_ms_consumed = rm_wt/Decimal(processed_wt)
                        rm_processed_wt = processed_wt

                    elif operation == "CTL":
                        no_of_ms_consumed = 0
                        rm_processed_wt = processed_wt

                    else:
                        no_of_ms_consumed = actual_no_of_pieces
                        rm_processed_wt =  processed_wt

                    # Reduce weight of mother material by the processed weight of cut material - balance weight remaining in the mother material
                    # rm_processed_wt = Decimal(rm_processed_wt) + balance_proc_wt
                    rm_status = CurrentStock.change_wt(smpl_no, ms_width, ms_length, rm_processed_wt, no_of_ms_consumed, "minus")

                    # if rm_status == "complete":
                        # This is done when the RM is over but for some reason the order could not be completed
                        # This could when the RM is thickness is more or wrong calc of material or processing mistake/change
                        # OrderDetail.complete_processing_on_del(smpl_no, ms_width, ms_length)

                    # Increase weight of cut material by processed weight. If cut material, doesn't already exist, the
                    # function returns insert => a new record has to be inserted
                    cc_insert = CurrentStock.change_wt(smpl_no, output_width, output_length, processed_wt,
                                                       actual_no_of_pieces, "plus")

                    # Unit of the material is decided based on the machine used to process the material.
                    # WARNING: This is bad programming
                    if machine.startswith("CTL 2") or machine == "Slitting" or machine == "Mini_Slitting" or \
                            machine == "Reshearing 5" or machine == "Reshearing 6" or machine == "Reshearing 7" or \
                            machine == "NCTL 2" or machine == "NCTL 3":
                        unit = '2'
                    else:
                        unit = '1'

                    # The new material is inserted in to current stock
                    if cc_insert == "insert":
                        cs_cc = CurrentStock(smpl_no, customer, processed_wt, actual_no_of_pieces, thickness,
                                             output_width, output_length, fg_yes_no, grade, unit, packet_name)
                        cs_cc.save_to_db()

                    # This checks if detail is complete by comparing the processed weight and order detail weight.
                    # If the order detail is complete, it checks if all the order details in that stage are complete (check_stage_complete)
                    # If all the order details in that stage are complete, it makes the order details of the next stage ready for production
                    # If this is the last stage of the order, it marks the order as closed
                    #OrderDetail.detail_complete(order_detail_id)




        if operation == "Slitting" or operation == "Mini_Slitting":
            ip_size = input_size.split('x')
            ms_width = ip_size[0]
            ms_length = ip_size[1]
            actual_no_of_packets_lst = request.form.getlist('actual_no_of_pieces')
            # actual_no_of_pieces = no of slits * no of parts
            # actual_no_of_packets = length_per_part
            # numbers =
            total_length = float(request.form['total_length'])

            no_of_parts = int(actual_no_of_packets_lst[0])
            length_per_part = float(total_length/no_of_parts)
            no_of_slits_lst = request.form.getlist('no_of_slits')
            # processed_wt = processed_wt_lst[0]
            remarks = remarks_lst[0]
            output_length = 0


            for output_width, fg_yes_no, no_of_slits, order_detail_id in zip(
                    output_width_lst, fg_yes_no_lst, no_of_slits_lst):
                if no_of_slits != '':
                    if int(no_of_slits) > 0 and no_of_parts > 0:
                        # Get number of coils produced for size = no of slits x no of parts
                        no_of_coils = int(no_of_slits) * no_of_parts
                        # This is processed weight for that size
                        processed_wt = Decimal(thickness * float(output_width) * length_per_part * 0.00000785 * no_of_coils)
                        processed_wt = round(processed_wt, 3)

                        # Processing details updated to db
                        if processed_wt > 0:
                            processing_detail = ProcessingDetail(smpl_no, operation, machine, processing_id, output_width,
                                                                 output_length, no_of_coils, length_per_part,
                                                                 remarks, processed_wt, ms_width, ms_length, order_detail_id)


                            processing_detail.save_to_db()

                            # Reduce weight of mother material by the processed weight of cut material
                            rm_status = CurrentStock.change_wt(smpl_no, ms_width, ms_length, processed_wt, length_per_part, "minus")

                            #if rm_status == "complete":
                                # This is done when the RM is over but for some reason the order could not be completed
                                # This could when the RM is thickness is more or wrong calc of material or processing mistake/change
                            #    OrderDetail.complete_processing_on_del(smpl_no, ms_width, ms_length)

                            # If the mother material is completed, then the order detail which has this

                            # Increase weight of cut material by processed weight. If cut material, doesn't already exist, the
                            # function returns insert => a new record has to be inserted
                            cc_insert = CurrentStock.change_wt(smpl_no, output_width, output_length, processed_wt,
                                                               no_of_coils, "plus")

                            # Unit of the material is decided based on the machine used to process the material.
                            # WARNING: This is bad programming
                            unit = '2'

                            # The new material is added to current stock
                            if cc_insert == "insert":
                                cs_cc = CurrentStock(smpl_no, customer, processed_wt, no_of_coils, thickness,
                                                     output_width, output_length, fg_yes_no, grade, unit)
                                cs_cc.save_to_db()

                            # This checks if detail is complete by comparing the processed weight and order detail weight.
                            # If the order detail is complete, it checks if all the order details in that stage are complete
                            # (check_stage_complete)
                            # If all the order details in that stage are complete, it makes the order details of the next stage
                            # ready for production
                            # If this is the last stage of the order, it marks the order as closed
                            # OrderDetail.detail_complete(order_detail_id)

            # This is for the slitter maintenance
            # Get the slitter batches and numbers used in slitting
            slitter_batch_lst = request.form.getlist('slitter_batch')
            slitter_number_lst = request.form.getlist('slitter_number')

            # The meterage is updated to the slitter usage  and slitter grinding table
            for slitter_batch, slitter_numbers in zip(slitter_batch_lst, slitter_number_lst):
                slitter_numbers = slitter_numbers.split(' ')
                for slitter_number in slitter_numbers:
                    if slitter_number != '':
                        slitter_usage = SlitterUsage(processing_id, smpl_no, slitter_batch, slitter_number, total_length,
                                                 thickness)
                        slitter_usage.save_to_db()

        # I'm assuming if less than 3% of the rm weight remains, that the material is over and the rm can be deleted
        # balance_proc_wt is >0, if the mother material if order wt > processed wt but user wants to mark the order complete
        # subtracting this from rm_wt will make the balance wt < 0.03 of rm_wt and thus, help us mark the order complete
        '''balance_wt = (rm_wt - total_processed_wt - abs(balance_proc_wt))
        if (balance_wt/rm_wt) < 0.03:
            OrderDetail.complete_processing_on_del(smpl_no, ms_width, ms_length)
            CurrentStock.delete_record(cs_rm_id)'''

        return render_template('/main_menu.html', message="Processing for " + smpl_no + " entered.")



@app.route("/submit_slitting_processing", methods=['GET', 'POST'])
def submit_slitting_processing():
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']
        operation = request.form['operation']
        #order_id = request.form['order_id']

        input_size = request.form['input_material']
        output_width_lst = request.form.getlist('output_width')
        width_name_lst = request.form.getlist('width_name')
        #order_detail_id_lst = request.form.getlist('order_detail_id')
        fg_yes_no_lst = request.form.getlist('fg_yes_no')

        part_length_lst = request.form.getlist('part_length')
        part_name_lst = request.form.getlist('part_name')
        #processed_wt_lst = request.form.getlist('processed_wt')
        #remarks = request.form['remarks']
        remarks = ''

        machine = request.form['machine']
        temp_machine = machine
        processing_date = request.form['processing_date']
        start_time = request.form['start_time']
        end_time = request.form['end_time']
        processing_time = request.form['processing_time']
        customer = request.form['customer']
        thickness = float(request.form['thickness'])
        grade = request.form['grade']

        no_of_qc = request.form['no_of_qc']
        no_of_helpers = request.form['no_of_helpers']
        #names_of_qc = request.form['names_of_qc']
        #names_of_helpers = request.form['names_of_helpers']
        #name_of_packer = request.form['name_of_packer']
        names_of_qc=''

        setting_date = request.form['setting_date']
        setting_start_time = request.form['setting_start_time']
        setting_end_time = request.form['setting_end_time']
        setting_time = request.form['setting_time']

        #total_processed_wt = Decimal(request.form['total_processed_wt'])
        total_processed_wt = Decimal(request.form['total_processed_wt'])
        #balance_proc_wt = Decimal(request.form['balance_wt'])
        total_length = int(request.form['total_length'])
        rm_wt = Decimal(request.form['input_weight'])
        cs_rm_id = request.form['cs_rm_id']

        # Processing object created and saved to db
        processing = Processing(smpl_no, operation, processing_date, start_time, end_time, setting_start_time,
                                setting_end_time, processing_time, setting_time, no_of_qc, no_of_helpers, names_of_qc,
                                setting_date, total_processed_wt, total_length)
        processing_id = processing.save_to_db()

        ip_size = input_size.split('x')
        ms_width = ip_size[0]
        ms_length = ip_size[1]

        for output_width, width_name, fg_yes_no in zip(output_width_lst, width_name_lst, fg_yes_no_lst):
            for part_length, part_name in zip(part_length_lst, part_name_lst):
                output_length = 0
                processed_numbers = 1

                packet_name = width_name + part_name
                part_weight = Decimal(thickness * float(output_width) * float(part_length) * 0.00000785)
                part_weight = round(part_weight, 3)
                processing_detail = ProcessingDetail(smpl_no, operation, machine, processing_id, output_width,
                                                     output_length, processed_numbers, packet_name, remarks, part_weight,
                                                     ms_width, ms_length)
                processing_detail.save_to_db()

                # Reduce weight of mother material by the processed weight of cut material
                rm_status = CurrentStock.change_wt(smpl_no, ms_width, ms_length, part_weight, processed_numbers, "minus")

                # Increase weight of cut material by processed weight. If cut material, doesn't already exist, the
                # function returns insert => a new record has to be inserted
                cc_insert = CurrentStock.change_wt(smpl_no, output_width, output_length, part_weight,
                                                   processed_numbers, "plus")

                # Unit of the material is decided based on the machine used to process the material.
                # WARNING: This is bad programming
                unit = '2'

                # The new material is added to current stock
                if cc_insert == "insert":
                    cs_cc = CurrentStock(smpl_no, customer, part_weight, processed_numbers, thickness,
                                         output_width, output_length, fg_yes_no, grade, unit, packet_name)
                    cs_cc.save_to_db()
        return render_template('/main_menu.html', message=Markup("Processing for " + smpl_no + " entered"))


@app.route('/print_label', methods=['GET', 'POST'])
def print_label():
    processing_id=0
    if request.method == 'POST':
        processing_id = request.form['processing_id']

    if request.method == 'GET':
        processing_id = request.args.get('processing_id')
    return render_template('print_label.html')

@app.route('/print_label_big', methods=['GET', 'POST'])
def print_label_big():
    processing_id=0
    if request.method == 'POST':
        processing_id = request.form['processing_id']

    if request.method == 'GET':
        processing_id = request.args.get('processing_id')
    return render_template('print_label_big.html')

@app.route('/print_label_reshearing', methods=['GET', 'POST'])
def print_label_reshearing():
    processing_id=0
    if request.method == 'POST':
        processing_id = request.form['processing_id']

    if request.method == 'GET':
        processing_id = request.args.get('processing_id')
    return render_template('print_label_reshearing.html')


@app.route('/check_stock', methods=['GET', 'POST'])
def check_stock():
    return render_template('check_stock.html')


# Function displays stock based on stock type selected
@app.route('/stock', methods=['GET', 'POST'])
def stock():
    stock_type = ""
    cs_lst = []
    _cs_lst = []
    cs_id_lst = []
    if request.method == 'POST':
        stock_type = request.form['stock_type']

    if request.method == 'GET':
        stock_type = request.args.get('stock_type')

    if current_user.unit == 1 or current_user.unit == 2:
        cs_lst = CurrentStock.get_stock(stock_type, current_user.unit)
    else:
        cs_lst_unit1 = CurrentStock.get_stock(stock_type, '1')
        for cs_id, cs in cs_lst_unit1:
            cs_id_lst.append(cs_id)
            _cs_lst.append(cs)
        cs_lst_unit2 = CurrentStock.get_stock(stock_type, '2')
        for cs_id, cs in cs_lst_unit2:
            cs_id_lst.append(cs_id)
            _cs_lst.append(cs)
        #cs_lst.append(cs_lst_unit1)
        #cs_lst.append(cs_lst_unit2)
        cs_lst = zip(cs_id_lst,_cs_lst)

    return render_template('stock_display.html', cs_lst=cs_lst)


# Choose from list of customer for whose FG/RM is present for dispatch
@app.route('/dispatch_pick_customer', methods=['GET', 'POST'])
def dispatch_pick_customer():
    customer_lst = CurrentStock.customer_list_for_dispatch()
    return render_template('dispatch_pick_customer.html', customer_lst=customer_lst)


# Display list of FG/RM of selected customer to choose for dispatch
@app.route('/dispatch_list', methods=['GET', 'POST'])
def dispatch_list():
    customer = ""
    display_type = ""
    if request.method == 'POST':
        customer = request.form['select_customer']
        display_type = request.form['FG/RM']
    if request.method == 'GET':
        customer = request.args.get('select_customer')
        display_type = request.args.get('FG/RM')

    cs_lst = CurrentStock.get_stock_by_customer(customer, display_type)

    return render_template('dispatch_list.html', cs_lst=cs_lst, customer=customer)


@app.route('/dispatch', methods=['GET', 'POST'])
def dispatch():
    if request.method == 'POST':
        dispatch_lst = request.form.getlist['select_smpl']
        dispatch_nos = request.form.getlist['dispatch_numbers']
        dispatch_quantity = request.form.getlist['dispatch_quantity']
        vehicle_no = request.form['vehicle_no']
        customer = request.form['customer']
        dispatch_date = request.form['dispatch_date']
        dispatch_time = request.form['dispatch_time']
        dispatch_pkts = request.form.getlist['dispatch_packets']
        remarks = request.form['remarks']

    if request.method == 'GET':
        dispatch_lst = request.args.getlist('select_smpl')
        dispatch_nos = request.args.getlist('dispatch_numbers')
        dispatch_quantity = request.args.getlist('dispatch_quantity')
        dispatch_pkts = request.args.getlist('dispatch_packets')
        defectives = request.args.getlist('defective')
        vehicle_no = request.args.get('vehicle_no')
        customer = request.args.get('customer')
        dispatch_date = request.args.get('dispatch_date')
        dispatch_time = request.args.get('dispatch_time')
        remarks = request.args.get('remarks')
        invoice_no = request.args.get('invoice_no')

    # This fetches the list and removes the elements that are not selected
    # The ones that are not selected are returned as None. The below list filters out the Nones
    dispatch_nos_lst = list(filter(None, dispatch_nos))
    dispatch_quantity_lst = list(filter(None, dispatch_quantity))
    defectives_lst = list(filter(None, defectives))
    dispatch_pkts_lst = list(filter(None,dispatch_pkts))

    dispatch_header = DispatchHeader(vehicle_no, customer, dispatch_date, dispatch_time, invoice_no, remarks)
    dispatch_id = dispatch_header.save_to_db()

    # For the items to be dispatched, dispatch detail is created and the current stock quantity is deleted or reduced
    for smpl, dispatch_nos, dispatch_qty, defective, no_of_packets in zip(dispatch_lst, dispatch_nos_lst, 
        dispatch_quantity_lst, defectives_lst, dispatch_pkts_lst):
        smpl_details = smpl.split(',')
        smpl_no = smpl_details[1]
        cs_id = smpl_details[0]
        cs = CurrentStock.load_smpl_by_id(cs_id)
        dispatch_detail = DispatchDetail(dispatch_id, cs.smpl_no, cs.thickness, cs.width, cs.length, int(dispatch_nos),
                                         Decimal(dispatch_qty), defective, int(no_of_packets))
        dispatch_detail.save_to_db()
        if dispatch_nos == cs.numbers:
            CurrentStock.delete_record(cs_id)
        else:
            cs.change_wt(smpl_no, cs.width, cs.length, dispatch_qty, dispatch_nos,'minus')

    return render_template('/main_menu.html')


@app.route('/display_dispatch_pick_day', methods=['GET', 'POST'])
def display_dispatch_pick_day():
    return render_template('dispatch_pick_date.html')


@app.route('/dispatch_list_hdr_by_date', methods=['GET', 'POST'])
def dispatch_list_hdr_by_date():
    if request.method == 'POST':
        dispatch_date = request.form['dispatch_date']
    if request.method == 'GET':
        dispatch_date = request.args.get('dispatch_date')

    dispatch_hdr_lst = DispatchHeader.get_dispatch_lst_by_date(dispatch_date)
    return render_template('pick_dispatch_hdr.html', dispatch_hdr_lst=dispatch_hdr_lst)


@app.route('/dispatch_view_detail', methods=['GET', 'POST'])
def dispatch_view_detail():
    if request.method == 'POST':
        select_dispatch_hdr_id = request.form['select_dispatch_hdr']
    if request.method == 'GET':
        select_dispatch_hdr_id = request.args.get('select_dispatch_hdr')

    dispatch_detail_lst = DispatchDetail.get_details_by_id(select_dispatch_hdr_id)
    dispatch_hdr = DispatchHeader.get_hdr_by_id(select_dispatch_hdr_id)

    return render_template('dispatch_view.html', dispatch_hdr=dispatch_hdr, dispatch_detail_lst=dispatch_detail_lst)


@app.route('/pick_slitting_batch', methods=['GET', 'POST'])
def pick_slitting_batch():
    slitter_lst = SlitterBatch.getSlitterLst()
    return render_template('slitter_pick_batch.html', slitter_lst=slitter_lst)


@app.route('/slitter_grinding_entry', methods=['GET', 'POST'])
def slitter_griding_entry():
    if request.method == 'POST':
        slitter_batch_no = request.form['select_slitter']
        submit_type = request.form['submit']
    if request.method == 'GET':
        slitter_batch_no = request.args.get('select_slitter')
        submit_type = request.args.get('submit')

    slitter_batch = SlitterBatch.load_slitter(slitter_batch_no)

    if submit_type == 'Enter Grinding Details':
        return render_template('slitter_grinding.html', slitter_batch=slitter_batch)

    if submit_type == 'View Slitter Details':
        slitter_grinding_lst = slitter_batch.get_slitter_grinding()
        return render_template('slitter_batch_view.html', slitter_batch=slitter_batch, 
                                slitter_grinding_lst=slitter_grinding_lst)


@app.route('/slitter_grinding_submit', methods=['GET','POST'])
def slitter_grinding_submit():
    if request.method == 'POST':
        slitter_batch_no = request.form['slitter_batch']
        start_date = request.form['start_date']
        end_date = request.form['end_date']
        return_date = request.form['return_date']
        new_od = request.form['new_od']
    if request.method == 'GET':
        slitter_batch_no = request.args.get('slitter_batch')
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        return_date = request.args.get('return_date')
        new_od = request.args.get('new_od')

    SlitterBatch.after_return_from_grinding(slitter_batch_no, end_date, return_date, float(new_od))
    return render_template('/main_menu.html')



@app.route('/enter_smpl_no', methods=['GET', 'POST'])
def enter_smpl_no():
    return render_template('/history_enter_smpl_no.html')


@app.route('/history_show_details', methods=['GET', 'POST'])
def history_show_details():
    smpl_number = ""
    file_list = ""
    if request.method == 'POST':
        smpl_number = request.form['smpl_no']
    if request.method == 'GET':
        smpl_number = request.args.get('smpl_no')

    dispatch_hdr_lst = []
    dispatch_dtl_lst, _dispatch_dtl_lst = [], []
    dispatch_id_lst = []
    order_lst, order_id_lst, _order_lst, order_lst_by_smpl, order_id_lst_by_smpl = [], [], [], [], []
    _processing_hdr_lst, processing_hdr_lst, processing_hdr_id_lst= [], [], []
    _order_dtl_lst, order_dtl_lst, order_dtl_id_lst = [], [], []
    order_dtl_lst_by_orderid, order_dtl_id_lst_by_orderid = [],[]
    processing_dtl_lst, processing_dtl_lst_by_order_dtl = [], []
    cs_lst, _cs_lst = [], []

    smpl_number = str(smpl_number).upper().replace(" ", "")
    #smpl_no.replace(" ", "")
    smpl_no_lst = Incoming.smpl_no_list_for_history(smpl_number)

    if smpl_no_lst:
        # the query from incoming returns smpl_nos in ascending order. The original number is always going to be the
        # the first element
        incoming = Incoming.load_smpl_by_smpl_no(smpl_no_lst[0])
        for smpl_no in smpl_no_lst:
            _cs_lst = (CurrentStock.load_smpl_for_history(smpl_no))
            if _cs_lst:
                for cs in _cs_lst:
                    cs_lst.append(cs)

            _processing = Processing.load_history(smpl_no)
            for processing_id, processing in _processing:
                processing_hdr_lst.append(processing)
                processing_hdr_id_lst.append(processing_id)
                processing_dtl_lst.append(ProcessingDetail.load_history(processing_id))

            '''_order_lst = Order.history_load_from_db(smpl_no)
            for ordr_id, ordr in _order_lst:
                order_id_lst.append(ordr_id)
                order_lst.append(ordr)
                _order_dtl_lst = OrderDetail.load_from_db(smpl_no,ordr_id)
                for _ordr_dtl_id, _ordr_dtl in _order_dtl_lst:
                    order_dtl_id_lst.append(_ordr_dtl_id)
                    order_dtl_lst.append(_ordr_dtl)
                    processing_dtl_lst.append(ProcessingDetail.load_history(_ordr_dtl_id))
                _processing = Processing.load_history(ordr_id)
                for processing_id, processing in _processing:
                    processing_hdr_lst.append(processing)
                    processing_hdr_id_lst.append(processing_id)
            order_lst_by_smpl.append(order_lst)
            order_id_lst_by_smpl.append(order_id_lst)
            order_dtl_lst_by_orderid.append(order_dtl_lst)
            order_dtl_id_lst_by_orderid.append(order_dtl_id_lst)'''

            _dispatch_dtl_lst.append(DispatchDetail.load_from_db(smpl_no))
            for dispatch_dtl_sublst in _dispatch_dtl_lst:
                for dispatch_dtl in dispatch_dtl_sublst:
                    dispatch_id_lst.append(int(dispatch_dtl.dispatch_id))
                    dispatch_dtl_lst.append(dispatch_dtl)

        dispatch_id_lst = list(set(dispatch_id_lst))
        dispatch_lst = []
        i = 0
        for dispatch_id in dispatch_id_lst:
            dispatch_hdr_lst.append(DispatchHeader.load_from_db(dispatch_id))
            dispatch_lst.append(dispatch_hdr_lst[i][0])
            i+=1


        return render_template('/hist_view.html', incoming=incoming, file_list=file_list,
                               smpl_no_lst=smpl_no_lst,
                               order_lst_by_smpl=zip(order_lst,order_id_lst),
                               order_id_lst_by_smpl=order_id_lst_by_smpl,
                               order_dtl_id_lst_by_orderid = order_dtl_id_lst_by_orderid,
                               order_dtl_lst_by_orderid = order_dtl_lst_by_orderid,
                               order_dtl_lst = order_dtl_lst,
                               processing_dtl_lst = processing_dtl_lst,
                               processing_hdr_lst= zip(processing_hdr_lst, processing_hdr_id_lst),
                               dispatch_hdr_lst=zip(dispatch_lst, dispatch_id_lst),
                               dispatch_dtl_lst=dispatch_dtl_lst,
                               cs_lst=cs_lst)

    else:
        return render_template('/main_menu.html', message= smpl_number + " not found.")

    '''
    dispatch_hdr_lst=zip(dispatch_lst, dispatch_id_lst),
                           dispatch_dtl_lst=dispatch_dtl_lst, smpl_no_lst = smpl_no_lst,
                           order_lst = order_lst_by_smpl,
                           order_id_lst= order_id_lst_by_smpl, order_dtl_lst = order_dtl_lst_by_orderid,
                           order_dtl_id_lst = order_dtl_lst_by_orderid,
                           processing_lst = processing_hdr_lst_by_orderid,
                           processing_id_lst = processing_hdr_id_lst,
                           processing_dtl_lst = processing_dtl_lst_by_order_dtl
                           
    order_lst = Order.history_load_from_db(smpl_no)
    if order_lst:
        for order_id, _order in order_lst:
            _order_detail_lst = OrderDetail.load_from_db(smpl_no, order_id)
            order = _order
            processing_lst.append(Processing.load_history(order_id))

        for _processing in processing_lst:
            for processing_id, processing in _processing:
                processing_hdr_lst.append(processing)
                processing_id_lst.append(processing_id)

        for order_detail_id, order_detail in _order_detail_lst:
            order_detail_lst.append(order_detail)
            order_detail_id_lst.append(order_detail_id)
            _processing_dtl_lst =(ProcessingDetail.load_history(order_detail_id))
            for processing_dtl in _processing_dtl_lst:
                processing_dtl_lst.append(processing_dtl)


        i = 0
        while len(order_detail_lst) > 0:
            operation = order_detail_lst[i].operation
            stage_no = order_detail_lst[i].stage_no
            # order_detail_by_stage_and_op_lst.append(order_detail)
            ms = str(order_detail_lst[i].ms_width) + " x " + str(order_detail_lst[i].ms_length)
            proc_wt = 0
            for order_detail2 in order_detail_lst:
                if order_detail2.operation == operation and stage_no == order_detail2.stage_no:
                    order_detail_by_stage_and_op_lst.append(order_detail2)
                    proc_wt += order_detail2.processing_wt
                    # order_detail_lst.remove(order_detail2)
            order_detail_for_print_lst.append(order_detail_by_stage_and_op_lst)
            operation_lst.append(operation)
            stage_no_lst.append(stage_no)
            ms_lst.append(ms)
            proc_wt_lst.append(proc_wt)
            for order_detail3 in order_detail_by_stage_and_op_lst:
                order_detail_lst.remove(order_detail3)
            order_detail_by_stage_and_op_lst = []



        _dispatch_dtl_lst.append(DispatchDetail.load_from_db(smpl_no))
        for dispatch_dtl_sublst in _dispatch_dtl_lst:
            for dispatch_dtl in dispatch_dtl_sublst:
                dispatch_id_lst.append(int(dispatch_dtl.dispatch_id))
                dispatch_dtl_lst.append(dispatch_dtl)

        dispatch_id_lst = list(set(dispatch_id_lst))
        dispatch_lst = []
        for dispatch_id in dispatch_id_lst:
            dispatch_hdr_lst.append(DispatchHeader.load_from_db(dispatch_id))
            dispatch_lst = dispatch_hdr_lst[0]

    # file_list = FileUploader.get_files_for_smpl_no(smpl_no)
    file_list = ""

    # processing_hdr_lst = zip(processing_lst, processing_id_lst),
    # processing_dtl_lst = processing_dtl_lst[0],
return render_template('/history_view.html', incoming=incoming, file_list=file_list,
                        dispatch_hdr_lst=zip(dispatch_lst,dispatch_id_lst),
                       dispatch_dtl_lst=dispatch_dtl_lst, order=order,
                           order_detail_lst=zip(order_detail_for_print_lst, operation_lst, ms_lst, proc_wt_lst,
                                                stage_no_lst),
                       processing_hdr_lst = zip(processing_hdr_lst,processing_id_lst), processing_dtl_lst = processing_dtl_lst)'''



@app.route('/daily_report_pick_date', methods=['GET', 'POST'])
def daily_report_pick_date():
    return render_template('/daily_report_pick_date.html')

@app.route('/get_daily_report', methods=['GET', 'POST'])
def get_daily_report():
    report_date = ""
    if request.method == 'POST':
        report_date = request.form['report_date']
    if request.method == 'GET':
        report_date = request.args.get('report_date')
    processing_lst=[]
    processing_hdr_detail= []
    processing_dtl_lst = []
    incoming_lst = []
    dispatch_hdr_lst = []
    total_incoming = 0

    incoming_lst = Incoming.get_daily_report(report_date)
    for incoming in incoming_lst:
        total_incoming += incoming[1]

    processing_hdr_lst = Processing.get_daily_report(report_date)

    processing_hdr_detail = Processing.get_daily_report_detail(report_date)

    dispatch_hdr_lst = DispatchHeader.get_daily_report(report_date)

    return render_template('/daily_report.html', date = change_date_format(report_date), incoming_lst = incoming_lst,
                           total_incoming = total_incoming, processing_hdr_lst = processing_hdr_lst,
                           dispatch_hdr_lst = dispatch_hdr_lst, processing_hdr_detail = processing_hdr_detail)

def change_date_format(date):
    split_date = date.split('-')
    new_date = split_date[2] + '-' + split_date[1] + '-' + split_date[0]
    return new_date

if __name__ == '__main__':
    app.config["SECRET_KEY"] = "SMPLMRP"
    # app.run(debug=True)
    SERVER_NAME = '0.0.0.0'
    SERVER_PORT = 5001
    app.run(SERVER_NAME, SERVER_PORT, threaded=True, debug=True)
