from database import CursorFromConnectionFromPool
from decimal import Decimal
from datetime import datetime




class Processing:
    def __init__(self, smpl_no, operation, processing_date, start_time, end_time, setting_start_time,
                 setting_end_time, processing_time, setting_time, no_of_qc, no_of_helpers, names_of_qc,
                 setting_date, total_processed_wt, total_cuts):
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
                                        total_cuts=int(lst[15]))
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
            cursor.execute('select * from processing where smpl_no = %s', (smpl_no, ))
            user_data = cursor.fetchall()
            processing_lst, processing_id_lst = [],[]
            for lst in user_data:
                processing = Processing(smpl_no=lst[2], operation=lst[2], processing_date= (lst[3]), start_time=lst[4],
                                        end_time=lst[5], processing_time=int(lst[6]), setting_start_time=lst[7],
                                        setting_end_time=lst[8], setting_time=int(lst[9]), no_of_qc=lst[10],
                                        no_of_helpers=lst[11], names_of_qc=lst[12],
                                        setting_date= (lst[13]), total_processed_wt = Decimal(lst[14]),
                                        total_cuts=int(lst[15]))
                processing_id = int(lst[0])
                processing_lst.append(processing)
                processing_id_lst.append(processing_id)
        return zip(processing_id_lst, processing_lst)

    @classmethod
    def get_daily_report(cls, report_date):
        with CursorFromConnectionFromPool() as cursor:
            # cursor.execute('select * from processing where processing_date = %s order by operation asc', (report_date, ))
            cursor.execute('select operation, sum(total_cuts), sum(total_processed_wt), sum(production_time)  from processing '
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
            cursor.execute('select * from processing where processing_date = %s order by operation, start_time',
                           (report_date,))
            user_data = cursor.fetchall()


        return user_data

def change_date_format(date):
    # split_date = date.split('-')
    # new_date = split_date[2] + '-' + split_date[1] + '-' + split_date[0]

    new_date = datetime.strptime(str(date),'%Y-%m-%d').strftime('%d/%m/%y')
    return new_date