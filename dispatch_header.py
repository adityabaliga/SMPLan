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

    @classmethod
    def get_dispatch_costing_summary(from_date, to_date):
        try:


            conn = get_db_connection()

            # Query with TRANSFER TO filter
            query = """
                WITH RECURSIVE processing_chain AS (
                    SELECT 
                        dd.dispatch_detail_id,
                        dd.dispatch_id,
                        dd.smpl_no,
                        p.processing_id,
                        p.previous_processing_id,
                        p.operation,
                        p.production_time,
                        p.setting_time,
                        p.total_processed_wt,
                        p.no_of_helpers,
                        p.no_of_qc,
                        1 as processing_level
                    FROM dispatch_detail dd
                    INNER JOIN dispatch_header dh ON dd.dispatch_id = dh.dispatch_id
                    INNER JOIN processing p ON dd.processing_id = p.processing_id
                    WHERE dh.dispatch_date >= %(from_date)s 
                        AND dh.dispatch_date <= %(to_date)s
                        AND (dh.remarks NOT LIKE '%%TRANSFER TO%%' OR dh.remarks IS NULL)
                    UNION ALL
                    SELECT 
                        pc.dispatch_detail_id,
                        pc.dispatch_id,
                        pc.smpl_no,
                        p.processing_id,
                        p.previous_processing_id,
                        p.operation,
                        p.production_time,
                        p.setting_time,
                        p.total_processed_wt,
                        p.no_of_helpers,
                        p.no_of_qc,
                        pc.processing_level + 1
                    FROM processing_chain pc
                    INNER JOIN processing p ON pc.previous_processing_id = p.processing_id
                    WHERE pc.processing_level < 10
                ),
                processing_costs AS (
                    SELECT 
                        pc.dispatch_detail_id,
                        pc.operation,
                        pc.production_time,
                        pc.setting_time,
                        pc.total_processed_wt,
                        pc.no_of_helpers,
                        pc.no_of_qc,
                        pc.processing_level,
                        COALESCE(mr.rate_per_hour, 0) as machine_rate,
                        COALESCE(mr.rate_per_hour, 0) * (pc.production_time + pc.setting_time)::decimal / 60.0 as machine_cost,
                        212.0 * (COALESCE(pc.no_of_helpers, 0) + COALESCE(pc.no_of_qc, 0)) * (pc.production_time + pc.setting_time)::decimal / 60.0 as labour_cost,
                        (COALESCE(mr.rate_per_hour, 0) * (pc.production_time + pc.setting_time)::decimal / 60.0) + (212.0 * (COALESCE(pc.no_of_helpers, 0) + COALESCE(pc.no_of_qc, 0)) * (pc.production_time + pc.setting_time)::decimal / 60.0) as total_cost,
                        CASE 
                            WHEN pc.total_processed_wt > 0 THEN
                                ((COALESCE(mr.rate_per_hour, 0) * (pc.production_time + pc.setting_time)::decimal / 60.0) + (212.0 * (COALESCE(pc.no_of_helpers, 0) + COALESCE(pc.no_of_qc, 0)) * (pc.production_time + pc.setting_time)::decimal / 60.0)) / (pc.total_processed_wt::decimal / 1000.0)
                            ELSE 0
                        END as cost_per_mt
                    FROM processing_chain pc
                    LEFT JOIN machine_rates mr ON pc.operation = mr.machine_name
                )
                SELECT 
                    dh.dispatch_id,
                    dh.customer,
                    dh.vehicle_no,
                    dh.dispatch_date,
                    dd.dispatch_detail_id,
                    dd.smpl_no,
                    dd.thickness,
                    dd.width,
                    dd.length,
                    dd.weight as dispatch_weight,
                    dd.numbers as dispatch_numbers,
                    dd.packet_name,
                    string_agg(pc.operation, ', ' ORDER BY pc.processing_level DESC) as operations_list,
                    ROUND(COALESCE(SUM(pc.machine_cost), 0)::numeric, 2) as total_machine_cost,
                    ROUND(COALESCE(SUM(pc.labour_cost), 0)::numeric, 2) as total_labour_cost,
                    ROUND(COALESCE(SUM(pc.total_cost), 0)::numeric, 2) as total_processing_cost,
                    ROUND((COALESCE(SUM(pc.cost_per_mt), 0) / 1000.0)::numeric) as total_cost_per_mt,
                    COUNT(pc.operation) as total_processing_steps
                FROM dispatch_header dh
                INNER JOIN dispatch_detail dd ON dh.dispatch_id = dd.dispatch_id
                LEFT JOIN processing_costs pc ON dd.dispatch_detail_id = pc.dispatch_detail_id
                WHERE dh.dispatch_date >= %(from_date)s 
                    AND dh.dispatch_date <= %(to_date)s
                    AND (dh.remarks NOT LIKE '%%TRANSFER TO%%' OR dh.remarks IS NULL)
                GROUP BY dh.dispatch_id, dh.customer, dh.vehicle_no, dh.dispatch_date,
                         dd.dispatch_detail_id, dd.smpl_no, dd.thickness, dd.width, dd.length,
                         dd.weight, dd.numbers, dd.packet_name
                ORDER BY dh.dispatch_date, dh.dispatch_id, dd.dispatch_detail_id;
                """

            df = pd.read_sql_query(query, conn, params={'from_date': from_date, 'to_date': to_date})

            conn.close()

            # Create Excel file
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Dispatch Costs', index=False)

                # Auto-adjust column widths
                worksheet = writer.sheets['Dispatch Costs']
                for idx, col in enumerate(df.columns):
                    max_length = max(
                        df[col].astype(str).apply(len).max(),
                        len(str(col))
                    ) + 2
                    worksheet.column_dimensions[chr(65 + idx)].width = min(max_length, 50)

            output.seek(0)

            return send_file(
                output,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=f'dispatch_costs_{from_date}_to_{to_date}.xlsx'
            )

        except Exception as e:
            import traceback
            traceback.print_exc()
            return jsonify({'error': str(e)}), 500