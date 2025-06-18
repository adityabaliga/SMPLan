from database import CursorFromConnectionFromPool
from decimal import *
import time

class DispatchHeader:
    def __init__(self, vehicle_no, customer, dispatch_date, dispatch_time, invoice_no, remarks, entry_by):
        self.vehicle_no = vehicle_no
        self.customer = customer
        self.dispatch_date = dispatch_date
        self.dispatch_time = dispatch_time
        self.invoice_no = invoice_no
        self.remarks = remarks
        self.entry_by = entry_by

    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("insert into dispatch_header (vehicle_no, dispatch_date, dispatch_time, customer, invoice_no, remarks, entry_by) values"
                           "(%s, %s, %s, %s, %s, %s, %s)",(self.vehicle_no, self.dispatch_date, self.dispatch_time,
                                                       self.customer, self.invoice_no, self.remarks, self.entry_by))

            cursor.execute("select dispatch_id from dispatch_header where oid= %s", (cursor.lastrowid,))
            data = cursor.fetchone()
            return data[0]


    @classmethod
    def get_dispatch_lst_by_date(cls, date):
        dispatch_lst = []
        dispatch_hdr_id_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select sum(weight), dispatch_detail.dispatch_id,  customer, vehicle_no, dispatch_time, invoice_no  from dispatch_header, dispatch_detail "
                            "where dispatch_date = %s and dispatch_header.dispatch_id = dispatch_detail.dispatch_id "
                            "group by dispatch_header.customer, dispatch_detail.dispatch_id, vehicle_no, dispatch_time, invoice_no order by dispatch_time asc",(date,))
            user_data = cursor.fetchall()
            return user_data

    @classmethod
    def get_daily_report(cls, date):
        dispatch_lst = []
        dispatch_hdr_id_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "select sum(weight), customer from dispatch_header, dispatch_detail "
                "where dispatch_date = %s and dispatch_header.dispatch_id = dispatch_detail.dispatch_id "
                "and remarks NOT LIKE %s"
                "group by dispatch_header.customer",
                (date, '%TRANSFER%'))
            user_data = cursor.fetchall()
            return user_data

    @classmethod
    def get_hdr_by_id(cls, select_dispatch_hdr_id):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from dispatch_header where dispatch_id = %s',(select_dispatch_hdr_id,))
            user_data = cursor.fetchone()
        dispatch_hdr = DispatchHeader(user_data[1], user_data[6], user_data[2], user_data[3], user_data[4],
                                      user_data[5], user_data[7])
        return dispatch_hdr

    @classmethod
    def load_from_db(cls, dispatch_id):
        dispatch_lst = []
        dispatch_hdr_id_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from dispatch_header where dispatch_id = %s order by dispatch_time asc", (dispatch_id,))
            user_data = cursor.fetchall()
        for lst in user_data:
            dispatch_lst.append(DispatchHeader(lst[1], lst[6], lst[2], lst[3], lst[4], lst[5], lst[7]))

        return dispatch_lst

    @classmethod
    def update_invoice_no(cls, dispatch_id, invoice_no, dispatch_date, vehicle_no):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update dispatch_header set invoice_no = %s, dispatch_date = %s, vehicle_no = %s "
                           "where dispatch_id = %s",
                           (invoice_no, dispatch_date, vehicle_no, dispatch_id))

    @classmethod
    def get_monthly_report(cls, month, year):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "SELECT  dd.unit, SUM(dd.weight) AS total_weight FROM dispatch_header dh "
                "JOIN dispatch_detail dd ON dh.dispatch_id = dd.dispatch_id WHERE "
                "extract(month from dh.dispatch_date) = %s  and extract(year from dh.dispatch_date) = %s "
                "and dh.invoice_no != 'TRANSFER' GROUP BY dd.unit ORDER BY dd.unit",
                (month, year))
            user_data = cursor.fetchall()
            return user_data

    @classmethod
    def get_monthly_report_by_customer(cls, month, year):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "SELECT  dh.customer, SUM(dd.weight) AS total_weight FROM dispatch_header dh "
                "JOIN dispatch_detail dd ON dh.dispatch_id = dd.dispatch_id WHERE "
                "extract(month from dh.dispatch_date) = %s  and extract(year from dh.dispatch_date) = %s"
                "and dh.invoice_no != 'TRANSFER' GROUP BY dh.customer ORDER BY total_weight desc",
                (month, year))
            user_data = cursor.fetchall()
            return user_data

    @classmethod
    def get_daily_report_whatsapp(cls, date):
        with CursorFromConnectionFromPool() as cursor:
            
            cursor.execute(
                "SELECT dd.unit, SUM(dd.weight) AS total_weight FROM dispatch_header dh "
                "JOIN dispatch_detail dd ON dh.dispatch_id = dd.dispatch_id WHERE "
                "dh.dispatch_date = %s and dh.invoice_no != 'TRANSFER' GROUP BY dd.unit ORDER BY "
                "dd.unit ", (date, ))
            user_data = cursor.fetchall()
            return user_data

    @classmethod
    def honda_dispatch_for_month(cls, month, year, honda_schedule_sizes):
        query_string = (("WITH daily_totals AS (SELECT EXTRACT(DAY FROM dispatch_header.dispatch_date)::int as day_of_month, "
                         "dispatch_detail.width, dispatch_detail.length, SUM(dispatch_detail.numbers) as total "
                         "FROM dispatch_header "
                         "JOIN dispatch_detail ON dispatch_header.dispatch_id = dispatch_detail.dispatch_id "
                         "WHERE dispatch_header.customer = 'HONDA TRADING CORPORATION INDIA PVT LTD' "
                         "AND EXTRACT(MONTH FROM dispatch_header.dispatch_date) = " + str(month) +
                         "AND EXTRACT(YEAR FROM dispatch_header.dispatch_date) =  " + str(year) +
                         "GROUP BY day_of_month, dispatch_detail.width, dispatch_detail.length) SELECT day_of_month"))

        for sizes in honda_schedule_sizes:
            query_string += (", coalesce(MAX(CASE WHEN width = " + str(sizes[0]) + (" AND length = " + str(sizes[1]) +
                                                                            " THEN total END),0) "
                                                                            "AS \"") + str(sizes[0]) + "x"
                                                                            + str(sizes[1]) +"\" ")

        query_string += "FROM daily_totals GROUP BY day_of_month ORDER BY day_of_month;"
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(query_string)
            user_data = cursor.fetchall()
            return user_data


    @classmethod
    def honda_schedule_sizes(cls, month, year):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("SELECT DISTINCT width, length FROM dispatch_detail JOIN dispatch_header ON "
                           " dispatch_header.dispatch_id = dispatch_detail.dispatch_id "
                           "WHERE dispatch_header.customer = 'HONDA TRADING CORPORATION INDIA PVT LTD' " 
                           "AND EXTRACT(MONTH FROM dispatch_header.dispatch_date) = %s"
                           " AND EXTRACT(YEAR FROM dispatch_header.dispatch_date) = %s and length != 0 "
                           "and dispatch_header.invoice_no != 'TRANSFER'", (month, year))
            user_data = cursor.fetchall()
            return user_data

    def save_to_staging_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("insert into staging_dispatch_header (vehicle_no, dispatch_date, dispatch_time, customer, "
                           "invoice_no, remarks, entry_by) values"
                           "(%s, %s, %s, %s, %s, %s, %s)", (self.vehicle_no, self.dispatch_date, self.dispatch_time,
                                                       self.customer, self.invoice_no, self.remarks, self.entry_by))

            cursor.execute("select dispatch_id from staging_dispatch_header where oid= %s", (cursor.lastrowid,))
            data = cursor.fetchone()
            return data[0]

    @classmethod
    def delete_staging_data(cls, delete_staging_data):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("delete from staging_dispatch_detail where dispatch_id = %s",(delete_staging_data,))
            cursor.execute("delete from staging_dispatch_header where dispatch_id = %s",(delete_staging_data,))


    @classmethod
    def get_open_staging_data(cls):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from staging_dispatch_header order by dispatch_date desc")
            user_data = cursor.fetchall()
            return user_data

    @classmethod
    def get_staging_header(cls, staging_dispatch_id):
        user_data = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from staging_dispatch_header where dispatch_id = %s", (int(staging_dispatch_id),))
            user_data = cursor.fetchone()

            dispatch_header = DispatchHeader(user_data[1], user_data[6], user_data[2], user_data[3], user_data[4], user_data[5], user_data[7])
            return dispatch_header