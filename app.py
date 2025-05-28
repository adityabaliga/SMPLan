from waitress import serve
import logging
from werkzeug.middleware.profiler import ProfilerMiddleware

from decimal import Decimal
from flask_login import LoginManager, login_user, current_user, logout_user
from file_uploader import FileUploader
from flask import Flask, render_template, request, jsonify
from markupsafe import Markup
from csv import writer
from datetime import datetime, timedelta
import calendar
import pandas as pd
import openpyxl
import urllib.request
from apscheduler.schedulers.background import BackgroundScheduler
import atexit

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
import psycopg2
from urllib.parse import unquote

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)

handler = logging.FileHandler('D:\\SMPLan\\app.log')
handler.setLevel(logging.ERROR)
app.logger.addHandler(handler)

# Clicking on http://127.0.0.1:5000/ (the home page), this will redirect you to login page
@app.route('/')
def home(message=""):
    # logger.info("Here's some info")
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
        unit = request.form['unit']


    else:
        xml_filename = request.args.get('xml_filename')
        unit = request.args.get('unit')

    incoming_lst = Incoming.fromfile(xml_filename, unit)
    # The details got from the XML file are updated to the database. The details are displayed for review and if any
    # remarks are to be entered
    #for incoming_coil in incoming_lst:
    #    incoming_coil.savetodb()
    return render_template('incoming_review_after_upload_form.html', incoming_lst=incoming_lst)


# The remarks are recovered. SMPL No is made a hidden field in the HTML to map the remarks and the SMPL
# This is then updated to the DB and then redirects to the main menu
@app.route('/submit_smpl_incoming', methods=['GET', 'POST'])
def submit_smpl_incoming():

    _smpl_nos_lst = []
    if request.method == 'POST':
        _smpl_nos_lst = request.form.getlist('select_smpl')


    # This fetches the list and removes the elements that are not selected
    # The ones that are not selected are returned as None. The below list filters out the Nones
    smpl_nos_lst = list(filter(None, _smpl_nos_lst))



    for smpl_no_string in smpl_nos_lst:
        incoming_str = smpl_no_string.split(';')
        incoming = Incoming(incoming_str[0], incoming_str[1], incoming_str[2], Decimal(incoming_str[3]),
                            Decimal(incoming_str[4]), Decimal(incoming_str[5]), incoming_str[6],
                            Decimal(incoming_str[7]),Decimal(incoming_str[8]),incoming_str[9],incoming_str[10],
                            incoming_str[11],
                            incoming_str[12],incoming_str[13],incoming_str[14], incoming_str[15],incoming_str[16],
                            incoming_str[17])
        incoming.savetodb()

        #Incoming.update_remarks_by_smpl_no(remark, smpl_no)

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

        weight = Decimal(request.form['weight'])
        numbers = int((request.form['numbers']))
        mill = request.form['mill']
        mill_id = request.form['mill_id']
        incoming_remarks = request.form['remarks']
        unit = request.form['unit']
        dc_number = request.form['dc_number']
        dc_date = request.form['dc_date']


        _incoming = Incoming(smpl_no, customer, incoming_date, thickness, width, length, grade, weight, numbers,
                             mill, mill_id, incoming_remarks, unit, material_type, '', '',
                             dc_number, dc_date)
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
    #if current_user.unit == 1 or current_user.unit == 2:
    #    cs_return_lst = CurrentStock.get_stock('All', str(current_user.unit))
    #else:

    return render_template('/transfer_pick_unit.html', stock_type='All', _unit=current_user.unit)

    #return render_template('transfer_enter_smpl_no.html', _unit=current_user.unit)
    '''cs_obj_lst = []
    cs_id_lst = []

    for cs_id, cs in cs_return_lst:
        cs_id_lst.append(cs_id)
        cs_obj_lst.append(cs)

    if cs_obj_lst:
        return render_template('transfer_material.html', cs_lst=zip(cs_id_lst, cs_obj_lst), _unit = current_user.unit)
    else:
        return render_template('/main_menu.html', message="No Raw material to transfer")'''


@app.route('/transfer_pick_unit', methods=['GET', 'POST'])
def transfer_pick_unit():
    stock_type = ""
    unit = ""
    if request.method == 'POST':
        unit = int(request.form['select_unit'])
        stock_type = request.form['stock_type']
    if request.method == 'GET':
        unit = int(request.args.get('select_unit'))
        stock_type = request.args.get('stock_type')

    '''cs_return_lst = CurrentStock.get_stock(stock_type,unit)

    cs_obj_lst = []
    cs_id_lst = []

    for cs_id, cs in cs_return_lst:
        cs_id_lst.append(cs_id)
        cs_obj_lst.append(cs)'''

    # if cs_obj_lst:
    # return render_template('transfer_material.html', cs_lst=zip(cs_id_lst, cs_obj_lst), _unit = unit)
    return render_template('transfer_enter_smpl_no.html', _unit=unit)
    # else:
    #   return render_template('/main_menu.html', message="No Raw material to transfer")


@app.route('/transfer_pick_size', methods=['GET', 'POST'])
def transfer_pick_size():
    smpl = ""
    unit = ""
    cs_return_lst = []
    cs_id_lst = []
    cs_obj_lst = []

    if request.method == 'POST':
        smpl = request.form['smpl_no']
        unit = request.form['unit']

    if request.method == 'GET':
        smpl = request.args.get('smpl_no')
        unit = request.args.get('unit')

    cs_return_lst = []
    cs_return_lst_unit4 = []

    cs_return_lst = CurrentStock.load_smpl_by_smplno(smpl, unit)
    # This is done so that anyone can transfer in to or out of Unit 4 [501] currently
    #cs_return_lst_unit4 = CurrentStock.load_smpl_by_smplno(smpl, '4')

    for cs_id, cs in cs_return_lst:
        cs_id_lst.append(cs_id)
        cs_obj_lst.append(cs)
        customer = cs.customer

    '''for cs_id, cs in cs_return_lst_unit4:
        cs_id_lst.append(cs_id)
        cs_obj_lst.append(cs)'''

    if cs_obj_lst:
        return render_template('transfer_list.html', cs_lst=zip(cs_id_lst, cs_obj_lst), unit=unit, customer = customer)

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
        transfer_lst = request.form.getlist['select_smpl']
        transfer_nos = request.form.getlist['dispatch_numbers']
        transfer_quantity = request.form.getlist['dispatch_quantity']
        vehicle_no = request.form['vehicle_no']
        customer = request.form['customer']
        transfer_date = request.form['dispatch_date']
        transfer_time = request.form['dispatch_time']
        transfer_pkts = request.form.getlist['dispatch_packets']
        unit = request.form.getlist['_unit']
        remarks = request.form['remarks']
        entry_by = request.form['entry_by']

    if request.method == 'GET':
        transfer_lst = request.args.getlist('select_smpl')
        transfer_nos = request.args.getlist('dispatch_numbers')
        transfer_quantity = request.args.getlist('dispatch_quantity')
        transfer_pkts = request.args.getlist('dispatch_packets')
        unit = request.args.getlist('_unit')
        vehicle_no = request.args.get('vehicle_no')
        customer = request.args.get('customer')
        transfer_date = request.args.get('dispatch_date')
        transfer_time = request.args.get('dispatch_time')
        remarks = request.args.get('remarks')
        invoice_no = request.args.get('invoice_no')
        current_unit = request.args.get('current_unit')
        entry_by = request.args.get('entry_by')

    # This fetches the list and removes the elements that are not selected
    # The ones that are not selected are returned as None. The below list filters out the Nones
    transfer_nos_lst = list(filter(None, transfer_nos))
    transfer_quantity_lst = list(filter(None, transfer_quantity))
    unit_lst = list(filter(None, unit))
    transfer_pkts_lst = list(filter(None, transfer_pkts))
    remarks = "TRANSFER TO UNIT " + unit[0]
    invoice_no = 'TRANSFER'

    transfer_header = DispatchHeader(vehicle_no, customer, transfer_date, transfer_time, invoice_no, remarks, entry_by)
    transfer_id = transfer_header.save_to_db()

    # Transfer Material has been changed for only partial material to be shifted.
    # Logic has been borrowed from Dispatch material
    for smpl, transfer_nos, transfer_qty, unit, no_of_packets in zip(transfer_lst, transfer_nos_lst,
                                                                     transfer_quantity_lst, unit_lst,
                                                                     transfer_pkts_lst):
        smpl_details = smpl.split(',')
        smpl_no = smpl_details[1]
        cs_id = int(smpl_details[0])
        cs = CurrentStock.load_smpl_by_id(cs_id)
        dispatch_detail = DispatchDetail(transfer_id, cs.smpl_no, cs.thickness, cs.width, cs.length, int(transfer_nos),
                                         Decimal(transfer_qty), '', int(no_of_packets), cs.length2,
                                         cs.packet_name, cs.unit)
        dispatch_detail.save_to_db()
        if int(transfer_nos) == cs.numbers:
            CurrentStock.transfer_material_cls(cs_id, unit)
        else:
            cs_new = CurrentStock(smpl_no, cs.customer, Decimal(transfer_qty), transfer_nos, cs.thickness, cs.width,
                                  cs.length, cs.status, cs.grade, unit, cs.packet_name, cs.length2, cs.date,
                                  cs.processing_id, '', 0)
            cs.change_wt(smpl_no, cs.width, cs.length, transfer_qty, transfer_nos, 'minus', cs.status, cs.length2)
            if cs_new.check_if_size_exists():
                cs_new.change_wt(cs_new.smpl_no, cs_new.width, cs_new.length, transfer_qty, transfer_nos,
                                 "plus", cs_new.status, cs_new.length2)
            else:
                cs_new.save_to_db()
        #transfer_remarks = "Transferred to Unit " + unit + " from " + current_unit
        #Incoming.update_remarks(transfer_remarks, smpl_no)

    '''smpl_details = smpl.split(',')
        smpl_no = smpl_details[1]
        cs_id = smpl_details[0]
        CurrentStock.transfer_material_cls(cs_id, unit)'''
    return render_template('/main_menu.html')


# pick smpl for deleting SMPL
@app.route('/delete_pick_smpl', methods=['GET', 'POST'])
def delete_pick_smpl(message=""):
    return render_template('/delete_pick_smpl.html', message=message)

#Confirm details before deleting
@app.route('/delete_confirm_details', methods=['GET', 'POST'])
def delete_confirm_details():
    smpl_no = ""
    unit = ""
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']
        unit = request.form['unit']
    if request.method == 'GET':
        smpl_no = request.args.get('smpl_no')
        unit = request.args.get('unit')

    smpl_no = smpl_no.replace(" ", "")
    incoming = Incoming.load_smpl_by_smpl_no(smpl_no)

    if incoming:
        cs_lst = []
        _cs_lst = []
        cs_id_lst = []
        _cs_lst = CurrentStock.load_smpl_by_smplno(smpl_no, unit)

        if _cs_lst:
            for cs_id, cs in _cs_lst:
                cs_id_lst.append(cs_id)
                cs_lst.append(cs)

        if len(cs_lst) > 0:
            return render_template('/delete_confirm_details.html', incoming=incoming, cs_lst=cs_lst)
        else:
            return render_template('/main_menu.html', message="SMPL No does not exist or not in stock")


@app.route('/delete_smpl_submit', methods=['GET', 'POST'])
def delete_smpl_submit():
    smpl_no = ""
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']
    if request.method == 'GET':
        smpl_no = request.args.get('smpl_no')

        # Establish a database connection
        connection = psycopg2.connect(
            dbname='smpl_prodn',
            user='postgres',
            password='smpl@509',
            host='localhost',
            port=5432
        )

        try:
            # Begin a transaction
            connection.autocommit = False
            cursor = connection.cursor()

            try:
                dispatch_detail = DispatchDetail.load_from_db(smpl_no)
                if dispatch_detail:
                    cursor.execute('delete from dispatch_detail where smpl_no = %s',(smpl_no,))
                processing_lst = Processing.load_history(smpl_no)
                if processing_lst:
                    '''for processing in processing_lst:
                        processing_detail = ProcessingDetail.load_history(processing.processing_id)
                        if processing_detail:
                            cursor.execute('delete from processing_detail where processing_id = %s',(smpl_no,))'''
                    cursor.execute('delete from processing where smpl_no = %s',(smpl_no,))

                cursor.execute('delete from current_stock where smpl_no = %s',(smpl_no,))
                cursor.execute('delete from incoming where smpl_no = %s',(smpl_no,))

                connection.commit()
            except (Exception, psycopg2.Error) as error:
                # Rollback the transaction if an error occurred
                connection.rollback()
                print("Error inserting data:", error)

                # Close the cursor
                cursor.close()

        except psycopg2.OperationalError as error:
            # Handle network errors
            print("Network error occurred:", error)
            print("Rolling back the transaction...")
            connection.rollback()
            return render_template('/main_menu.html', message="Not Deleted")
        finally:
            # Close the database connection
            connection.close()

        return render_template('/main_menu.html', message="SMPL No: " + smpl_no + " deleted.")


#Pick SMPL for adding weight to current stock
@app.route('/add_weight', methods=['GET', 'POST'])
def add_weight():
    return render_template('/add_weight_pick_smpl.html')

@app.route('/add_weight_list', methods=['GET', 'POST'])
def add_weight_list():

    smpl_no = ""
    unit = ""
    _cs_lst = []
    cs_lst = []
    cs_id_lst = []
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']
        unit = request.form['unit']

    if request.method == 'GET':
        smpl_no = request.args.get('smpl_no')
        unit = request.args.get('unit')


    _cs_lst = (CurrentStock.load_smpl_by_smplno(smpl_no, unit))

    if _cs_lst:
        for cs_id, cs in _cs_lst:
            cs_lst.append(cs)
            cs_id_lst.append(cs_id)
        return render_template('/add_weight_display_list.html', cs_lst=zip(cs_id_lst, cs_lst))
    else:
        return render_template('/main_menu.html', message=smpl_no + " not found.")


@app.route('/add_weight_submit', methods=['GET', 'POST'])
def add_weight_submit():
    smpl_no = ''
    if request.method == 'POST':
        smpl_no_lst = request.form.get['select_smpl']
        #current_wt = request.form.get['current_wt']
        _add_weight_lst = request.form.getlist['add_weight']
    if request.method == 'GET':
        smpl_no_lst = request.args.get('select_smpl')
        #current_wt = request.args.get('current_wt')
        _add_weight_lst = request.args.getlist('add_weight')

    add_weight_lst = list(filter(None, _add_weight_lst))

    smpl_details = smpl_no_lst.split(',')
    smpl_no = smpl_details[1]
    cs_id = smpl_details[0]
    current_wt = smpl_details[2]

    for add_wt in add_weight_lst:
        new_weight = Decimal(current_wt) + Decimal(add_wt)

        CurrentStock.add_weight(int(cs_id), new_weight)

    return render_template('/main_menu.html', message="Weight Changed.")

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
        _smpl_no = request.form['select_smpl']

    if request.method == 'GET':
        _smpl_no = request.args.get('select_smpl')

    _smpl_no = _smpl_no.split(',')
    smpl_no = _smpl_no[0]
    unit = _smpl_no[1]

    incoming = Incoming.load_smpl_by_smpl_no(smpl_no)


    current_stock = CurrentStock.load_smpl_by_smplno(smpl_no, unit)
    for cs_id, _current_stock in current_stock:
        cs = _current_stock

    return render_template('order.html', smpl_no=smpl_no, customer=incoming.customer, thickness=incoming.thickness,
                           width=incoming.width, length=incoming.length, grade=incoming.grade,
                           weight=cs.weight, numbers=incoming.numbers)


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
    order = Order(smpl_no, order_date, expected_date, processing_wt, "Open", header_remarks)
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
        incoming_new = Incoming(new_smpl_no, customer, incoming.incoming_date, thickness, width, length, grade, new_wt,
                                new_nos,
                                incoming.mill, incoming.mill_id, incoming.remarks, incoming.unit)
        incoming_new.savetodb()
        rm_status = CurrentStock.change_wt(smpl_no, width, length, new_wt, new_nos, "minus", "RM", 0)

    # The status of the smpl is updated in current_stock
    cs = CurrentStock(smpl_no, customer, available_wt, available_numbers, thickness, width, length, "RM", grade, "X")
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

    return render_template('/print_order.html', smpl_no=temp_print_order_string)


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
        _order_detail_lst = OrderDetail.load_from_db(smpl_no, order_id)
        order = _order

    for order_detail_id, order_detail in _order_detail_lst:
        order_detail_lst.append(order_detail)

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

    return render_template('view_order.html', smpl_no=smpl_no, customer=incoming.customer, thickness=incoming.thickness,
                           width=incoming.width, length=incoming.length, grade=incoming.grade,
                           weight=incoming.weight, numbers=incoming.numbers, order=order,
                           order_detail_lst=zip(order_detail_for_print_lst, operation_lst, ms_lst, proc_wt_lst,
                                                stage_no_lst))


# To load orders by machine to chose for processing
@app.route('/orders_by_machine', methods=['GET', 'POST'])
def orders_by_machine():
    operation = ""
    customer_type = ""
    cs_id_lst = []
    cs_lst = []
    if request.method == 'POST':
        operation = request.form['select_operation']
        customer_type = request.form['type']

    if request.method == 'GET':
        operation = request.args.get('select_operation')
        customer_type = request.args.get('type')

    if current_user.unit == 1 or current_user.unit == 2:
        smpl_for_processing_lst = CurrentStock.smpl_list_for_processing(operation, customer_type,
                                                                        str(current_user.unit))
        if smpl_for_processing_lst:
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
        else:
            return render_template('/main_menu.html', message="No raw material or WIP available!")

    if current_user.unit == 0:
        return render_template('/processing_pick_unit.html', operation=operation, type=customer_type)

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

    cs_lst = []
    cs_id_lst = []
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
        return render_template('processing_pick_smpl.html', cs_lst=zip(cs_id_lst, cs_lst), operation=operation)
    else:
        return render_template('/main_menu.html', message="No raw material or WIP available!")


@app.route('/processing_search', methods=['GET', 'POST'])
def processing_search():
    operation = ""
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

    smpl_for_processing_search_lst = CurrentStock.smpl_for_processing_search_lst(operation, smpl_no,
                                                                                 str(current_user.unit))

    if smpl_for_processing_search_lst:
        for cs_id, cs in smpl_for_processing_search_lst:
            cs_lst.append(cs)
            cs_id_lst.append(cs_id)

        return render_template('processing_pick_smpl.html', cs_lst=zip(cs_id_lst, cs_lst), operation=operation)

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

    processing_detail_lst = ProcessingDetail.load_from_db(cs_rm.smpl_no)

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

    if operation == 'Narrow_CTL':
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

    if operation == 'Trap_NCTL':
        return render_template('processing_trap_nctl.html', incoming=incoming, operation=operation,
                               processing_details_lst=processing_detail_lst, cs_rm=cs_rm, cs_rm_id=cs_rm_id)

    if operation == 'Trap_Reshearing':
        return render_template('processing_trap_reshearing.html', incoming=incoming, operation=operation,
                               processing_details_lst=processing_detail_lst, cs_rm=cs_rm, cs_rm_id=cs_rm_id)


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
    if operation == 'Levelling':
        return render_template('processing_levelling.html', incoming=incoming, operation=operation,
                               processing_details_lst=processing_detail_lst, cs_rm=cs_rm, cs_rm_id=cs_rm_id)


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
        # order_id = request.form['order_id']

        input_size = request.form['input_material']
        output_width_lst = request.form.getlist('output_width')
        output_length_lst = request.form.getlist('output_length')
        output_length2_lst = request.form.getlist('output_length2')
        # order_detail_id_lst = request.form.getlist('order_detail_id')

        fg_yes_no_lst = request.form.getlist('fg_yes_no')

        actual_no_of_pieces_lst = request.form.getlist('actual_no_of_pieces')
        packet_name_lst = request.form.getlist('packet_name')
        processed_wt_lst = request.form.getlist('processed_wt')
        remarks_lst = request.form.getlist('remarks')
        net_wt_lst = request.form.getlist('net_wt')
        second_customer_lst = request.form.getlist('second_customer')
        #sticker_txt = request.form['stickers']

        machine = request.form['machine']
        temp_machine = machine
        # I had originally wanted to keep operation in processing and machine in processing_detail diff
        # but this separation is only useful for unit 2 CTL where lamination causes an issue
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
        mat_type = request.form['mat_type']

        no_of_qc = request.form['no_of_qc']
        no_of_helpers = request.form['no_of_helpers']
        names_of_qc = request.form['names_of_qc']
        # names_of_helpers = request.form['names_of_helpers']
        # name_of_packer = request.form['name_of_packer']

        setting_date = request.form['setting_date']
        setting_start_time = request.form['setting_start_time']
        setting_end_time = request.form['setting_end_time']
        setting_time = request.form['setting_time']

        # total_processed_wt = Decimal(request.form['total_processed_wt'])
        total_processed_wt = Decimal(request.form['total_processed_wt'])
        # balance_proc_wt = Decimal(request.form['balance_wt'])
        total_cuts = int(request.form['total_cuts'])
        rm_wt = Decimal(request.form['input_weight'])
        cs_rm_id = request.form['cs_rm_id']

        # Establish a database connection
        connection = psycopg2.connect(
            dbname='smpl_prodn',
            user='postgres',
            password='smpl@509',
            host='localhost',
            port=5432
        )

        try:
            # Begin a transaction
            connection.autocommit = False
            cursor = connection.cursor()

            try:
                cs_rm = CurrentStock.csid_exists(cs_rm_id)

                if cs_rm is not None:
                    new_rm_wt = cs_rm.weight
                    new_rm_numbers = cs_rm.numbers
                    # Processing object created and saved to db
                    processing = Processing(smpl_no, op_for_hdr, processing_date, start_time, end_time, setting_start_time,
                                            setting_end_time, processing_time, setting_time, no_of_qc, no_of_helpers, names_of_qc,
                                            setting_date, total_processed_wt, total_cuts)

                    cursor.execute("insert into processing (smpl_no, operation, processing_date, start_time, "
                                   "end_time, setting_start_time, setting_end_time, production_time, setting_time, no_of_qc, "
                                   "no_of_helpers, names_of_qc,setting_date, total_processed_wt,"
                                   "total_cuts) values (%s, %s,%s, %s, "
                                   "%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)",
                                   (processing.smpl_no, processing.operation, processing.processing_date,
                                    processing.start_time, processing.end_time, processing.setting_start_time,
                                    processing.setting_end_time, processing.processing_time, processing.setting_time,
                                    processing.no_of_qc, processing.no_of_helpers, processing.names_of_qc,
                                    processing.setting_date,
                                    processing.total_processed_wt, processing.total_cuts))

                    cursor.execute("select processing_id from processing where oid= %s", (cursor.lastrowid,))
                    processing_id = cursor.fetchone()
                    #processing_id = processing.save_to_db()

                    # Slitting/Mini Slitting and CTL/Reshearing/NCTL are managed differently
                    if operation == "CTL" or operation == "CTL 2" or operation == "Reshearing" or operation == "Narrow_CTL" or \
                            operation == "Lamination" or operation == "Levelling" or operation == 'Trap_NCTL' or operation == 'Trap_Reshearing':
                        lamination_lst = request.form.getlist('lamination')
                        for output_width, output_length, output_length2, actual_no_of_pieces, packet_name, processed_wt, \
                            lamination, fg_yes_no, remarks, net_wt, second_customer in zip(output_width_lst,
                                                                                           output_length_lst, output_length2_lst,
                                                                  actual_no_of_pieces_lst,
                                                                  packet_name_lst, processed_wt_lst,
                                                                  lamination_lst, fg_yes_no_lst, remarks_lst, net_wt_lst,
                                                                    second_customer_lst):
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
                                                                     ms_length, fg_yes_no, output_length2)

                                cursor.execute(
                                    "insert into processing_detail (smpl_no, operation, machine, processing_id, input_width,"
                                    "input_length, cut_width, cut_length, processed_numbers, packet_name, processed_wt, "
                                    "remarks, status, cut_length2) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                    (processing_detail.smpl_no,
                                     processing_detail.operation,
                                     processing_detail.machine,
                                     processing_detail.processing_id,
                                     processing_detail.input_width,
                                     processing_detail.input_length,
                                     processing_detail.cut_width,
                                     processing_detail.cut_length,
                                     processing_detail.processed_numbers,
                                     processing_detail.packet_name,
                                     processing_detail.processed_wt,
                                     processing_detail.remarks,
                                     processing_detail.status,
                                     processing_detail.cut_length2))
                                #processing_detail.save_to_db()

                                if operation == "Reshearing":
                                    # For reshearing, the mother material no. of pieces consumed have to be calculated and scrap
                                    # per mother piece has to be calculated and subtracted from the weight
                                    ms_weight = round(
                                        (Decimal(thickness) * Decimal(ms_width) * Decimal(ms_length) * Decimal(0.00000785)), 3)
                                    output_weight = round(
                                        (Decimal(thickness) * Decimal(output_length) * Decimal(output_width) * Decimal(0.00000785)),
                                        3)
                                    # Calculate no of pieces got per mother sheet and then divide by no of output pieces to get
                                    # no. of mother sheets consumed
                                    no_of_pieces_per_ms = round((ms_weight / output_weight), 0)
                                    no_of_ms_consumed = round((int(actual_no_of_pieces) / no_of_pieces_per_ms), 0)

                                    # I am not handling scrap as of now because I don't know if the balance width is to be returned
                                    # as balance or scrap. I have to think of how to do this.
                                    # For scrap per mother sheet
                                    # scrap_per_ms = (ms_weight - (output_weight*no_of_pieces_per_ms))
                                    # total_scrap = Decimal(scrap_per_ms) * Decimal(no_of_ms_consumed) / Decimal(1000)

                                    # the weight of RM to be reduced is the weight of FG + the scrap generated
                                    # rm_processed_wt = Decimal(processed_wt) + round(total_scrap,3)

                                    new_rm_weight = Decimal(processed_wt)

                                elif operation == "Narrow_CTL":
                                    no_of_ms_consumed = 0
                                    new_rm_weight = processed_wt

                                elif operation == "CTL" or operation == "CTL 2":
                                    no_of_ms_consumed = 0
                                    new_rm_weight = processed_wt

                                else:
                                    no_of_ms_consumed = actual_no_of_pieces
                                    new_rm_weight = processed_wt

                                # Reduce weight of mother material by the processed weight of cut material - balance weight remaining in the mother material
                                # rm_processed_wt = Decimal(rm_processed_wt) + balance_proc_wt

                                if Decimal(new_rm_weight) > Decimal(-0.03)*Decimal(cs_rm.weight):
                                    #rm_status = CurrentStock.change_wt(smpl_no, ms_width, ms_length, rm_processed_wt,
                                    #                                   no_of_ms_consumed, "minus", cs_rm.status, cs_rm.length2)
                                    ########################################################################################
                                    # Change wt of RM in current stock


                                    sign = 'minus'
                                    #length = ms_length
                                    if packet_name == "":
                                        cursor.execute(
                                            "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                                            "and length = %s and status = %s and length2 = %s",
                                            (smpl_no, ms_width, ms_length, cs_rm.status, cs_rm.length2))
                                        user_data = cursor.fetchone()
                                    else:
                                        cursor.execute(
                                            "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                                            "and length = %s and status = %s and packet_name = %s and length2 = %s",
                                            (smpl_no, ms_width, ms_length, cs_rm.status, cs_rm.packet_name, cs_rm.length2))
                                        user_data = cursor.fetchone()
                                    if user_data:
                                        weight = Decimal(user_data[0])
                                        numbers = Decimal(user_data[1])
                                        cs_id = int(user_data[3])
                                        new_rm_weight = weight - Decimal(processed_wt)
                                        new_rm_weight = round(new_rm_weight, 3)
                                        if numbers > 1:
                                            new_numbers = numbers - Decimal(no_of_ms_consumed)
                                        else:
                                            new_numbers = numbers
                                        #if (new_weight < 0.5 and sign == "minus" and Decimal(ms_length) == 0) or (
                                        #        (new_weight < 0.2) and sign == "minus" and Decimal(ms_length) > 0):
                                            # OrderDetail.complete_processing_on_del(smpl_no, width, length)
                                            # CurrentStock.delete_record(cs_id)

                                        #    cursor.execute("delete from current_stock where cs_id = %s", (cs_id,))

                                            # This is done when the RM is over but for some reason the order could not be completed
                                            # This could when the RM is thickness is more or wrong calc of material or processing mistake/change


                                        #else:
                                        cursor.execute(
                                            "update current_stock set weight = %s, numbers = %s where cs_id = %s",
                                            (new_rm_weight, new_numbers, cs_id))



                                # if rm_status == "complete":
                                # This is done when the RM is over but for some reason the order could not be completed
                                # This could when the RM is thickness is more or wrong calc of material or processing mistake/change
                                # OrderDetail.complete_processing_on_del(smpl_no, ms_width, ms_length)

                                # Unit of the material is decided based on the machine used to process the material.
                                # WARNING: This is bad programming
                                if machine.startswith(
                                        "CTL 2") or machine == "Slitting" or machine == "Mini_Slitting" or \
                                        machine == "Reshearing 5" or machine == "Reshearing 6" or machine == "Reshearing 7" or \
                                        machine == "Reshearing 9" or machine == "NCTL 2" or machine == "NCTL 3" or machine == "NCTL 4" or \
                                        machine == "NCTL 5" or machine == "NCTL 1":
                                    unit = '2'

                                else:
                                    unit = '1'


                                # Increase weight of cut material by processed weight. If cut material, doesn't already exist, the
                                # function returns insert => a new record has to be inserted
                                if (fg_yes_no == "FG"):
                                    _packet_name = packet_name
                                else:
                                    _packet_name = "WIP"

                                #cc_insert = CurrentStock.change_wt(smpl_no, output_width, output_length, processed_wt,
                                #                                   actual_no_of_pieces, "plus", fg_yes_no,output_length2,
                                #                                   _packet_name)


                                ############################################################################################
                                # Change weight or insert output of processing in to current_stock
                                sign = 'plus'
                                if _packet_name == "":
                                    cursor.execute(
                                        "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                                        "and length = %s and status = %s and length2 = %s",
                                        (smpl_no, output_width, output_length, fg_yes_no, output_length2))
                                    user_data = cursor.fetchone()
                                else:
                                    cursor.execute(
                                        "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                                        "and length = %s and status = %s and packet_name = %s and length2 = %s",
                                        (smpl_no, output_width, output_length, fg_yes_no, _packet_name, output_length2))
                                    user_data = cursor.fetchone()
                                if user_data and fg_yes_no != 'FG':
                                    weight = Decimal(user_data[0])
                                    numbers = Decimal(user_data[1])
                                    cs_id = int(user_data[3])

                                    if sign == "plus":
                                        new_weight = weight + Decimal(processed_wt)
                                        new_weight = round(new_weight, 3)
                                        # if numbers > 1:
                                        new_numbers = numbers + Decimal(actual_no_of_pieces)
                                        # else:
                                        #    new_numbers = numbers

                                    if (new_weight < (Decimal('0.02') * rm_wt) and sign == "minus" and Decimal(output_length) == 0) or (
                                            (new_weight < (Decimal('0.02') * rm_wt)) and sign == "minus" and Decimal(output_length) > 0):
                                        # OrderDetail.complete_processing_on_del(smpl_no, width, length)
                                        # CurrentStock.delete_record(cs_id)

                                        cursor.execute("delete from current_stock where cs_id = %s", (cs_id,))

                                    else:
                                        cursor.execute(
                                            "update current_stock set weight = %s, numbers = %s where cs_id = %s",
                                            (new_weight, new_numbers, cs_id))

                                else:
                                    cs_cc = CurrentStock(smpl_no, customer, processed_wt, actual_no_of_pieces, thickness,
                                                         output_width, output_length, fg_yes_no, grade, unit, _packet_name,
                                                         output_length2, processing_date, processing_id[0],
                                                         second_customer, net_wt)
                                    cursor.execute(
                                        "insert into current_stock (smpl_no,weight,numbers,width,length,status,customer,thickness"
                                        ",grade, unit, packet_name, length2, date, processing_id, second_customer, net_wt) "
                                        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (cs_cc.smpl_no, cs_cc.weight, cs_cc.numbers, cs_cc.width, cs_cc.length, cs_cc.status,
                                         cs_cc.customer,
                                         cs_cc.thickness, cs_cc.grade, cs_cc.unit, cs_cc.packet_name, cs_cc.length2,
                                         cs_cc.date,cs_cc.processing_id,cs_cc.second_customer, cs_cc.net_wt))





                                # The new material is inserted in to current stock
                                '''if cc_insert == "insert":
                                    cs_cc = CurrentStock(smpl_no, customer, processed_wt, actual_no_of_pieces, thickness,
                                                         output_width, output_length, fg_yes_no, grade, unit, packet_name,
                                                         output_length2)
                                    cs_cc.save_to_db()'''

                                # This checks if detail is complete by comparing the processed weight and order detail weight.
                                # If the order detail is complete, it checks if all the order details in that stage are complete (check_stage_complete)
                                # If all the order details in that stage are complete, it makes the order details of the next stage ready for production
                                # If this is the last stage of the order, it marks the order as closed
                                # OrderDetail.detail_complete(order_detail_id)
                    wt_factor = Decimal('0.02')
                    if rm_wt < 5:
                        wt_factor = Decimal('0.07')
                    if rm_wt < 10 and rm_wt > 5:
                        wt_factor = Decimal('0.05')
                    if rm_wt < 15 and rm_wt > 10:
                        wt_factor = Decimal('0.04')


                    if (new_rm_weight < ((wt_factor) * rm_wt) and Decimal(ms_length) == 0) or (
                            (new_rm_weight < ((wt_factor) * rm_wt)) and Decimal(ms_length) > 0):
                        # OrderDetail.complete_processing_on_del(smpl_no, width, length)
                        # CurrentStock.delete_record(cs_id)

                        cursor.execute("delete from current_stock where cs_id = %s", (cs_rm_id,))
                    connection.commit()
                    print("Data inserted successfully!")
                else:
                    return render_template('/main_menu.html',
                                           message=Markup("Entry Failed. Please check RM weight"))


            except (Exception, psycopg2.Error) as error:
                # Rollback the transaction if an error occurred
                connection.rollback()
                print("Error inserting data:", error)

                # Close the cursor
                return render_template('/main_menu.html', message="Processing Entry not completed")
            cursor.close()

        except psycopg2.OperationalError as error:
            # Handle network errors
            print("Network error occurred:", error)
            print("Rolling back the transaction...")
            connection.rollback()
            return render_template('/main_menu.html', message="Processing Entry not completed")
        finally:
            # Close the database connection
            connection.close()

        return render_template('/main_menu.html', message="Processing for " + smpl_no + " entered.")


@app.route("/submit_slitting_processing", methods=['GET', 'POST'])
def submit_slitting_processing():
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']
        operation = request.form['operation']
        # order_id = request.form['order_id']

        input_size = request.form['input_material']
        output_width_lst = request.form.getlist('output_width')
        width_name_lst = request.form.getlist('width_name')
        # order_detail_id_lst = request.form.getlist('order_detail_id')
        fg_yes_no_lst = request.form.getlist('fg_yes_no')

        part_length_lst = request.form.getlist('part_length')
        part_name_lst = request.form.getlist('part_name')

        fg_net_wt_lst = request.form.getlist('lbl_net_wt')
        fg_packet_name_lst = request.form.getlist('lbl_packet_name')
        fg_size_lst = request.form.getlist('lbl_size')
        fg_second_customer_lst = request.form.getlist('lbl_2nd_customer')


        # processed_wt_lst = request.form.getlist('processed_wt')
        # remarks = request.form['remarks']
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
        mat_type = request.form['mat_type']

        no_of_qc = request.form['no_of_qc']
        no_of_helpers = request.form['no_of_helpers']
        fg_id = request.form['fg_id']
        names_of_qc = request.form['names_of_qc']
        # names_of_helpers = request.form['names_of_helpers']
        # name_of_packer = request.form['name_of_packer']
        # names_of_qc = ''

        setting_date = request.form['setting_date']
        setting_start_time = request.form['setting_start_time']
        setting_end_time = request.form['setting_end_time']
        setting_time = request.form['setting_time']

        # total_processed_wt = Decimal(request.form['total_processed_wt'])
        total_processed_wt = Decimal(request.form['total_processed_wt'])
        # balance_proc_wt = Decimal(request.form['balance_wt'])
        total_length = int(request.form['total_length'])
        rm_wt = Decimal(request.form['input_weight'])
        cs_rm_id = request.form['cs_rm_id']
        # Establish a database connection
        connection = psycopg2.connect(
            dbname='smpl_prodn',
            user='postgres',
            password='smpl@509',
            host='localhost',
            port=5432
        )

        try:
            # Begin a transaction
            connection.autocommit = False
            cursor = connection.cursor()

            try:
                cs_rm = CurrentStock.csid_exists(cs_rm_id)

                if cs_rm is not None:
                    new_rm_weight = cs_rm.weight
                    new_rm_numbers = cs_rm.numbers

                    # Processing object created and saved to db
                    processing = Processing(smpl_no, operation, processing_date, start_time, end_time, setting_start_time,
                                            setting_end_time, processing_time, setting_time, no_of_qc, no_of_helpers, names_of_qc,
                                            setting_date, total_processed_wt, total_length)
                    #processing_id = processing.save_to_db()

                    cursor.execute("insert into processing (smpl_no, operation, processing_date, start_time, "
                                   "end_time, setting_start_time, setting_end_time, production_time, setting_time, no_of_qc, "
                                   "no_of_helpers, names_of_qc,setting_date, total_processed_wt,"
                                   "total_cuts) values (%s, %s,%s, %s, "
                                   "%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)",
                                   (processing.smpl_no, processing.operation, processing.processing_date,
                                    processing.start_time, processing.end_time, processing.setting_start_time,
                                    processing.setting_end_time, processing.processing_time, processing.setting_time,
                                    processing.no_of_qc, processing.no_of_helpers, processing.names_of_qc,
                                    processing.setting_date,
                                    processing.total_processed_wt, processing.total_cuts))

                    cursor.execute("select processing_id from processing where oid= %s", (cursor.lastrowid,))
                    processing_id = cursor.fetchone()

                    ip_size = input_size.split('x')
                    ms_width = Decimal(ip_size[0])
                    ms_length = Decimal(ip_size[1])

                    # For Slitting unit will be unit 2
                    unit = '2'

                    for output_width, width_name, fg_yes_no in zip(output_width_lst, width_name_lst, fg_yes_no_lst):
                        for part_length, part_name in zip(part_length_lst, part_name_lst):
                            output_length = 0
                            output_length2 = 0
                            processed_numbers = 1
                            output_width = Decimal(output_width)

                            packet_name = part_name + width_name
                            part_weight = Decimal(thickness * float(output_width) * float(part_length) * 0.00000785)
                            if "ALUMINIUM " in mat_type or "ALU " in mat_type:
                                part_weight = Decimal(thickness * float(output_width) * float(part_length) * 0.0000027)
                            part_weight = round(part_weight, 3)

                            _remarks = "FG ID:" + fg_id + remarks
                            processing_detail = ProcessingDetail(smpl_no, operation, machine, processing_id, output_width,
                                                                 output_length, processed_numbers, packet_name, _remarks,
                                                                 part_weight,
                                                                 ms_width, ms_length, fg_yes_no, output_length2)

                            cursor.execute(
                                "insert into processing_detail (smpl_no, operation, machine, processing_id, input_width,"
                                "input_length, cut_width, cut_length, processed_numbers, packet_name, processed_wt, "
                                "remarks, status, cut_length2) values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                                (processing_detail.smpl_no,
                                 processing_detail.operation,
                                 processing_detail.machine,
                                 processing_detail.processing_id,
                                 processing_detail.input_width,
                                 processing_detail.input_length,
                                 processing_detail.cut_width,
                                 processing_detail.cut_length,
                                 processing_detail.processed_numbers,
                                 processing_detail.packet_name,
                                 processing_detail.processed_wt,
                                 processing_detail.remarks,
                                 processing_detail.status,
                                 processing_detail.cut_length2))

                            #processing_detail.save_to_db()

                            _remarks = ''

                            # Reduce weight of mother material by the processed weight of cut material
                            # In case of rewinding, there is the RM and the FG which have the same size.
                            # This check has been added so that weight is deducted from the RM only

                            if Decimal(new_rm_weight) > Decimal(-0.03)*Decimal(cs_rm.weight):
                                # rm_status = CurrentStock.change_wt(smpl_no, ms_width, ms_length, part_weight, processed_numbers,
                                #                                   "minus", cs_rm.status, 0, cs_rm.packet_name)

                                ########################################################################################
                                # Change wt of RM in current stock

                                sign = 'minus'

                                '''if packet_name == "":
                                    cursor.execute(
                                        "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                                        "and length = %s and status = %s and length2 = %s",
                                        (smpl_no, ms_width, ms_length, cs_rm.status, cs_rm.length2))
                                    user_data = cursor.fetchone()
                                else:
                                    cursor.execute(
                                        "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                                        "and length = %s and status = %s and packet_name = %s and length2 = %s",
                                        (smpl_no, ms_width, ms_length, cs_rm.status, cs_rm.packet_name, cs_rm.length2))
                                    user_data = cursor.fetchone()
                                if user_data:
                                    weight = Decimal(user_data[0])
                                    numbers = Decimal(user_data[1])
                                    cs_id = int(user_data[3])'''
                                new_rm_weight = new_rm_weight - Decimal(part_weight)
                                new_rm_weight = round(new_rm_weight, 3)
                                if new_rm_numbers > 1:
                                    new_rm_numbers = new_rm_numbers - Decimal(part_weight)
                                else:
                                    new_rm_numbers = new_rm_numbers
                                #if (new_rm_weight < 0.5 and sign == "minus" and Decimal(ms_length) == 0):
                                    # OrderDetail.complete_processing_on_del(smpl_no, width, length)
                                    # CurrentStock.delete_record(cs_id)

                                    '''cursor.execute("delete from current_stock where cs_id = %s", (cs_rm_id,))
                                    new_rm_weight = 0'''
                                    # This is done when the RM is over but for some reason the order could not be completed
                                    # This could when the RM is thickness is more or wrong calc of material or processing mistake/change


                                #else:
                                cursor.execute(
                                    "update current_stock set weight = %s, numbers = %s where cs_id = %s",
                                    (new_rm_weight, new_rm_numbers, cs_rm_id))


                                # The issue is during rewinding since mother coil and output width & length remain the same,
                                # The weight is getting added and subtracted from the same current_stock record.
                                # not equal. Else, it will directly jump to insert. This might cause multiple current_stock records
                                # To avoid this; the change wt "plus" for output will only happen if the output width and ms width are
                                # for the same size but till I come up with a better solution so be it.

                                if ms_width != output_width:
                                    # Increase weight of cut material by processed weight. If cut material, doesn't already exist, the
                                    # function returns insert => a new record has to be inserted

                                    if fg_yes_no == "FG":
                                        _packet_name = packet_name
                                    else:
                                        _packet_name = "WIP"

                                    # cc_insert = CurrentStock.change_wt(smpl_no, output_width, output_length, part_weight,
                                    #                                   processed_numbers, "plus", fg_yes_no, 0, packet_name)

                                    ############################################################################################
                                    # Change weight or insert output of processing in to current_stock

                                    sign = 'plus'
                                    if _packet_name == "WIP":
                                        cursor.execute(
                                            "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                                            "and length = %s and status = %s and length2 = %s",
                                            (smpl_no, output_width, output_length, fg_yes_no, output_length2))
                                        user_data = cursor.fetchone()
                                    else:
                                        cursor.execute(
                                            "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                                            "and length = %s and status = %s and packet_name = %s and length2 = %s",
                                            (smpl_no, output_width, output_length, fg_yes_no, _packet_name, output_length2))

                                        user_data = cursor.fetchone()
                                    if user_data:
                                        weight = Decimal(user_data[0])
                                        numbers = Decimal(user_data[1])
                                        cs_id = int(user_data[3])
                                        if sign == "plus":
                                            new_weight = weight + Decimal(part_weight)
                                            new_weight = round(new_weight, 3)
                                            # if numbers > 1:
                                            new_numbers = numbers + Decimal(processed_numbers)
                                            # else:
                                            #    new_numbers = numbers

                                        if (new_weight < ((Decimal('0.02') * rm_wt)) and sign == "minus" and Decimal(output_length) == 0):
                                            # OrderDetail.complete_processing_on_del(smpl_no, width, length)
                                            # CurrentStock.delete_record(cs_id)

                                            cursor.execute("delete from current_stock where cs_id = %s", (cs_id,))

                                        else:
                                            cursor.execute(
                                                "update current_stock set weight = %s, numbers = %s where cs_id = %s",
                                                (new_weight, new_numbers, cs_id))

                                    else:
                                        #cc_insert = "insert"
                                        second_customer = ''
                                        net_wt = 0
                                        for fg_packet_name, fg_size, fg_net_wt, fg_second_customer in zip(fg_packet_name_lst,
                                                                                                          fg_size_lst,
                                                                                                          fg_net_wt_lst,
                                                                                                          fg_second_customer_lst):

                                            if fg_packet_name == _packet_name:
                                                second_customer = fg_second_customer
                                                net_wt = fg_net_wt

                                        if net_wt == '':
                                            net_wt = 0

                                        cs_cc = CurrentStock(smpl_no, customer, part_weight, processed_numbers, thickness,
                                                             output_width, output_length, fg_yes_no, grade, unit, _packet_name,
                                                             output_length2, processing_date, processing_id[0], second_customer, net_wt)
                                        cursor.execute(
                                            "insert into current_stock (smpl_no,weight,numbers,width,length,status,customer,thickness"
                                            ",grade, unit, packet_name, length2, date, processing_id, second_customer, net_wt) "
                                            "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                            (
                                            cs_cc.smpl_no, cs_cc.weight, cs_cc.numbers, cs_cc.width, cs_cc.length, cs_cc.status,
                                            cs_cc.customer,
                                            cs_cc.thickness, cs_cc.grade, cs_cc.unit, cs_cc.packet_name, cs_cc.length2,
                                            cs_cc.date, cs_cc.processing_id, cs_cc.second_customer, cs_cc.net_wt))

                                # If rewinding insert FG as new stock
                                else:
                                    # cc_insert = "insert"
                                    if fg_yes_no == "FG":
                                        _packet_name = packet_name
                                    else:
                                        _packet_name = "WIP"


                                    second_customer = ''
                                    net_wt = 0
                                    for fg_packet_name, fg_size, fg_net_wt, fg_second_customer in zip(
                                            fg_packet_name_lst,
                                            fg_size_lst,
                                            fg_net_wt_lst,
                                            fg_second_customer_lst):

                                        if fg_packet_name == _packet_name:
                                            second_customer = fg_second_customer
                                            net_wt = fg_net_wt

                                    if net_wt == '':
                                        net_wt = 0



                                    cs_cc = CurrentStock(smpl_no, customer, part_weight, processed_numbers, thickness,
                                                         output_width, output_length, fg_yes_no, grade, unit,
                                                         packet_name,
                                                         output_length2, processing_date, processing_id[0], second_customer, net_wt)
                                    cursor.execute(
                                        "insert into current_stock (smpl_no,weight,numbers,width,length,status,customer,thickness"
                                        ",grade, unit, packet_name, length2, date, processing_id, second_customer, net_wt) "
                                        "values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                                        (
                                            cs_cc.smpl_no, cs_cc.weight, cs_cc.numbers, cs_cc.width, cs_cc.length,
                                            cs_cc.status,
                                            cs_cc.customer,
                                            cs_cc.thickness, cs_cc.grade, cs_cc.unit, cs_cc.packet_name, cs_cc.length2,
                                            cs_cc.date, cs_cc.processing_id, cs_cc.second_customer, cs_cc.net_wt))

                                # Unit of the material is decided based on the machine used to process the material.
                                # WARNING: This is bad programming
                                #unit = '2'

                                # The new material is added to current stock
                                # In case of new material one more check in case material already exists. THis is especially for
                                # rewinding when FG and RM have the same size
                                '''if cc_insert == "insert":
                                    cs_cc = CurrentStock(smpl_no, customer, part_weight, processed_numbers, thickness,
                                                         output_width, output_length, fg_yes_no, grade, unit, packet_name,
                                                         output_length2)
                                    if cs_cc.check_if_size_exists():
                                        if fg_yes_no == "FG":
                                            CurrentStock.change_wt(cs_cc.smpl_no, cs_cc.width, cs_cc.length, cs_cc.weight,
                                                                   cs_cc.numbers, "plus", fg_yes_no, 0, packet_name)
                                        if fg_yes_no == "WIP":
                                            CurrentStock.change_wt(cs_cc.smpl_no, cs_cc.width, cs_cc.length, cs_cc.weight,
                                                                   cs_cc.numbers, "plus", fg_yes_no, 0)
                                    else:
                                        cs_cc.save_to_db()'''

                            else:
                                return render_template('/main_menu.html',
                                                       message=Markup("Entry Failed. Please check RM weight"))

                            wt_factor = Decimal('0.02')
                            if rm_wt < 5:
                                wt_factor = Decimal('0.07')
                            if rm_wt < 10 and rm_wt > 5:
                                wt_factor = Decimal('0.05')
                            if rm_wt < 15 and rm_wt > 10:
                                wt_factor = Decimal('0.04')

                            if (new_rm_weight < (Decimal(wt_factor) * rm_wt)):
                                # OrderDetail.complete_processing_on_del(smpl_no, width, length)
                                # CurrentStock.delete_record(cs_id)

                                cursor.execute("delete from current_stock where cs_id = %s", (cs_rm_id,))

                    connection.commit()
                    print("Data inserted successfully!")

                else:
                    return render_template('/main_menu.html', message=Markup("Entry Failed. Please check RM weight"))
            except (Exception, psycopg2.Error) as error:
                # Rollback the transaction if an error occurred
                connection.rollback()
                print("Entry Failed:", error)
                return render_template('/main_menu.html', message="Processing Entry not completed")
                # Close the cursor
            cursor.close()

        except psycopg2.OperationalError as error:
            # Handle network errors
            print("Network error occurred:", error)
            print("Rolling back the transaction...")
            connection.rollback()
            return render_template('/main_menu.html', message="Entry Failed")
        finally:
            # Close the database connection
            connection.close()

        return render_template('/main_menu.html', message=Markup("Processing for " + smpl_no + " entered"))


@app.route('/process_data', methods=['POST'])
def process_sticker_background():
    # Get data sent from the client
    data = request.json

    sticker_txt = data['fieldName']
    sticker_txt = sticker_txt.split(';;')

    # Establish a database connection
    connection = psycopg2.connect(
        dbname='smpl_prodn',
        user='postgres',
        password='smpl@509',
        host='localhost',
        port=5432
    )

    try:
        # Begin a transaction
        connection.autocommit = False
        cursor = connection.cursor()

        try:
            cursor.execute('insert into sticker (smpl_no, prod_date, customer, machine, size, numbers, packet_name, '
                           'lamination, mill_id, grade, mill, comment, second_customer, material_type, scams_no, coating, '
                           'part_no, batch_no, net_wt, gross_wt, top_comment, format_size, mat_status, qc_name) values'
                           ' (%s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s, %s, %s,%s, %s)',
                           (sticker_txt[0], sticker_txt[1], sticker_txt[2], sticker_txt[3], sticker_txt[4], sticker_txt[5],
                                  sticker_txt[6], sticker_txt[7], sticker_txt[8], sticker_txt[9], sticker_txt[10],
                                  sticker_txt[11],sticker_txt[12], sticker_txt[13], sticker_txt[14], sticker_txt[15],
                                  sticker_txt[16], sticker_txt[17], sticker_txt[18], sticker_txt[19], sticker_txt[20],
                                  sticker_txt[21], sticker_txt[22], sticker_txt[23]))

        except (Exception, psycopg2.Error) as error:
            # Rollback the transaction if an error occurred
            connection.rollback()
            print("Error inserting data:", error)

        # Close the cursor
        connection.commit()
        cursor.close()

    except psycopg2.OperationalError as error:
        # Handle network errors
        print("Network error occurred:", error)
        print("Rolling back the transaction...")
        connection.rollback()


    finally:
        # Close the database connection
        connection.close()


    # Return a response to the client
    return jsonify('')


@app.route('/make_label_hist', methods=['GET', 'POST'])
def make_label_hist():
    processing_id = 0
    if request.method == 'POST':
        processing_id = request.form['processing_id']

    if request.method == 'GET':
        processing_id = request.args.get('processing_id')
    return render_template('make_label.html')

@app.route('/print_label', methods=['GET', 'POST'])
def print_label():
    processing_id = 0
    if request.method == 'POST':
        processing_id = request.form['processing_id']

    if request.method == 'GET':
        processing_id = request.args.get('processing_id')
    return render_template('print_label.html')

@app.route('/print_label_slit', methods=['GET', 'POST'])
def print_label_slit():
    processing_id = 0
    if request.method == 'POST':
        processing_id = request.form['processing_id']

    if request.method == 'GET':
        processing_id = request.args.get('processing_id')
    return render_template('print_label_slit.html')


@app.route('/print_label_big', methods=['GET', 'POST'])
def print_label_big():
    processing_id = 0
    if request.method == 'POST':
        processing_id = request.form['processing_id']

    if request.method == 'GET':
        processing_id = request.args.get('processing_id')
    return render_template('print_label_big.html')

@app.route('/print_label_tsl', methods=['GET', 'POST'])
def print_label_tsl():
    processing_id = 0
    if request.method == 'POST':
        processing_id = request.form['processing_id']

    if request.method == 'GET':
        processing_id = request.args.get('processing_id')
    return render_template('print_label_tsl.html')


@app.route('/print_label_reshearing', methods=['GET', 'POST'])
def print_label_reshearing():
    processing_id = 0
    if request.method == 'POST':
        processing_id = request.form['processing_id']

    if request.method == 'GET':
        processing_id = request.args.get('processing_id')
    return render_template('print_label_reshearing.html')


@app.route('/check_stock', methods=['GET', 'POST'])
def check_stock():

    return render_template('check_stock.html')

@app.route('/check_stock_by_customer', methods=['GET', 'POST'])
def check_stock_by_customer():

    customer_lst = []
    customer_lst = CurrentStock.customer_list_for_stock()

    return render_template('stock_summary_by_customer.html', cs_lst = customer_lst)

@app.route('/get_stock_full_by_customer', methods=['GET', 'POST'])
def get_stock_full_by_customer():

    if request.method == 'POST':
        customer_input = request.form['customer']
    if request.method == 'GET':
        customer_input = request.args.get('customer').lstrip(' ')


    customer = unquote(customer_input)
    customer = customer.strip()
    cs_lst = []
    _cs_lst = []
    cs_lst = CurrentStock.get_stock_by_customer(customer, 'All')
    cs_id_lst = []

    for cs_id, cs in cs_lst:
        cs_id_lst.append(cs_id)
        _cs_lst.append(cs)


    return render_template('stock_display.html', cs_lst = zip(cs_id_lst, _cs_lst))



@app.route('/check_stock_ttssi_fg', methods=['GET', 'POST'])
def check_stock_ttssi_fg():
    _cs_lst = []
    _cs_id_lst = []
    cs_lst = []
    cs_509_lst = []
    scams_no_lst = []

    cs_lst = CurrentStock.get_stock_by_customer('TT STEEL SERVICE INDIA PVT.LTD.', 'FGandWIP')
    cs_509_lst = (CurrentStock.get_stock_by_customer('TT STEEL SERVICE INDIA PVT.LTD [ #509 ]', 'FGandWIP'))
    #cs_lst.append(CurrentStock.get_stock_by_customer('TT STEEL SERVICE INDIA PVT LTD', 'FG'))

    for cs_id, cs in cs_lst:
        _cs_id_lst.append(cs_id)
        _cs_lst.append(cs)
        scams_no = cs.grade.split('SCAMS NO')
        if len(scams_no) > 1:
            scams_no = scams_no[1]
            scams_no = scams_no.replace(':', '')
            scams_no = scams_no.replace(';', '')
            scams_no = scams_no.replace('.', '')
            scams_no = scams_no.replace(' ', '')
            scams_no_lst.append(scams_no)
        else:
            scams_no_lst.append('')

    for cs_id, cs in cs_509_lst:
        _cs_id_lst.append(cs_id)
        _cs_lst.append(cs)
        scams_no = cs.grade.split('SCAMS NO')
        if len(scams_no) > 1:
            scams_no = scams_no[1]
            scams_no = scams_no.replace(':', '')
            scams_no = scams_no.replace(';', '')
            scams_no = scams_no.replace('.', '')
            scams_no = scams_no.replace(' ', '')
            scams_no_lst.append(scams_no)
        else:
            scams_no_lst.append('')

    cs_lst = zip(_cs_id_lst, _cs_lst, scams_no_lst)
    return render_template('stock_display_ttssi.html', cs_lst=cs_lst)

@app.route('/check_stock_htid', methods=['GET', 'POST'])
def check_stock_htid():
    _cs_lst = []
    _cs_id_lst = []
    cs_lst = []
    part_no_lst = []
    wt_per_sheet_lst = []
    coating_lst = []
    packet_wt_lst = []
    mill_lst = []
    mill_id_lst = []
    incoming_date_lst = []
    dc_number_lst = []
    dc_date_lst = []


    part_no = ""
    coating = ""
    wt_per_sheet = 0
    packet_wt = 0

    cs_lst = CurrentStock.get_stock_by_customer('HONDA TRADING CORPORATION INDIA PVT LTD', 'All')

    for cs_id, cs in cs_lst:
        if not any(substring in cs.packet_name for substring in ['W0P0', 'D0', 'M0']):
            _cs_id_lst.append(cs_id)
            _cs_lst.append(cs)
            if cs.width == 720 and cs.length == 745:
                part_no = "K0NA PLATE BOTTOM"
                wt_per_sheet = 3.37
                coating = "20/0"
            if cs.width == 600 and cs.length == 820:
                part_no = "K0NA OUTER R/L"
                wt_per_sheet = 3.09
                coating = "0/20"
            if cs.width == 370 and cs.length == 415:
                part_no = "K0LA+K0PA+K0YA, Tank Upper"
                wt_per_sheet = 0.97
                coating = "0/20"
            if cs.width == 430 and cs.length == 455:
                part_no = "K0LA+K0PA+K0YA, Tank Lower"
                wt_per_sheet = 1.23
                coating = "0/20"
            if cs.width == 570 and cs.length == 830:
                part_no = "K1KA R/L"
                wt_per_sheet = 2.97
                coating = "0/20"
            if cs.width == 600 and cs.length == 715:
                part_no = "K1KA PLATE BOTTOM"
                wt_per_sheet = 2.69
                coating = "20/0"
            if cs.width == 550 and cs.length == 790:
                part_no = "K1CA TANK R/L"
                wt_per_sheet = 2.73
                coating = "0/20"
            if cs.width == 590 and cs.length == 705:
                part_no = "K1CA TANK BOTTOM"
                wt_per_sheet = 2.61
                coating = "20/0"
            if cs.width == 530 and cs.length == 765:
                part_no = "K67 OUTER R/L"
                wt_per_sheet = 2.55
                coating = "0/20"
            if cs.width == 575 and cs.length == 640:
                part_no = "K67 PLATE BOTTOM"
                wt_per_sheet = 2.31
                coating = "20/0"
            if cs.width == 510 and cs.length == 785:
                part_no = "K0VA OUTER R/L"
                wt_per_sheet = 2.50
                coating = "0/20"
            if cs.width == 600 and cs.length == 660:
                part_no = "K0VA PLATE BOTTOM"
                wt_per_sheet = 2.29
                coating = "20/0"
            if cs.width == 520 and cs.length == 765:
                part_no = "KTE TANK R/L"
                wt_per_sheet = 2.50
                coating = "0/20"
            if cs.width == 565 and cs.length == 645:
                part_no = "KTE TANK BOTTOM"
                wt_per_sheet = 2.29
                coating = "20/0"
            if cs.width == 515 and cs.length == 715:
                part_no = "K1EA TANK R/L"
                wt_per_sheet = 2.31
                coating = "0/20"
            if cs.width == 620 and cs.length == 675:
                part_no = "K1EA TANK BOTTOM"
                wt_per_sheet = 2.63
                coating = "20/0"
            if cs.width == 655 and cs.length == 740:
                part_no = "K3CA Upper"
                wt_per_sheet = 2.66
                coating = "0/30"
            if cs.width == 565 and cs.length == 645:
                part_no = "K3CA BTM"
                wt_per_sheet = 2.29
                coating = "0/20"
            if cs.width == 810 and cs.length == 1010:
                part_no = "K0NH RL"
                wt_per_sheet = 4.79
                coating = "0/20"
            if cs.length > 0:
                packet_wt = round((cs.numbers * wt_per_sheet)/1000, 3)
            else:
                part_no = ''
                packet_wt = cs.weight

            incoming = Incoming.load_smpl_by_smpl_no(cs.smpl_no)
            mill_lst.append(incoming.mill)
            mill_id_lst.append(incoming.mill_id)
            incoming_date = incoming.incoming_date.replace('/', '-')
            incoming_date_lst.append(incoming_date)
            part_no_lst.append(part_no)
            wt_per_sheet_lst.append(wt_per_sheet)
            coating_lst.append(coating)
            packet_wt_lst.append(packet_wt)
            dc_number_lst.append(incoming.dc_number)


            dc_date_year = ''
            dc_date_month = ''
            dc_date = ''
            if incoming.dc_date:
                #if len(incoming.dc_date) > 7:
                dc_date = incoming.dc_date.strftime('%d-%m-%Y')
                '''dc_date = incoming.dc_date.replace('/', '-')
                i=0
                while i<4:
                    dc_date_year= dc_date_year + (dc_date[i])
                    i=i+1
                while i<6:
                    dc_date_month = dc_date_month + (dc_date[i])
                    i=i+1
                while i<8:
                    dc_date_date = dc_date_date + (dc_date[i])
                    i=i+1
                dc_date = dc_date_date + '-' + dc_date_month + '-' + dc_date_year'''

            #else:
            #    dc_date = change_date_format(incoming.incoming_date)
            dc_date_lst.append(dc_date)
            grade = (cs.grade.split("GRADE:"))
            if len(grade) > 1:
                grade = grade[1].split(';')
                cs.grade = grade[0]

    cs_lst = zip(_cs_id_lst, _cs_lst, part_no_lst, wt_per_sheet_lst, coating_lst, packet_wt_lst, mill_lst, mill_id_lst,
                 incoming_date_lst, dc_number_lst, dc_date_lst)
    return render_template('stock_display_htid.html', cs_lst=cs_lst)

@app.route('/check_stock_tsdpl', methods=['GET', 'POST'])
def check_stock_tsdpl():
    _cs_lst = []
    _cs_id_lst = []
    cs_lst = []
    today_date_lst = []
    no_of_days_lst = []
    incoming_lst = []
    sticker_lst = []
    finishing_date_lst = []


    part_no = ""
    coating = ""
    wt_per_sheet = 0
    packet_wt = 0

    cs_lst = CurrentStock.get_stock_by_customer('TATA STEEL DOWNSTREAM PRODUCTS LTD%', 'AllminusScrap')

    for cs_id, cs in cs_lst:
        if not any(substring in cs.packet_name for substring in ['W0P0', 'D0', 'M0']):
            _cs_id_lst.append(cs_id)
            _cs_lst.append(cs)
            incoming = Incoming.load_smpl_by_smpl_no(cs.smpl_no)
            incoming_lst.append(incoming)
            sticker = CurrentStock.get_sticker(cs.smpl_no, cs.packet_name, cs.thickness, cs.width, cs.length)
            sticker_lst.append(sticker)


        today_date = datetime.today().strftime('%Y-%m-%d')
        change_date_format(today_date)
        today_date_lst.append(change_date_format(today_date))

        no_of_days = (datetime.today().date() - cs.date).days
        no_of_days_lst.append(no_of_days)

        finishing_date = cs.date.strftime('%Y-%m-%d')

        finishing_date = (change_date_format(finishing_date))

        finishing_date_lst.append(finishing_date)

        '''incoming_flag = 0
        for incoming in incoming_lst:
            if cs.smpl_no == incoming.smpl_no:
                incoming_lst.append(incoming)
                incoming_flag = 1
                break

        if incoming_flag == 0:
            incoming_db = Incoming.load_smpl_by_smpl_no(cs.smpl_no)
            incoming_lst.append(incoming_db)

        grade = (cs.grade.split("GRADE:"))
        if len(grade) > 1:
            grade = grade[1].split(';')
            cs.grade = grade[0]'''

    cs_lst = zip(_cs_id_lst, _cs_lst, today_date_lst, no_of_days_lst, finishing_date_lst, incoming_lst, sticker_lst)
    return render_template('stock_display_tsdpl.html', cs_lst=cs_lst)


# Function displays stock based on stock type selected
@app.route('/stock', methods=['GET', 'POST'])
def stock():
    stock_type = ""
    unit = ""
    cs_lst = []
    _cs_lst = []
    cs_id_lst = []
    if request.method == 'POST':
        stock_type = request.form['stock_type']
        unit = request.form['unit']

    if request.method == 'GET':
        stock_type = request.args.get('stock_type')
        unit = request.args.get('unit')

    cs_lst_unit = CurrentStock.get_stock(stock_type, unit)
    for cs_id, cs in cs_lst_unit:
        cs_id_lst.append(cs_id)
        _cs_lst.append(cs)

    # cs_lst.append(cs_lst_unit1)
    # cs_lst.append(cs_lst_unit2)
    cs_lst = zip(cs_id_lst, _cs_lst)

    return render_template('stock_display.html', cs_lst=cs_lst)


@app.route('/mark_as_scrap_tr', methods=['GET', 'POST'])
def mark_as_scrap_tr():
    stock_type = ""
    unit = ""
    cs_lst = []
    _cs_lst = []
    cs_id_lst = []

    cs_lst = CurrentStock.get_stock_by_customer('TATA STEEL DOWNSTREAM PRODUCTS LTD%', 'RMFGForScrap')


    for cs_id, cs in cs_lst:
        cs_id_lst.append(cs_id)
        _cs_lst.append(cs)

    # cs_lst.append(cs_lst_unit1)
    # cs_lst.append(cs_lst_unit2)
    cs_lst = zip(cs_id_lst, _cs_lst)

    return render_template('mark_scrap.html', cs_lst=cs_lst)

@app.route('/scrap_marked', methods=['GET', 'POST'])
def scrap_marked():
    if request.method == 'POST':
        scrap_marked_lst = request.form.getlist['select_smpl']


    if request.method == 'GET':
        scrap_marked_lst = request.args.getlist('select_smpl')

    cs_id_lst = []


    for smpl in zip(scrap_marked_lst):
        smpl_details = smpl[0].split(',')
        smpl_no = smpl_details[1]
        cs_id = smpl_details[0]
        cs_id_lst.append(cs_id)

    message = CurrentStock.mark_for_scrap(cs_id_lst)

    return render_template('main_menu.html', message = message)

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
    dispatch_type = ""
    if request.method == 'POST':
        customer = request.form['select_customer']
        display_type = request.form['FG/RM']
        dispatch_type = request.form['dispatch_type']
    if request.method == 'GET':
        customer = request.args.get('select_customer')
        display_type = request.args.get('FG/RM')
        dispatch_type = request.args.get('dispatch_type')

    cs_lst = CurrentStock.get_stock_by_customer(customer, display_type)
    smpl_no_lst = []
    _cs_lst = []
    _cs_id_lst = []

    for cs_id, cs in cs_lst:
        smpl_no_lst.append(cs.smpl_no)
        _cs_id_lst.append(cs_id)
        _cs_lst.append(cs)


        # Extract unique sizes
    unique_smpl_no_lst = []
    unique_smpl_no_lst = list(set(smpl_no_lst))
    unique_smpl_no_lst.sort()

    if dispatch_type == 'qr':
        return render_template('qr_dispatch.html', customer=customer)
    else:
        return render_template('dispatch_list.html', cs_lst=zip(_cs_id_lst, _cs_lst), customer=customer,
                               unique_smpl_no_lst = unique_smpl_no_lst)


@app.route('/dispatch', methods=['GET', 'POST'])
def dispatch():
    if request.method == 'POST':
        dispatch_lst = request.form.getlist['select_smpl']
        '''pkt_name = request.form.getlist['packet_name']
        dispatch_nos = request.form.getlist['dispatch_numbers']
        dispatch_quantity = request.form.getlist['dispatch_quantity']'''
        vehicle_no = request.form['vehicle_no']
        customer = request.form['customer']
        dispatch_date = request.form['dispatch_date']
        dispatch_time = request.form['dispatch_time']
        dispatch_pkts = request.form.getlist['dispatch_packets']
        remarks = request.form['remarks']
        entry_by = request.form['entry_by']

    if request.method == 'GET':
        dispatch_lst = request.args.getlist('select_smpl')
        '''pkt_name = request.args.getlist('packet_name')
        dispatch_nos = request.args.getlist('dispatch_numbers')
        dispatch_quantity = request.args.getlist('dispatch_quantity')
        dispatch_pkts = request.args.getlist('dispatch_packets')'''
        defectives = request.args.getlist('defective')
        vehicle_no = request.args.get('vehicle_no')
        customer = request.args.get('customer')
        dispatch_date = request.args.get('dispatch_date')
        dispatch_time = request.args.get('dispatch_time')
        remarks = request.args.get('remarks')
        invoice_no = request.args.get('invoice_no')
        entry_by = request.args.get('entry_by')

    # This fetches the list and removes the elements that are not selected
    # The ones that are not selected are returned as None. The below list filters out the Nones
    #dispatch_nos_lst = list(filter(None, dispatch_nos))
    #dispatch_quantity_lst = list(filter(None, dispatch_quantity))
    defectives_lst = list(filter(None, defectives))
    #dispatch_pkts_lst = list(filter(None, dispatch_pkts))
    #pkt_name_lst = list(filter(None, pkt_name))

    dispatch_header = DispatchHeader(vehicle_no, customer, dispatch_date, dispatch_time, invoice_no, remarks, entry_by)
    dispatch_id = dispatch_header.save_to_db()

    # For the items to be dispatched, dispatch detail is created and the current stock quantity is deleted or reduced
    for smpl, defective in zip(dispatch_lst, defectives_lst):
        smpl_details = smpl.split(',')
        smpl_no = smpl_details[1]
        cs_id = smpl_details[0]
        cs = CurrentStock.load_smpl_by_id(cs_id)
        dispatch_detail = DispatchDetail(dispatch_id, cs.smpl_no, cs.thickness, cs.width, cs.length, cs.numbers,
                                         cs.weight, defective, 1, cs.length2, cs.packet_name, cs.unit)
        dispatch_detail.save_to_db()

        CurrentStock.delete_record(cs_id)


    return render_template('/main_menu.html')


@app.route('/qr_dispatch', methods=['GET', 'POST'])
def qr_dispatch():
    return render_template('qr_dispatch.html')

@app.route('/qr_dispatch_submit', methods=['GET', 'POST'])
def qr_dispatch_submit():
    cs_lst = []
    _cs_lst = []
    cs_id_lst = []
    cs_qr_lst = []
    dispatch_lst = []
    dispatch_numbers_lst = []
    dispatch_wt_lst = []
    packet_name_lst = []
    if request.method == 'POST':
        dispatch_lst = request.form.getlist['qr_dispatch']
        customer = request.form['customer']

    if request.method == 'GET':
        dispatch_lst = request.args.getlist('qr_dispatch')
        customer = request.args.get('customer')

    dispatch_string_lst = dispatch_lst[0].split('\n')
    #dispatch_record = dispatch_string_lst.split(',')


    for dispatch_string in dispatch_string_lst:
        if dispatch_string:
            dispatch_string = dispatch_string.split(',')
            smpl_no = dispatch_string[0]
            packet_name = dispatch_string[1]
            numbers = dispatch_string[3]
            size = dispatch_string[2].upper().split('X')
            if len(size) == 3:
                thickness = size[0]
                width = size[1]
                length = size[2]
                if '-' in length:
                    _length = length.split(' - ')
                    length = _length[0]
                    length2 = _length[1]
                else:
                    length2 = 0
                dispatch_weight = ''
                if 'COIL' in length:
                    length = '0'
            # This is for trap sizes
            if len(size) == 4:
                thickness = size[0]
                width = round(((Decimal(size[1]) + Decimal(size[2]))/2), 0)
                length = size[3]
                dispatch_weight = ''
                if 'COIL' in length:
                    length = '0'
            status = dispatch_string[6].replace('\r', '')

            # Currently FG wise separate packets is only mentioned for unit 2, so picking the unit based on user
            # to query for packet wise details or else no
            user = current_user
            if user.unit == 1:
                unit = '1'

            if user.unit == 2:
                unit = '2'

            unmatched_lst = []


            cs_qr_lst = CurrentStock.get_cs_for_qr_dispath(smpl_no, packet_name, width, length, status, customer, length2, unit, numbers)

            if cs_qr_lst:
                for cs_id, cs in cs_qr_lst:
                    cs_id_lst.append(cs_id)
                    cs_lst.append(cs)
                    # if coil then numbers =1, else take numbers from sticker
                    if cs.length == 0:
                        dispatch_numbers_lst.append(1)
                    else:
                        dispatch_numbers_lst.append(dispatch_string[3])
                    if dispatch_string[4]:
                        dispatch_weight = Decimal(dispatch_string[4])/1000
                    else:
                        dispatch_weight = '0'
                    dispatch_wt_lst.append(dispatch_weight)
                    packet_name_lst.append(dispatch_string[1])
            else:
                unmatched_lst.append(dispatch_string)

    _cs_lst = zip(cs_id_lst, cs_lst, dispatch_numbers_lst, dispatch_wt_lst, packet_name_lst)
    return render_template('qr_dispatch_list.html', _cs_lst = _cs_lst, customer = customer,
                            unmatched_lst = unmatched_lst)

@app.route('/honda_dispatch_list', methods=['GET', 'POST'])
def honda_dispatch_list():
    customer = 'HONDA TRADING CORPORATION INDIA PVT LTD'
    display_type = 'FGHonda'
    cs_lst = CurrentStock.get_stock_by_customer(customer, display_type)
    _cs_lst = []
    _cs_id_lst = []
    sizes = []

    for cs_id, cs in cs_lst:
        size = str(cs.width) + " x " + str(cs.length)
        if not any(substring in cs.packet_name for substring in ['W0P0', 'D0', 'M0']):
            _cs_id_lst.append(cs_id)
            _cs_lst.append(cs)
            sizes.append(size)

    # Extract unique sizes
    unique_sizes = []
    unique_sizes = list(set(sizes))
    unique_sizes.sort()



    return render_template('honda_dispatch_list.html', cs_lst=zip(_cs_id_lst,_cs_lst),
                           customer=customer, unique_sizes = unique_sizes)

@app.route("/honda_sizes")
def honda_sizes():
    with open("honda_sizes.json", "r") as file:
        data = json.load(file)
    return jsonify(data)

@app.route('/generate_honda_disp_list', methods=['GET', 'POST'])
def generate_honda_disp_list():
    cs_ids = ''
    if request.method == 'POST':
        cs_ids = request.form['cs_id_list']
        veh_no = request.form['vehicle_no']
        dispatch_date = request.form['dispatch_date']
    if request.method == 'GET':
        cs_ids = request.args.get('cs_id_list')
        veh_no = request.args.get('vehicle_no')
        dispatch_date = request.args.get('dispatch_date')

    dispatch_date = change_date_format(dispatch_date)

    cs_id_lst = []
    cs_id_lst= cs_ids.split(',')
    cs_id_lst= cs_id_lst[:-1]

    cs_lst = []
    incoming_lst = []

    for cs_id in cs_id_lst:
        cs = CurrentStock.load_smpl_by_id(cs_id)

        cs_lst.append(cs)

    zipped_cs_lst = []
    zipped_cs_lst_sorted = []
    cs_id_lst_sorted = []
    # Zip the IDs and objects together
    zipped_cs_lst = list(zip(cs_id_lst,cs_lst))


    zipped_cs_lst_sorted = sorted(zipped_cs_lst, key= lambda cs:(cs[1].width, cs[1].length, cs[1].smpl_no, cs[1].packet_name, cs[1].processing_id))

    # Unzip back into separate lists
    cs_id_lst_sorted, cs_lst_sorted = zip(*zipped_cs_lst_sorted)
    import_invoice_number_lst = []

    for cs in cs_lst_sorted:
        incoming = Incoming.load_smpl_by_smpl_no(cs.smpl_no)
        incoming_lst.append(incoming)
        import_invoice_number = incoming.remarks.split('IIN :')
        if len(import_invoice_number) > 1:
            import_invoice_number_lst.append(import_invoice_number[1])
        else:
            import_invoice_number_lst.append('')

    return render_template('honda_dispatch_list_ready.html',
                           cs_incoming_lst = zip(cs_lst_sorted, incoming_lst, import_invoice_number_lst), veh_no = veh_no,
                           dispatch_date = dispatch_date, cs_lst = zip(cs_id_lst_sorted, cs_lst_sorted))



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

    return render_template('dispatch_view.html', dispatch_hdr=dispatch_hdr, dispatch_detail_lst=dispatch_detail_lst,
                           dispatch_hdr_id=select_dispatch_hdr_id)


@app.route('/dispatch_view_invoice_no_update', methods=['GET', 'POST'])
def dispatch_view_invoice_no_update():
    if request.method == 'POST':
        invoice_no = request.form['invoice_no']
        dispatch_hdr_id = request.form['dispatch_hdr_id']
        dispatch_date = request.form['dispatch_date']
    if request.method == 'GET':
        invoice_no = request.args.get('invoice_no')
        dispatch_hdr_id = request.args.get('dispatch_hdr_id')
        dispatch_date = request.args.get('dispatch_date')

    DispatchHeader.update_invoice_no(dispatch_hdr_id, invoice_no, dispatch_date)
    return render_template('main_menu.html')

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


@app.route('/slitter_grinding_submit', methods=['GET', 'POST'])
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


@app.route('/maintenance_log',  methods=['GET', 'POST'])
def maintenance_log():
    return render_template('/maintenance_pick_machine.html')


@app.route('/maintenance_entry',  methods=['GET', 'POST'])
def maintenance_entry():

    if request.method == 'GET':
        machine = request.args.get('select_machine')

        # Establish a database connection
    connection = psycopg2.connect(
        dbname='smpl_prodn',
        user='postgres',
        password='smpl@509',
        host='localhost',
        port=5432
    )

    try:
        connection.autocommit = False
        cursor = connection.cursor()
        cursor.execute('select * from maintenance_history where machine = %s order by repair_start_date desc',(machine,))

        user_data = cursor.fetchall()
        maint_log = []

        for rec in user_data:
            rec = list(rec)
            rec[0] = change_date_format(str(rec[0]))
            if rec[9] != None:
                rec[9] = change_date_format(str(rec[9]))
            maint_log.append(rec)

    except psycopg2.OperationalError as error:
        # Handle network errors

        print("Rolling back the transaction...")
        connection.rollback()
        return render_template('/main_menu.html', message="Not Entered")
    finally:
        # Close the database connection
        connection.commit()
        connection.close()

    return render_template('/maintenance_entry.html', machine = machine, user_data = maint_log)


@app.route('/maintenance_entry_submit',  methods=['GET', 'POST'])
def maintenance_entry_submit():
    if request.method == 'GET':
        machine = request.args.get('machine')
        repair_start_date = request.args.get('maintenance_start_date')
        repair_start_time = request.args.get('maintenance_start_time')
        repair_end_date = request.args.get('maintenance_end_date')
        repair_end_time = request.args.get('maintenance_end_time')

        machine_part = request.args.get('machine_part')
        maintenance_by = request.args.get('maintenance_by')
        description = request.args.get('description')

    if request.method == 'POST':
        machine = request.form['machine']
        repair_start_date = request.form['maintenance_start_date']
        repair_start_time = request.form['maintenance_start_time']
        repair_end_date = request.form['maintenance_end_date']
        repair_end_time = request.form['maintenance_end_time']

        machine_part = request.form['machine_part']
        maintenance_by = request.form['maintenance_by']

        description = request.form.get('description')


    # Establish a database connection
    connection = psycopg2.connect(
        dbname='smpl_prodn',
        user='postgres',
        password='smpl@509',
        host='localhost',
        port=5432
    )

    try:
        connection.autocommit = False
        cursor = connection.cursor()
        cursor.execute("insert into maintenance_history (machine, repair_start_date, repair_start_time,"
                       "repair_end_date, repair_end_time, part, repair_done_by, description, file_name) values"
                       "(%s,%s,%s,%s,%s,%s,%s,%s,%s)", (machine, repair_start_date, repair_start_time, repair_end_date
                                                        ,repair_end_time, machine_part, maintenance_by, description, ''))

    except psycopg2.OperationalError as error:
        # Handle network errors

        print("Rolling back the transaction...")
        connection.rollback()
        return render_template('/main_menu.html', message="Not Entered")
    finally:
        # Close the database connection
        connection.commit()
        connection.close()
        return render_template('/main_menu.html', message="Entry Done")


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
    _processing_hdr_lst, processing_hdr_lst, processing_hdr_id_lst = [], [], []
    _order_dtl_lst, order_dtl_lst, order_dtl_id_lst = [], [], []
    order_dtl_lst_by_orderid, order_dtl_id_lst_by_orderid = [], []
    processing_dtl_lst, processing_dtl_lst_by_order_dtl = [], []
    cs_lst, _cs_lst = [], []

    smpl_number = str(smpl_number).upper().replace(" ", "")
    # smpl_no.replace(" ", "")
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
            i += 1

        sticker_lst = []
        sticker_lst = CurrentStock.getStickerList(smpl_no)

        return render_template('/hist_view.html', incoming=incoming, file_list=file_list,
                               smpl_no_lst=smpl_no_lst,
                               order_lst_by_smpl=zip(order_lst, order_id_lst),
                               order_id_lst_by_smpl=order_id_lst_by_smpl,
                               order_dtl_id_lst_by_orderid=order_dtl_id_lst_by_orderid,
                               order_dtl_lst_by_orderid=order_dtl_lst_by_orderid,
                               order_dtl_lst=order_dtl_lst,
                               processing_dtl_lst=processing_dtl_lst,
                               processing_hdr_lst=zip(processing_hdr_lst, processing_hdr_id_lst),
                               dispatch_hdr_lst=zip(dispatch_lst, dispatch_id_lst),
                               dispatch_dtl_lst=dispatch_dtl_lst,
                               cs_lst=cs_lst, sticker_lst = sticker_lst)

    else:
        return render_template('/main_menu.html', message=smpl_number + " not found.")

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


@app.route('/scams_search', methods=['GET', 'POST'])
def scams_search():
    return render_template('/scams_search.html')


@app.route('/scams_show_details', methods=['GET', 'POST'])
def scams_show_details():
    scams_no = ""
    file_list = ""
    if request.method == 'POST':
        scams_no = request.form['scams_no']
    if request.method == 'GET':
        scams_no = request.args.get('scams_no')

    smpl_no_lst = Incoming.get_scams_no(scams_no)

    dispatch_hdr_lst = []
    dispatch_dtl_lst, _dispatch_dtl_lst = [], []
    dispatch_id_lst = []
    order_lst, order_id_lst, _order_lst, order_lst_by_smpl, order_id_lst_by_smpl = [], [], [], [], []
    _processing_hdr_lst, processing_hdr_lst, processing_hdr_id_lst = [], [], []
    _order_dtl_lst, order_dtl_lst, order_dtl_id_lst = [], [], []
    order_dtl_lst_by_orderid, order_dtl_id_lst_by_orderid = [], []
    processing_dtl_lst, processing_dtl_lst_by_order_dtl = [], []
    cs_lst, _cs_lst = [], []

    #smpl_number = str(smpl_number).upper().replace(" ", "")
    # smpl_no.replace(" ", "")
    #smpl_no_lst = Incoming.smpl_no_list_for_history(smpl_number)

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
            i += 1

        return render_template('/hist_view.html', incoming=incoming, file_list=file_list,
                               smpl_no_lst=smpl_no_lst,
                               order_lst_by_smpl=zip(order_lst, order_id_lst),
                               order_id_lst_by_smpl=order_id_lst_by_smpl,
                               order_dtl_id_lst_by_orderid=order_dtl_id_lst_by_orderid,
                               order_dtl_lst_by_orderid=order_dtl_lst_by_orderid,
                               order_dtl_lst=order_dtl_lst,
                               processing_dtl_lst=processing_dtl_lst,
                               processing_hdr_lst=zip(processing_hdr_lst, processing_hdr_id_lst),
                               dispatch_hdr_lst=zip(dispatch_lst, dispatch_id_lst),
                               dispatch_dtl_lst=dispatch_dtl_lst,
                               cs_lst=cs_lst)

    else:
        return render_template('/main_menu.html', message=scams_no + " not found.")



@app.route('/print_old_label', methods=['GET', 'POST'])
def print_old_label():
    return render_template('/print_old_label.html')


@app.route('/print_label_smpl_pick', methods=['GET', 'POST'])
def print_label_smpl_pick():
    smpl_number = ""
    processing_lst = []
    processing_detail_lst = []
    _processing_detail_lst = []
    processing_date_lst = []
    processing_qc_lst=[]

    if request.method == 'POST':
        smpl_number = request.form['smpl_no']
    if request.method == 'GET':
        smpl_number = request.args.get('smpl_no')

    processing_lst = Processing.load_history(smpl_number)
    for processing_id, processing in processing_lst:
        _processing_detail_lst = (ProcessingDetail.load_history(processing_id))
        for processing_detail in _processing_detail_lst:
            processing_detail_lst.append(processing_detail)
            processing_date_lst.append(processing.processing_date)
            processing_qc_lst.append(processing.names_of_qc)

    return render_template('/print_label_pick_processing.html', processing_detail_lst=zip(processing_detail_lst, processing_date_lst, processing_qc_lst))

@app.route('/print_old_label_format', methods=['GET', 'POST'])
def print_old_label_format():
    smpl_number = ""

    if request.method == 'POST':
        smpl_number = request.form['select_processing_id']
    if request.method == 'GET':
        smpl_number = request.args.get('select_processing_id')

    smpl_no = smpl_number.split(';')
    size = smpl_no[2].split('x')
    packet_wt = smpl_no[7]
    _packet_wt = 0

    # Since size contains length1 and length2. Coil is represented as 0-0
    if size[1] == '0-0':
        _packet_wt = packet_wt


    incoming = Incoming.load_smpl_by_smpl_no(smpl_no[0])

    return render_template('/make_label.html', incoming = incoming, _packet_wt=_packet_wt)

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
    processing_lst = []
    processing_hdr_detail = []
    processing_dtl_lst = []
    incoming_lst = []
    dispatch_hdr_lst = []
    total_incoming = 0
    total_dispatch_hdr = 0

    incoming_lst = Incoming.get_daily_report(report_date)
    for incoming in incoming_lst:
        total_incoming += incoming[1]

    processing_hdr_lst = Processing.get_daily_report(report_date)

    processing_hdr_detail = Processing.get_daily_report_detail(report_date)

    dispatch_hdr_lst = DispatchHeader.get_daily_report(report_date)
    for dispatch_hdr in dispatch_hdr_lst:
        total_dispatch_hdr += (dispatch_hdr[0])

    machine_lst  = []
    processing_detail_lst = []
    pro_detail_lst = []

    for processing in processing_hdr_lst:
        if processing[0] not in machine_lst:
            if processing[0] != 'Slitting' or processing[0] != 'Mini_Slitting':
                machine_lst.append(processing[0])

    for processing_hdr in processing_hdr_detail:
        pro_detail_lst = ProcessingDetail.load_for_report(processing_hdr[0])
        for processing_detail in pro_detail_lst:
             processing_detail_lst.append(processing_detail)

    #daily_report_whatsapp()

    #Sticker taken but entry not done
    sticker_lst = []
    sticker_lst = ProcessingDetail.no_entry_done(report_date)

    #machine_lst = ['CTL 1', 'CTL 2', 'NCTL 1', 'NCTL 2', 'NCTL 3', 'NCTL 4', 'Reshearing 1', 'Reshearing 2', 'Reshearing 3',
    #                'Reshearing 4', 'Reshearing 5', 'Reshearing 6', 'Reshearing 7', 'Reshearing 8']

    return render_template('/daily_report.html', date=change_date_format(report_date), incoming_lst=incoming_lst,
                           total_incoming=total_incoming, processing_hdr_lst=processing_hdr_lst,
                           dispatch_hdr_lst=dispatch_hdr_lst, processing_hdr_detail=processing_hdr_detail,
                           machine_lst = machine_lst, processing_detail_lst = processing_detail_lst,
                           total_dispatch_hdr= total_dispatch_hdr, sticker_lst = sticker_lst)

def daily_report_whatsapp():
    yesterday_date_lst = []
    yesterday_date_lst.append(datetime.now() - timedelta(1))
    print(calendar.day_name[yesterday_date_lst[0].weekday()])

    # On Mondays 2 messages have to be sent, 1 for Saturday and 1 for Sunday
    if calendar.day_name[yesterday_date_lst[0].weekday()] == 'Sunday':
        yesterday_date_lst.append(datetime.now() - timedelta(2))

    for yesterday_date in yesterday_date_lst:
        yesterday_date = yesterday_date.strftime('%Y-%m-%d')
        incoming_lst = Incoming.get_daily_report(yesterday_date)
        #phone_number_lst = ['919632120048']
        phone_number_lst = ['919632120048', '919945660080', '919845015897']
        total_incoming_unit1 = 0
        total_incoming_unit2 = 0
        total_incoming_unit4 = 0
        for incoming in incoming_lst:
            if incoming[2] == '1':
                total_incoming_unit1 += incoming[1]
            if incoming[2] == '2':
                total_incoming_unit2 += incoming[1]
            if incoming[2] == '4':
                total_incoming_unit4 += incoming[1]

        processing_hdr_lst = Processing.get_daily_report(yesterday_date)

        reshearing_unit1 = ['Reshearing 1', 'Reshearing 2', 'Reshearing 3', 'Reshearing 4', 'Reshearing 8']
        reshearing_unit2 = ['Reshearing 5', 'Reshearing 6', 'Reshearing 7', 'Reshearing 9']

        processing_ctl1 = 0
        processing_reshearing1 = 0
        processing_ctl2 = 0
        processing_reshearing2 = 0
        processing_slitting = 0
        processing_nctl = 0

        for processing in processing_hdr_lst:
            if processing[0] == 'CTL 1':
                processing_ctl1 += processing[2]
            if processing[0] in reshearing_unit1:
                processing_reshearing1 += processing[2]
            if processing[0] == 'CTL 2':
                processing_ctl2 += processing[2]
            if processing[0] == 'Slitting':
                processing_slitting += processing[2]
            if processing[0].startswith('NCTL'):
                processing_nctl += processing[2]
            if processing[0] in reshearing_unit2:
                processing_reshearing2 += processing[2]

        dispatch_lst = []
        dispatch_lst =  DispatchHeader.get_daily_report_whatsapp(yesterday_date)
        dispatch_msg = ''

        for phone_no in phone_number_lst:
            incoming_msg = 'https://twha.inosms.com/api/sendText?token=624682490c9014d2e917f18e&phone=' + phone_no + '&message=Incoming%20' + change_date_format(yesterday_date) + '%0a%20Unit%201%20-%20' + str(total_incoming_unit1) + '%20MT%0a%20Unit%202%20-%20' + str(total_incoming_unit2) + '%20MT%0a%20Unit%204%20-%20' + str(total_incoming_unit4) +'%20MT'

            urllib.request.urlopen(incoming_msg)

            processing_unit1_msg = 'https://twha.inosms.com/api/sendText?token=624682490c9014d2e917f18e&phone=' + phone_no + '&message=Processing%20Unit%201%20' + change_date_format(yesterday_date) + '%0aCTL%20-%20' + str(processing_ctl1) + '%20MT%0aReshearing%20-%20' + str(processing_reshearing1) + '%20MT'

            urllib.request.urlopen(processing_unit1_msg)

            processing_unit2_msg = 'https://twha.inosms.com/api/sendText?token=624682490c9014d2e917f18e&phone=' + phone_no + '&message=Processing%20U2%20' + change_date_format(yesterday_date) + '%0aCTL%20-%20' + str(processing_ctl2) + '%0aSlitting%20-%20' + str(processing_slitting) + '%0aNCTL%20-%20' + str(processing_nctl) + '%0aReshearing%20-%20' + str(processing_reshearing2) + '%20MT'

            urllib.request.urlopen(processing_unit2_msg)

            dispatch_msg = 'https://twha.inosms.com/api/sendText?token=624682490c9014d2e917f18e&phone=' + phone_no + '&message=Dispatch%20' + change_date_format(yesterday_date)
            if dispatch_lst:

                for dispatch in dispatch_lst:
                    dispatch_msg = dispatch_msg + '%0a%20Unit%20' + dispatch[0] + '%20-%20' + str(dispatch[1]) + '%20MT'

            urllib.request.urlopen(dispatch_msg)

# This is to schedule the whatsapp messages
scheduler = BackgroundScheduler()
scheduler.add_job(func=daily_report_whatsapp, trigger="cron", hour=10, minute=30)
scheduler.start()

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route('/get_monthly_report', methods=['GET', 'POST'])
def get_monthly_report():
    report_month = 0
    report_year = 0
    if request.method == 'POST':
        report_month = int(request.form['report_month'])
        report_year = int(request.form['report_year'])
    if request.method == 'GET':
        report_month = int(request.args.get('report_month'))
        report_year = int(request.args.get('report_year'))

    month_data = CurrentStock.monthly_report_hdr((report_month), (report_year))
    month_dispatch_total = (DispatchHeader.get_monthly_report((report_month), (report_year)))
    month_dispatch_total_by_customer = (DispatchHeader.get_monthly_report_by_customer((report_month), (report_year)))


    month_incoming_total = Incoming.get_monthly_total((report_month), (report_year))

    customer_wise_machine_wise_data = CurrentStock.customer_wise_machine_wise_month_data((report_month), (report_year))

    customer_wise_month_data = CurrentStock.customer_wise_month_data((report_month), (report_year))

    prev_month_data = []
    prev_prev_month_data = []
    if report_month != 1 or report_month != 2:
        prev_month_data = CurrentStock.monthly_report_hdr((report_month- 1), (report_year))
        prev_prev_month_data = CurrentStock.monthly_report_hdr((report_month- 2), (report_year))

        #customer_wise_prev_month_data = CurrentStock.customer_wise_month_data((report_month - 1), (report_year))
        #customer_wise_prev_prev_month_data = CurrentStock.customer_wise_month_data((report_month - 2), (report_year))

    if report_month == 1:
       prev_month_data = CurrentStock.monthly_report_hdr((12), (report_year -1))
       prev_prev_month_data = CurrentStock.monthly_report_hdr((11), (report_year -1))
       #customer_wise_prev_month_data = CurrentStock.customer_wise_month_data((12), (report_year - 1))
       #customer_wise_prev_prev_month_data = CurrentStock.customer_wise_month_data((11), (report_year - 1))

    if report_month == 2:
       prev_month_data = CurrentStock.monthly_report_hdr((report_month- 1), (report_year))
       prev_prev_month_data = CurrentStock.monthly_report_hdr((12), (report_year -1))
       #customer_wise_prev_month_data = CurrentStock.customer_wise_month_data((report_month - 1), (report_year))
       #customer_wise_prev_prev_month_data = CurrentStock.customer_wise_month_data((12), (report_year - 1))


    machine_lst = ['CTL 1', 'CTL 2', 'NCTL 1', 'NCTL 2', 'NCTL 3', 'NCTL 4', 'NCTL 5','Reshearing 1',
                   'Reshearing 2', 'Reshearing 3', 'Reshearing 4', 'Reshearing 5', 'Reshearing 6',
                   'Reshearing 7', 'Reshearing 8', 'Slitting', 'Mini_Slitting']

    # As there are 17 machines, arrays are made for each row with 17 elements assigned to 0
    month_wt_lst_arr = [0]*17
    month_cuts_lst_arr = [0]*17
    month_time_lst_arr = [0]*17
    prev_month_wt_lst_arr = [0]*17
    prev_month_cuts_lst_arr = [0]*17
    prev_month_time_lst_arr = [0]*17
    prev_prev_month_wt_lst_arr = [0]*17
    prev_prev_month_cuts_lst_arr = [0]*17
    prev_prev_month_time_lst_arr = [0]*17

    i = 0
    month_total_wt=0
    prev_month_total_wt=0
    prev_prev_month_total_wt=0
    for machine in machine_lst:

        for data in month_data:
            if data[0] == machine:
                month_wt_lst_arr[i] += data[1]
                month_cuts_lst_arr[i] += data[2]
                month_time_lst_arr[i] += data[3]
                month_total_wt += data[1]
        for prev_data in prev_month_data:
            if prev_data[0] == machine:
                prev_month_wt_lst_arr[i] += prev_data[1]
                prev_month_cuts_lst_arr[i] += prev_data[2]
                prev_month_time_lst_arr[i] += prev_data[3]
                prev_month_total_wt += prev_data[1]
        for prev_prev_data in prev_prev_month_data:
            if prev_prev_data[0] == machine:
                prev_prev_month_wt_lst_arr[i] += prev_prev_data[1]
                prev_prev_month_cuts_lst_arr[i] += prev_prev_data[2]
                prev_prev_month_time_lst_arr[i] += prev_prev_data[3]
                prev_prev_month_total_wt += prev_prev_data[1]
        i += 1

    operations = ['CTL', 'CTL 2','Lamination', 'Levelling', 'Mini_Slitting', 'Narrow_CTL', 'Reshearing',
                  'Slitting', 'Trap_NCTL', 'Trap_Reshearing']

    customer_lst = []
    for customer in customer_wise_machine_wise_data:
        customer_lst.append(customer[0])

    # Convert to set to get unique names
    unique_customers = set(customer_lst)

    # Convert back to list if needed
    unique_customers_list = list(unique_customers)
    unique_customers_list.sort()

    # Pivot the data: create a dictionary with customer_name as key and operation values
    pivoted_data = {}
    for customer in unique_customers_list:
        pivoted_data[customer] = {op: float(0) for op in operations}

    # Fill in the actual values
    for row in customer_wise_machine_wise_data:
        customer = row[0]
        operation = row[1]
        weight = float(row[2])
        if customer in pivoted_data and operation in pivoted_data[customer]:
            pivoted_data[customer][operation] = weight


    honda_schedule_sizes = DispatchHeader.honda_schedule_sizes(report_month, report_year)

    honda_dispatch_by_size = DispatchHeader.honda_dispatch_for_month(report_month, report_year, honda_schedule_sizes)

    honda_dispatch_total = []
    honda_dispatch_total_pkts = []

    column = 1
    while column < len(honda_dispatch_by_size[column]):
        column_total = 0
        row = 0
        while row < len(honda_dispatch_by_size):
            column_total += honda_dispatch_by_size[row][column]
            row +=1
        column += 1
        honda_dispatch_total.append(column_total)

    for decimal_sizes, column_tot in zip(honda_schedule_sizes, honda_dispatch_total):
        sizes = str(decimal_sizes[0]) + 'x' + str(decimal_sizes[1])
        if sizes == '565x645' or sizes == '655x740':
            pkts = round(column_tot/450,2)
        else:
            pkts = round(column_tot/300, 2)
        honda_dispatch_total_pkts.append(pkts)




    return render_template('/monthly_report_display.html', report_month= report_month,
                           report_year= report_year,
                           month_lst = zip(machine_lst, month_wt_lst_arr, month_cuts_lst_arr, month_time_lst_arr,
                                           prev_month_wt_lst_arr, prev_month_cuts_lst_arr, prev_month_time_lst_arr,
                                           prev_prev_month_wt_lst_arr, prev_prev_month_cuts_lst_arr, prev_prev_month_time_lst_arr),
                                            month_total_wt = month_total_wt, prev_prev_month_total_wt = prev_prev_month_total_wt,
                                            prev_month_total_wt = prev_month_total_wt, cust_month_lst = customer_wise_month_data,
                                            month_dispatch_total = month_dispatch_total, month_incoming_total = month_incoming_total,
                                            customer_wise_machine_wise_data = customer_wise_machine_wise_data,
                           customers = unique_customers_list, operations = operations, data = pivoted_data,
                           month_dispatch_total_by_customer = month_dispatch_total_by_customer,
                           honda_dispatch_by_size = honda_dispatch_by_size, honda_schedule_sizes = honda_schedule_sizes,
                           honda_dispatch_total = honda_dispatch_total, honda_dispatch_total_pkts = honda_dispatch_total_pkts)


@app.route('/daily_report_pick_month_year', methods=['GET', 'POST'])
def daily_report_pick_month_year():
    return render_template('/daily_report_pick_month_year.html')


@app.route('/honda_wip_fg_stock', methods=['GET', 'POST'])
def honda_wip_fg_stock():
    honda_fg_stock_lst = []
    honda_wip_stock_lst = []

    honda_fg_stock_lst = CurrentStock.getHondaFGStock()
    honda_wip_stock_lst = CurrentStock.getHondaWIPStock()

    return render_template('/honda_FG_WIP_stock.html', fg_lst = honda_fg_stock_lst, wip_lst = honda_wip_stock_lst)


def change_date_format(date):


    split_date = date.split('-')
    new_date = split_date[2] + '-' + split_date[1] + '-' + split_date[0]
    return new_date


@app.route('/fg_to_wip_enter_smpl', methods=['GET', 'POST'])
def fg_to_wip_enter_smpl():
    return render_template('/fg_to_wip_enter_smpl.html')


@app.route('/get_fg_to_wip_list', methods=['GET', 'POST'])
def get_fg_to_wip_list():
    smpl_no = ""
    file_list = ""
    _cs_lst = []
    cs_lst = []
    cs_id_lst = []
    if request.method == 'POST':
        smpl_no = request.form['smpl_no']
    if request.method == 'GET':
        smpl_no = request.args.get('smpl_no')

    _cs_lst = (CurrentStock.get_smpl_for_fg_to_wip(smpl_no))
    if _cs_lst:
        for cs_id, cs in _cs_lst:
            cs_lst.append(cs)
            cs_id_lst.append(cs_id)
        return render_template('/fg_to_wip_display_list.html', cs_lst=zip(cs_id_lst, cs_lst))
    else:
        return render_template('/main_menu.html', message=smpl_no + " not found.")


@app.route('/fg_to_wip_submit', methods=['GET', 'POST'])
def fg_to_wip_submit():
    smpl = ""
    if request.method == 'POST':
        smpl = request.form['select_smpl']

    if request.method == 'GET':
        smpl = request.args.get('select_smpl')

    smpl_details = smpl.split(',')
    # smpl_no = smpl_details[1]
    cs_id = smpl_details[0]
    #CurrentStock.update_status_cls(cs_id, "WIP")
    cs = CurrentStock.load_smpl_by_id(cs_id)
    ProcessingDetail.change_status(cs.smpl_no, cs.width, cs.length, cs.length2, cs.packet_name, 'WIP')
    status = CurrentStock.change_wt(cs.smpl_no, cs.width, cs.length, cs.weight,cs.numbers, 'plus', 'WIP', cs.length2)

    if status == 'insert':
        CurrentStock.update_status_cls(cs_id, "WIP")
    elif status == 'continue':
        CurrentStock.delete_record(cs_id)


    return render_template('/main_menu.html')

@app.route('/invoice_check_report', methods=['GET', 'POST'])
def invoice_check_report():
    processing_lst = Processing.list_for_invoice_check()
    processing_pass_lst = []

    # The rates machine cost - direct labour cost
    # in the pricing sheet, delete the direct labour row, the total cost you get is the cost mentioned here
    machine_name_value = [("Slitting",7155), ("CTL 1", 4598), ("CTL 2", 4598), ("NCTL 1", 1325), ("NCTL 2", 805),
                          ("NCTL 3", 1325), ("NCTL 4", 500), ("NCTL 5", 1325), ("Reshearing 1", 410),
                          ("Reshearing 2", 410), ("Reshearing 3", 410), ("Reshearing 4", 410), ("Reshearing 5", 410),
                          ("Reshearing 6", 410), ("Reshearing 7", 410), ("Reshearing 8", 410),  ("Reshearing 9", 410),
                        ("Mini_Slitting", 500), ("Lamination", 300)]
    labour_rate = 190
    indirect_labour = 0
    indirect_labour_value = [("Slitting",2.5), ("CTL 1", 2.5), ("CTL 2", 2.5), ("NCTL 1", 1), ("NCTL 2", 1),
                          ("NCTL 3", 1), ("NCTL 4", 0.75), ("NCTL 5", 1), ("Reshearing 1", 1),
                          ("Reshearing 2", 1), ("Reshearing 3", 1), ("Reshearing 4", 1), ("Reshearing 5", 1),
                          ("Reshearing 6", 1), ("Reshearing 7", 1), ("Reshearing 8", 1), ("Reshearing 9", 1),
                             ("Mini_Slitting", 0.75), ("Lamination", 0.5)]

    for processing_tup in processing_lst:
        processing = list(processing_tup)
        machine_cost = 0
        for machine in machine_name_value:
            if processing[3] == machine[0]:
                machine_rate = machine[1]
                machine_cost = round(machine_rate * (processing[20]/60),2)
                processing.append(machine_cost)
        for _indirect_labour in indirect_labour_value:
            if processing[3] == _indirect_labour[0]:
                indirect_labour = _indirect_labour[1]
                labour_cost = round(labour_rate * (processing[19] + indirect_labour)  * (processing[20]/60),2)
                processing.append(labour_cost)
        total_cost = labour_cost + machine_cost
        processing.append(total_cost)

        total_cost_per_mt = round(Decimal(total_cost)/(processing[15]),0)
        processing.append(total_cost_per_mt)

        processing_pass_lst.append(processing)

    return render_template('/invoice_check_report.html', processing_lst = processing_pass_lst)

@app.route('/tally_stock_check_upload', methods=['GET', 'POST'])
def tally_stock_check_upload():
    return render_template('/tally_stock_check_upload.html')


@app.route('/tally_stock_check', methods=['GET', 'POST'])
def tally_stock_check():
    db_data = []
    _cs_lst = []
    if request.method == 'POST':
        # Save uploaded file
        file = request.files['xlsx_filename']

    else:
        file = request.args.get('xlsx_filename')

    if file and file.filename.endswith('.xlsx'):
        # Read the Excel file into a DataFrame
        excel_data = pd.read_excel(file)

        # Get the header row (4th row, index 3) and remaining data
        header_row = excel_data.iloc[2]
        excel_data = excel_data.iloc[3:]

        # Set the header
        excel_data.columns = header_row

        # Reset index after removing rows
        excel_data = excel_data.reset_index(drop=True)

        # Remove all spaces from the first column
        excel_data[excel_data.columns[0]] = excel_data[excel_data.columns[0]].astype(str).str.replace(' ', '')

        # Remove rows with blank values in third column
        excel_data = excel_data.dropna(subset=[excel_data.columns[2]])

        # Remove rows containing 'Lami' in second column
        excel_data = excel_data[~excel_data[excel_data.columns[1]].str.contains('Lami', na=False, case=False)]

        # Keep only rows with 'FG' or 'RM' in fourth column
        excel_data = excel_data[excel_data[excel_data.columns[2]].isin(['Finished Goods', 'Raw Materials'])]

        # Reset index after all filtering
        excel_data = excel_data.reset_index(drop=True)

        # Now call a function to compare the data
        _cs_lst = CurrentStock.get_stock('All','All')

        for cs_id, cs in _cs_lst:
            db_data_obj = [cs.smpl_no, str(cs.weight), str(cs.numbers), str(cs.width), str(cs.length),
                           str(cs.status), cs.customer,
                           str(cs.thickness), cs. grade, cs.unit, cs.packet_name, str(cs.length2),
                           str(cs.date), str(cs.processing_id), cs.second_customer, cs_id]
            db_data.append(db_data_obj)
            db_data_obj = []

        cs_dataframe = pd.DataFrame(db_data, columns=["smpl_no","weight","numbers","width","length","status",
                                                      "customer","thickness","grade","unit","packet_name","length2",
                                                      "date","processing_id","second_customer", "cs_id"])

        missing_in_db = excel_data[~excel_data['SMPL No.'].isin(cs_dataframe['smpl_no'])]
        missing_in_excel = cs_dataframe[~cs_dataframe['smpl_no'].isin(excel_data['SMPL No.'])]

        missing_in_db_html = missing_in_db.to_html(classes='table table-striped', index=False)
        missing_in_excel_html = missing_in_excel.to_html(classes='table table-striped', index=False)

        if missing_in_db.empty and missing_in_excel.empty:
            print("All items match!")
        else:
            print("Items missing in DB:")
            print(missing_in_db)
            print("Items missing in Excel:")
            print(missing_in_excel)


        return render_template('/tally_stock_check_result.html', missing_in_db_html = missing_in_db_html,
                               missing_in_excel_html = missing_in_excel_html)


@app.errorhandler(Exception)
def handle_error(e):
    # Log the error
    app.logger.error(f"An error occurred: {str(e)}")

    # Display a custom error page with the error details
    return render_template('error.html', error=str(e)), 500


if __name__ == '__main__':
    app.config["SECRET_KEY"] = "SMPLMRP"
    # app.run(debug=True)
    SERVER_NAME = '0.0.0.0'
    #SERVER_NAME = '127.0.0.1'
    SERVER_PORT = 5001


    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[5], profile_dir='E:\postgres_data_bkp\PROFILING')
    #app.run(debug=True)
    #app.run(SERVER_NAME, SERVER_PORT, threaded=True, debug=True)

    logger = logging.getLogger('waitress')
    logger.setLevel(logging.INFO)

    # Using waitress as a WSGI server.
    # Steps here https://dev.to/thetrebelcc/how-to-run-a-flask-app-over-https-using-waitress-and-nginx-2020-235c

    serve(app,host=SERVER_NAME,port=SERVER_PORT)
