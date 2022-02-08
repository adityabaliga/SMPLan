from database import CursorFromConnectionFromPool


class SlitterUsage:
    def __init__(self, processing_id, smpl_no, slitter_batch, slitter_number, length, thickness):
        self.processing_id = processing_id
        self.smpl_no = smpl_no
        self.slitter_batch = slitter_batch
        self.slitter_number = slitter_number
        self.length = length
        self.thickness = thickness

    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("insert into slitter_usage (processing_id,smpl_no,slitter_batch,slitter_number,length, thickness)"
                           "values (%s,%s,%s,%s,%s,%s)",(self.processing_id, self.smpl_no, self.slitter_batch,
                                                      self.slitter_number, self.length, self.thickness))
            slitter_no = "slitter_" + self.slitter_number
            query = "select " + slitter_no + " from slitter_grinding where slitter_batch = '" + self.slitter_batch + "' and grinding_date is NULL "

            cursor.execute(query)
            user_data = cursor.fetchone()
            if user_data:
                new_length = int(self.length) + int(user_data[0])
            else:
                new_length = int(self.length)

            update_query = "update slitter_grinding set " + slitter_no + " = " + str(new_length) + " where slitter_batch = '" + self.slitter_batch + "' and grinding_date is NULL"
            cursor.execute(update_query)