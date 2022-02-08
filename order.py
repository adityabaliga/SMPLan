from database import CursorFromConnectionFromPool
from order_detail import OrderDetail


class Order:
    def __init__(self, smpl_no, order_date, expected_date, processing_wt, status, remarks):
        self.smpl_no = smpl_no
        self.order_date = order_date
        self.expected_date = expected_date
        self.processing_wt = processing_wt
        self.status = status
        self.remarks = remarks

    @classmethod
    def load_from_db(cls, smpl_no, status):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from order_header where smpl_no = %s and status = %s', (smpl_no, status))
            user_data = cursor.fetchall()
            order_lst = []
            order_id_lst = []
            for lst in user_data:
                order = Order(smpl_no=lst[1], order_date=lst[2], expected_date=lst[3], processing_wt=lst[4],
                              status=lst[5], remarks=lst[6])
                order_lst.append(order)
                order_id_lst.append(lst[0])
        return zip(order_id_lst, order_lst)

    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "insert into order_header (smpl_no, order_date, expected_date, processing_wt, status, remarks) values "
                "( %s, %s, %s, %s, %s, %s)", (self.smpl_no, self.order_date, self.expected_date,
                                          self.processing_wt, self.status, self.remarks))
            # cursor.connection.commit()
            # last_row_id = cursor.lastrowid
            cursor.execute("select order_id from order_header where oid= %s", (cursor.lastrowid,))
            data = cursor.fetchone()
            return data[0]

    def cancel_order(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update order_header set status = 'Cancelled' where smpl_no = %s and order_date=%s",
                           (self.smpl_no, self.order_date))
            cursor.execute("select order_id from order_header where smpl_no = %s and order_date=%s",
                           (self.smpl_no, self.order_date))
            data = cursor.fetchone()
        OrderDetail.cancel_order(data[0])

    def order_on_hold(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update order_header set status = 'On Hold' where smpl_no = %s and order_date=%s",
                           (self.smpl_no, self.order_date))
            cursor.execute("select order_id from order_header where smpl_no = %s and order_date=%s",
                           (self.smpl_no, self.order_date))
            data = cursor.fetchone()
        OrderDetail.order_on_hold(data[0])

    def modify_order(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "update order_header set expected_date = %s, processing_wt = %s, remarks = %s where smpl_no = %s and status = 'Open'",
                (self.expected_date, self.processing_wt, self.remarks, self.smpl_no))
            cursor.execute("select order_id from order_header where smpl_no = %s and status = 'Open'", (self.smpl_no,))
            data = cursor.fetchone()
            return data[0]

    @classmethod
    def history_load_from_db(cls, smpl_no):
        order_id_lst = []
        order_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from order_header where smpl_no = %s', (smpl_no,))
            lst = cursor.fetchone()
            if lst:
                order = Order(smpl_no=lst[1], order_date=lst[2], expected_date=lst[3], processing_wt=lst[4],
                          status=lst[5], remarks=lst[6])

                order_id = int(lst[0])
                order_id_lst.append(order_id)
                order_lst.append(order)
        return zip(order_id_lst, order_lst)
