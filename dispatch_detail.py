from database import CursorFromConnectionFromPool
from decimal import *

class DispatchDetail:
    def __init__(self, dispatch_id, smpl_no, thickness, width, length, numbers, dispatch_wt, defective, no_of_pkts):
        self.dispatch_id = dispatch_id
        self.smpl_no = smpl_no
        self.thickness = thickness
        self.width = width
        self.length = length
        self.numbers = numbers
        self.dispatch_wt = dispatch_wt
        self.defective = defective
        self.no_of_pkts = no_of_pkts


    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("insert into dispatch_detail (dispatch_id, smpl_no, thickness, width, length, numbers, "
                           "weight, defective, no_of_packets) values (%s, %s, %s, %s, %s, %s, %s, %s, %s)",(self.dispatch_id, self.smpl_no,
                                                                                              self.thickness, self.width,
                                                                                              self.length, self.numbers,
                                                                                              self.dispatch_wt,
                                                                                              self.defective, self.no_of_pkts))


    @classmethod
    def get_details_by_id(cls, select_dispatch_hdr_id):
        dispatch_detail_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from dispatch_detail where dispatch_id = %s",(select_dispatch_hdr_id,))
            user_data = cursor.fetchall()
            for detail in user_data:
                dispatch_detail = DispatchDetail(select_dispatch_hdr_id, detail[2], float(detail[3]), float(detail[4]),
                                                 float(detail[5]), int(detail[6]), float(detail[7]), detail[8],
                                                 detail[9])
                dispatch_detail_lst.append(dispatch_detail)

        return dispatch_detail_lst


    @classmethod
    def load_from_db(cls,smpl_no):
        dispatch_detail_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from dispatch_detail where smpl_no = %s", (smpl_no,))
            user_data = cursor.fetchall()
            for detail in user_data:
                dispatch_detail = DispatchDetail(int(detail[1]), detail[2], float(detail[3]), float(detail[4]),
                                                 float(detail[5]), int(detail[6]), float(detail[7]), detail[8],
                                                 detail[9])
                dispatch_detail_lst.append(dispatch_detail)

        return dispatch_detail_lst

    @classmethod
    def get_daily_report(cls, dispatch_id):
        dispatch_detail_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from dispatch_detail where dispatch_id = %s", (dispatch_id,))
            user_data = cursor.fetchall()
            for detail in user_data:
                dispatch_detail = DispatchDetail(int(detail[1]), detail[2], float(detail[3]), float(detail[4]),
                                                 float(detail[5]), int(detail[6]), float(detail[7]), detail[8],
                                                 detail[9])
                dispatch_detail_lst.append(dispatch_detail)

        return dispatch_detail_lst