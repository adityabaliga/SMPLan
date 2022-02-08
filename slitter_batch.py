from database import CursorFromConnectionFromPool

class SlitterBatch:
    def __init__(self, slitter_batch, no_of_cutters, start_date, end_date, cutter_thickness, current_od, batch_length_limit, machine):
        self.slitter_batch = slitter_batch
        self.no_of_cutters = no_of_cutters
        self.start_date = start_date
        self.end_date = end_date
        self.cutter_thickness = cutter_thickness
        self.current_od = current_od
        self.batch_length_limit = batch_length_limit
        self.machine = machine


    @classmethod
    def getSlitterLst(cls):
        slitter_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select distinct slitter_batch from slitter_master")
            user_data = cursor.fetchall()
            for data in user_data:
                slitter_lst.append(data[0])

        return slitter_lst


    @classmethod
    def load_slitter(cls, slitter_batch):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from slitter_master where slitter_batch = %s",(slitter_batch,))
            user_data = cursor.fetchone()
            return SlitterBatch(slitter_batch=user_data[0], no_of_cutters=user_data[1], start_date=user_data[2],
                                end_date=user_data[7], cutter_thickness=user_data[3], current_od= user_data[4],
                                batch_length_limit=user_data[5], machine= user_data[6])


    @classmethod
    def after_return_from_grinding(cls, slitter_batch_no, end_date, return_date, new_od):
        with CursorFromConnectionFromPool() as cursor:

            cursor.execute('update slitter_grinding set grinding_date = %s where slitter_batch = %s and grinding_date is NULL',(end_date,slitter_batch_no))
            cursor.execute('update slitter_master set last_grinding_date = %s, current_od = %s where slitter_batch = %s ',(end_date, new_od, slitter_batch_no))
            cursor.execute('insert into slitter_grinding (slitter_batch, current_od, prev_grinding_date, slitter_1, '
                           'slitter_2, slitter_3, slitter_4, slitter_5, slitter_6, slitter_7, slitter_8, slitter_9, '
                           'slitter_10, slitter_11, slitter_12, slitter_13, slitter_14, slitter_15, slitter_16, '
                           'slitter_17, slitter_18, slitter_19, slitter_20, slitter_21, slitter_22, slitter_23, '
                           'slitter_24, slitter_25, slitter_26, slitter_27, slitter_28, slitter_29, slitter_30,'
                           'slitter_31, slitter_32, slitter_33, slitter_34, slitter_35, slitter_36, slitter_37'
                           ', slitter_38, slitter_39, slitter_40, slitter_41, slitter_42, slitter_43, slitter_44'
                           ', slitter_45, slitter_46, slitter_47, slitter_48, slitter_49, slitter_50) values'
                           '(%s, %s, %s, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0,'
                           ' 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, '
                           '0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)'
                           ,(slitter_batch_no, new_od, return_date))


    def get_slitter_grinding(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from slitter_grinding where slitter_batch = %s and grinding_date is NULL',(self.slitter_batch,))
            user_data = cursor.fetchone()
            return user_data