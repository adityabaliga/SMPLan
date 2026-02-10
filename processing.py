from database import CursorFromConnectionFromPool
from decimal import Decimal
from datetime import datetime




class Processing:
    def __init__(self, smpl_no, operation, processing_date, start_time, end_time, setting_start_time,
                 setting_end_time, processing_time, setting_time, no_of_qc, no_of_helpers, names_of_qc,
                 setting_date, total_processed_wt, total_cuts, previous_processing_id):
        self.smpl_no = smpl_no
        self.operation = operation
        self.processing_date = change_date_format(processing_date)
        self.start_time = start_time
        self.end_time = end_time
        self.setting_start_time = setting_start_time
        self.setting_end_time = setting_end_time
        self.processing_time = processing_time
        self.setting_time = setting_time
        self.no_of_qc = no_of_qc
        self.no_of_helpers = no_of_helpers
        self.names_of_qc = names_of_qc
        self.setting_date = setting_date
        self.total_processed_wt = total_processed_wt
        self.total_cuts = total_cuts
        self.previous_processing_id = previous_processing_id


    @classmethod
    def load_from_db(cls, smpl_no, operation):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from processing where smpl_no = %s and operation = %s', (smpl_no, operation))
            user_data = cursor.fetchall()
            processing_lst = []
            for lst in user_data:
                processing = Processing(smpl_no=lst[1], operation=lst[2], processing_date=change_date_format(lst[3]), start_time=lst[4],
                                        end_time=lst[5], processing_time=int(lst[6]), setting_start_time=lst[7],
                                        setting_end_time=lst[8], setting_time=int(lst[9]), no_of_qc=lst[10],
                                        no_of_helpers=lst[11], names_of_qc=lst[12],
                                        setting_date=change_date_format(lst[13]), total_processed_wt = Decimal(lst[14]),
                                        total_cuts=int(lst[15]), previous_processing_id=(lst[16]))
                processing_lst.append(processing)
        return processing_lst

    def save_to_db(self):

        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("insert into processing (smpl_no, operation, processing_date, start_time, "
                "end_time, setting_start_time, setting_end_time, production_time, setting_time, no_of_qc, "
                "no_of_helpers, names_of_qc,setting_date, total_processed_wt,"
                "total_cuts) values (%s, %s,%s, %s, "
                "%s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s)",
                (self.smpl_no, self.operation, self.processing_date,
                    self.start_time, self.end_time, self.setting_start_time,
                    self.setting_end_time, self.processing_time, self.setting_time,
                    self.no_of_qc, self.no_of_helpers, self.names_of_qc, self.setting_date,
                    self.total_processed_wt, self.total_cuts))

            cursor.execute("select processing_id from processing where oid= %s", (cursor.lastrowid,))
            data = cursor.fetchone()
            return data[0]

    @classmethod
    def load_history(cls, smpl_no):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from processing where smpl_no = %s order by processing_date, start_time asc', (smpl_no, ))
            user_data = cursor.fetchall()
            processing_lst, processing_id_lst = [],[]
            for lst in user_data:
                processing = Processing(smpl_no=lst[2], operation=lst[2], processing_date= (lst[3]), start_time=lst[4],
                                        end_time=lst[5], processing_time=int(lst[6]), setting_start_time=lst[7],
                                        setting_end_time=lst[8], setting_time=int(lst[9]), no_of_qc=lst[10],
                                        no_of_helpers=lst[11], names_of_qc=lst[12],
                                        setting_date= (lst[13]), total_processed_wt = Decimal(lst[14]),
                                        total_cuts=int(lst[15]), previous_processing_id=(lst[16]))
                processing_id = int(lst[0])
                processing_lst.append(processing)
                processing_id_lst.append(processing_id)
        return zip(processing_id_lst, processing_lst)

    @classmethod
    def get_daily_report(cls, report_date):
        with CursorFromConnectionFromPool() as cursor:
            # cursor.execute('select * from processing where processing_date = %s order by operation asc', (report_date, ))
            cursor.execute('select operation, sum(total_cuts), sum(total_processed_wt), sum(production_time), sum(setting_time)  from processing '
                           'where processing_date = %s group by operation order by operation', (report_date,))
            user_data = cursor.fetchall()

            # THis was the original query here but the time wasn't coming properly so changed it to above
            ''' select sum(processing_detail.processed_numbers), sum(processing_detail.processed_wt), 
                           sum(processing.production_time)/60, processing_detail.operation from processing, processing_detail on 
                           processing.processing_id = processing_detail.processing_id where 
                           processing.processing_date = %s and processing.processing_id = processing_detail.processing_id 
                           group by  processing_detail.operation order by processing_detail.operation'''
        return user_data

    @classmethod
    def get_daily_report_detail(cls, report_date):
        with CursorFromConnectionFromPool() as cursor:
            # cursor.execute('select * from processing where processing_date = %s order by operation asc', (report_date, ))
            cursor.execute('select p.*, i.thickness, i.customer from processing p LEFT JOIN incoming i ON p.smpl_no = i.smpl_no '
                           'where p.processing_date = %s order by '
                           'p.operation, p.start_time',
                           (report_date,))
            user_data = [list(row) for row in cursor.fetchall()]

            for processing in user_data:
                processing[17] = cust_name_for_label(processing[17])


        return user_data

    @classmethod
    def list_for_invoice_check(cls):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('SELECT distinct p.processing_id, p.*, i.thickness, i.customer, p.no_of_qc + p.no_of_helpers'
                           ' as total_members, p.setting_time + p.production_time as total_time , d.machine '
                           'FROM incoming i JOIN '
                           'processing p ON p.smpl_no = i.smpl_no '
                           'JOIN processing_detail d ON d.processing_id = p.processing_id where '
                           '(p.processing_date >= current_date - interval %s '
                           'month and p.processing_date < current_date)', ('12',))

            user_data = cursor.fetchall()

            return user_data

def change_date_format(date):
    # split_date = date.split('-')
    # new_date = split_date[2] + '-' + split_date[1] + '-' + split_date[0]

    new_date = datetime.strptime(str(date),'%Y-%m-%d').strftime('%d/%m/%y')
    return new_date

def cust_name_for_label(customer):
    customer = customer.lower()

    customer = customer.replace("private",'')
    customer = customer.replace("limited",'')
    customer = customer.replace("pvt",'')
    customer = customer.replace("ltd",'')
    customer = customer.replace(".",'')
    customer = customer.replace("&",' and ')

    _customer = customer

    temp_customer = customer.split('[')
    customer =  temp_customer[0]


    if customer.startswith("veer o metal") or customer.startswith("veer-o-metal"):
        cust_name= "Veer O Metals";
        if "mkl" in _customer:
            cust_name= "Veer O Metals [MKL]"
        elif "bel" in _customer:
            cust_name= "Veer O Metals [BEL]"
        elif "jigani" in _customer:
            cust_name= "Veer O Metals [JIG]"
        elif "haro" in _customer:
            cust_name= "Veer O Metals [HRL]"

    elif customer.startswith("ttp technolgies"):
        cust_name= "TTP Technologies";
    elif customer.startswith("mpp technolgies"):
        cust_name= "MPP Technologies";
    elif customer.startswith("nash industries"):
        cust_name= "Nash Industries";
        if "38/1" in _customer:
            cust_name= "Nash Industries [NGR]"
        if "70  and  104" in _customer:
            cust_name= "Nash Industries [DBS]"
        if "102" in _customer or "236" in _customer or "247" in _customer:
            cust_name= "Nash Industries [PNY]"
        if "PLOT-2" in _customer:
            cust_name= "Nash Industries [JGN]"
        if "30/1,31/3" in _customer:
            cust_name= "Nash Industries [JGN]"
    elif customer.startswith("balmer lawrie"):
        cust_name= "Balmer Lawrie"
    elif customer.startswith("metal storage"):
        cust_name= "Metal Storage"
    elif customer.startswith("bharat metal"):
        cust_name= "Bharat Metal"
    elif customer.startswith("aditya auto"):
        cust_name= "Aditya Auto"
    elif customer.startswith("satrac eng"):
        cust_name= "SATRAC"
    elif customer.startswith("mallik eng"):
        cust_name= "Mallik Engg"
    elif customer.startswith("kanunga"):
        cust_name= "Kanunga Extrusion"
    elif customer.startswith("sun zone"):
        cust_name= "SUN ZONE SOLAR"
    elif customer.startswith("tata steel downstream products"):
        cust_name= "TSDPL"
    elif customer.startswith("honda"):
        cust_name= "HONDA"
    elif customer.startswith("tt steel"):
        cust_name= "TTSSI"
    elif customer.startswith("jr and "):
        cust_name= "J R AND COMPANY"
    elif customer.startswith("vns "):
        cust_name= "VNS"
    elif customer.startswith("ets - lindgren "):
        cust_name= "ETS - LINDGREN ENG"
    else:
        cust_split = customer.split(' ')
        if len(cust_split) >=2:
            cust_name = cust_split[0] + ' ' + cust_split[1]

    cust_name = cust_name.upper()
    return cust_name

