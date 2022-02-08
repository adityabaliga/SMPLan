from database import CursorFromConnectionFromPool
from decimal import *



class OrderDetail:
    def __init__(self, order_id, smpl_no, operation, ms_width, ms_length, cut_width, cut_length, processing_wt, numbers,
                 fg_yes_no, no_per_packet, no_of_packets, packing, remarks, status, stage_no, tolerance, lamination,
                 wt_per_pkt, internal_dia):

        self.order_id = order_id
        self.smpl_no = smpl_no
        self.operation = operation
        self.ms_width = ms_width
        self.ms_length = ms_length
        self.cut_width = cut_width
        self.cut_length = cut_length
        self.processing_wt = processing_wt
        self.numbers = numbers
        self.fg_yes_no = fg_yes_no
        self.no_per_packet = no_per_packet
        self.no_of_packets = no_of_packets
        self.packing = packing
        self.remarks = remarks
        self.status = status
        self.stage_no = stage_no
        self.tolerance = tolerance
        self.lamination = lamination
        self.wt_per_pkt =  wt_per_pkt
        self.internal_dia = internal_dia

    @classmethod
    def load_from_db(cls, smpl_no, order_id):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from order_details where smpl_no = %s and order_id = %s order by stage_no, '
                           'operation, order_detail_id asc',
                           (smpl_no, order_id))
            user_data = cursor.fetchall()
            order_detail_lst = []
            order_detail_id_lst = []
            for lst in user_data:
                order_detail = OrderDetail(order_id=lst[1], smpl_no=lst[2], operation=lst[3], ms_width=lst[4],
                                           ms_length=lst[5], cut_width=lst[6], cut_length=lst[7], processing_wt=lst[8],
                                           numbers=lst[9], fg_yes_no=lst[10], no_per_packet=lst[11],
                                           no_of_packets=lst[12],
                                           packing=lst[13], remarks=lst[14], status=lst[15], stage_no=lst[16],
                                           tolerance=lst[17], lamination=lst[18], wt_per_pkt=lst[19], internal_dia=lst[20])
                order_detail_lst.append(order_detail)
                order_detail_id_lst.append(lst[0])
        return zip(order_detail_id_lst,order_detail_lst)

    @classmethod
    def load_ids_from_db(cls, smpl_no, order_id):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select order_detail_id from order_details where smpl_no = %s and order_id = %s',
                           (smpl_no, order_id))
            user_data = cursor.fetchall()
            order_detail_id_lst = []
            for lst in user_data:
                order_detail_id_lst.append(lst[0])
        return order_detail_id_lst

    @classmethod
    def load_ids_for_same_stage_no(cls, smpl_no, order_id, stage_no):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select order_detail_id from order_details where smpl_no = %s and order_id = %s and stage_no = %s',
                           (smpl_no, order_id, stage_no))
            user_data = cursor.fetchall()
            order_detail_id_lst = []
            for lst in user_data:
                order_detail_id_lst.append(lst[0])
        return order_detail_id_lst

    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("insert into order_details (order_id, smpl_no, operation, ms_width, ms_length, cc_width, "
                           "cc_length, processing_wt, processing_numbers, fg_yes_no, no_per_packet, "
                           "no_of_packets, packing_type, remarks, status, "
                           "stage_no, tolerance, lamination, wt_per_pkt, internal_dia)"
                           " values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (self.order_id, self.smpl_no, self.operation, self.ms_width, self.ms_length, self.cut_width,
                            self.cut_length, self.processing_wt, self.numbers, self.fg_yes_no,
                            self.no_per_packet, self.no_of_packets, self.packing, self.remarks,
                            self.status, self.stage_no, self.tolerance, self.lamination, self.wt_per_pkt,
                            self.internal_dia))

    @classmethod
    def cancel_order(cls, order_id):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update order_details set status = 'Cancelled' where order_id = %s", (order_id,))

    @classmethod
    def order_on_hold(cls, order_id):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update order_details set status = 'On Hold' where order_id = %s", (order_id,))

    def modify_detail(self, order_detail_id):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "update order_details set operation = %s, ms_width = %s, ms_length = %s, cc_width = %s, cc_length = %s,"
                "processing_wt = %s, processing_numbers = %s, fg_yes_no = %s, no_per_packet= %s, no_of_packets = %s, "
                "packing_type = %s, remarks = %s, status = %s, stage_no = %s, tolerance = %s, lamination = %s, "
                "wt_per_pkt = %s, internal_dia = %s where order_detail_id = %s",
                (self.operation, self.ms_width, self.ms_length, self.cut_width, self.cut_length, self.processing_wt,
                 self.numbers, self.fg_yes_no, self.no_per_packet, self.no_of_packets, self.packing, self.remarks,
                 self.status, self.stage_no, self.tolerance, self.lamination, self.wt_per_pkt,
                 self.internal_dia, int(order_detail_id)))

    @classmethod
    def smpl_lst_by_operation(cls, status, operation):

        with CursorFromConnectionFromPool() as cursor:
            if operation == 'Mini_Slitting':
                cursor.execute(
                    "select distinct on (smpl_no, ms_width) * from order_details where status = %s and operation like %s",
                    (status, operation + '%'))
            if operation == 'Reshearing' or operation == "Narrow_CTL":
                cursor.execute(
                    "select distinct on (smpl_no, ms_width, ms_length) * from order_details where status = %s and operation like %s",
                    (status, operation + '%'))
            else:
                cursor.execute("select distinct on (smpl_no) * from order_details where status = %s and operation like %s",(status, operation + '%'))

            user_data = cursor.fetchall()
            order_detail_lst = []
            if user_data:
                for lst in user_data:
                    order_detail = OrderDetail(order_id=lst[1], smpl_no=lst[2], operation=lst[3], ms_width=lst[4],
                                               ms_length=lst[5], cut_width=lst[6], cut_length=lst[7],
                                               processing_wt=float(lst[8]), numbers=lst[9], fg_yes_no=lst[10],
                                               no_per_packet=lst[11], no_of_packets=lst[12], packing=lst[13],
                                               remarks=lst[14], status=lst[15], stage_no=lst[16],
                                               tolerance=lst[17], lamination=lst[18], wt_per_pkt=lst[19],
                                               internal_dia=lst[20])
                    order_detail_lst.append(order_detail)
        return order_detail_lst

    @classmethod
    def detail_complete(cls,order_detail_id):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from order_details where order_detail_id = %s', (order_detail_id,))
            user_data = cursor.fetchone()
            # if user_data:
            order_detail = OrderDetail(order_id=user_data[1], smpl_no=user_data[2], operation=user_data[3], ms_width=user_data[4],
                                       ms_length=user_data[5], cut_width=user_data[6], cut_length=user_data[7],
                                       processing_wt=float(user_data[8]),
                                       numbers=user_data[9], fg_yes_no=user_data[10], no_per_packet=user_data[11],
                                       no_of_packets=user_data[12],
                                       packing=user_data[13], remarks=user_data[14], status=user_data[15], stage_no=user_data[16],
                                       tolerance=user_data[17], lamination=user_data[18], wt_per_pkt=user_data[19],
                                       internal_dia=user_data[20])
            cursor.execute("select weight from current_stock where smpl_no = %s and width = %s and length = %s",
                           (order_detail.smpl_no,order_detail.cut_width,order_detail.cut_length))
            user_data1 = cursor.fetchone()
            processed_wt = 0
            #numbers = 0
            if user_data1:
                processed_wt = float(user_data1[0])
            #    numbers = Decimal(user_data1[1])

        # check_weight = 0.98 * float(order_detail.processing_wt)
        if processed_wt > (0.98 * float(order_detail.processing_wt)):
            order_detail.status = "Completed"

            order_detail.modify_detail(order_detail_id)

            OrderDetail.check_stage_complete(order_detail.order_id,order_detail.stage_no)

    @classmethod
    def check_stage_complete(cls,order_id, stage_no):
        flag = 1
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select status from order_details where order_id = %s and stage_no = %s",(order_id,stage_no))
            user_data = cursor.fetchall()
        for status in user_data:
            if status[0] != "Completed":
                flag = 0

        if flag == 1:
            stage_no += 1
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select order_detail_id from order_details where order_id = %s and stage_no = %s",(order_id,stage_no))
                user_data = cursor.fetchall()
                if user_data:
                    for order_detail_id in user_data:
                        cursor.execute("update order_details set status = 'Ready' where order_detail_id = %s",(order_detail_id,))
                else:
                    cursor.execute("update order_header set status='Closed' where order_id = %s",(order_id,))


    @classmethod
    def complete_processing_on_del(cls, smpl_no, width, length):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from order_details where smpl_no = %s and ms_width = %s and ms_length = %s",(smpl_no, width, length))
            od_lst = cursor.fetchall()
        if od_lst:
            for user_data in od_lst:
                order_detail = OrderDetail(order_id=user_data[1], smpl_no=user_data[2], operation=user_data[3],
                                           ms_width=user_data[4],
                                           ms_length=user_data[5], cut_width=user_data[6], cut_length=user_data[7],
                                           processing_wt=float(user_data[8]),
                                           numbers=user_data[9], fg_yes_no=user_data[10],
                                           no_per_packet=user_data[11],
                                           no_of_packets=user_data[12],
                                           packing=user_data[13], remarks=user_data[14], status=user_data[15],
                                           stage_no=user_data[16],
                                           tolerance=user_data[17], lamination=user_data[18],
                                           wt_per_pkt=user_data[19],
                                           internal_dia=user_data[20])
                order_detail.status = "Completed"
                order_detail.modify_detail(int(user_data[0]))
                OrderDetail.check_stage_complete(order_detail.order_id,order_detail.stage_no)