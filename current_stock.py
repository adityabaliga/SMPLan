from database import CursorFromConnectionFromPool
from decimal import *
from order_detail import OrderDetail


class CurrentStock:
    def __init__(self, smpl_no, customer, weight, numbers, thickness, width, length, status, grade, unit, packet_name):
        self.smpl_no = smpl_no
        self.customer = customer
        self.weight = weight
        self.numbers = numbers
        self.thickness = thickness
        self.width = width
        self.length = length
        self.status = status
        self.grade = grade
        self.unit = unit
        self.packet_name = packet_name

    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("insert into current_stock (smpl_no,weight,numbers,width,length,status,customer,thickness"
                           ",grade, unit, packet_name) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (self.smpl_no, self.weight, self.numbers, self.width, self.length, self.status, self.customer,
                           self.thickness, self.grade, self.unit, self.packet_name))

    def update_status(self, status):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update current_stock set status = %s where smpl_no = %s and width = %s and length = %s",
                           (status, self.smpl_no, self.width, self.length))

    @classmethod
    def update_status_cls(cls,cs_id,status):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update current_stock set status = %s where cs_id = %s",(status, cs_id))

    @classmethod
    def smpl_list_for_modify_order(cls):
        user_data = []
        cs_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from current_stock where status= 'Order' order by smpl_no asc")
            #cursor.execute("select * from current_stock order by smpl_no asc")
            user_data = cursor.fetchall()

            if user_data:
                for lst in user_data:
                    cs = CurrentStock(smpl_no=lst[1], weight=Decimal(lst[2]), numbers=int(lst[3]),
                                      width=Decimal(lst[4]),
                                      length=Decimal(lst[5]), status=lst[6], customer=lst[7], thickness=Decimal(lst[8]),
                                      grade=lst[9], unit=lst[10], packet_name = lst [11])
                    cs_lst.append(cs)

                return cs_lst
            else:
                return None

    @classmethod
    def smpl_list_for_place_order(cls, string):
        user_data = []
        cs_lst = []
        if string == 'SMPL':
            query = "select * from current_stock where customer not like 'TSDPL%' and status = 'RM' or status = 'HC' order by smpl_no asc"
        if string == 'TR':
            query = "select * from current_stock where customer like 'TSDPL%'  and status = 'RM' or status = 'HC' order by smpl_no asc"
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(query)
            user_data = cursor.fetchall()

        if user_data:
            for lst in user_data:
                cs = CurrentStock(smpl_no=lst[1], weight=Decimal(lst[2]), numbers=int(lst[3]), width=Decimal(lst[4]),
                                  length=Decimal(lst[5]), status=lst[6], customer=lst[7], thickness=Decimal(lst[8]),
                                  grade=lst[9], unit=lst[10], packet_name = lst [11])
                cs_lst.append(cs)

            return cs_lst
        else:
            return None

    @classmethod
    def smpl_for_processing_search_lst(cls, operation, smpl_no, unit):
        user_data = []
        cs_lst = []
        cs_id_lst = []
        smpl_no_like = '%' + smpl_no + '%'

        if operation == "CTL" or operation == "Slitting":
            with CursorFromConnectionFromPool() as cursor:
                if unit == '0':
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and smpl_no like %s order by smpl_no asc", (smpl_no_like,))
                else:
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                               "length = 0 and unit = %s  and smpl_no like %s order by smpl_no asc", (str(unit),smpl_no_like))


                user_data = cursor.fetchall()

        if operation == "Narrow_CTL":
            with CursorFromConnectionFromPool() as cursor:
                if unit == '0':
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP')"
                                   " and "
                                   "length = 0 and smpl_no like %s and width <=800 order by "
                                   "smpl_no asc", (smpl_no_like,))
                else:
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP')"
                                   " and "
                                   "length = 0 and unit = %s  and smpl_no like %s and width <=800 order by "
                                   "smpl_no asc", (str(unit),smpl_no_like))


                user_data = cursor.fetchall()

        if operation == "Mini_Slitting":
            with CursorFromConnectionFromPool() as cursor:
                if unit == '0':
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP')"
                                   " and "
                                   "length = 0 and smpl_no like %s and width <=500 order by "
                                   "smpl_no asc", (smpl_no_like,))
                else:
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP')"
                                   " and "
                                   "length = 0 and unit = %s  and smpl_no like %s and width <=500 order by "
                                   "smpl_no asc", (str(unit),smpl_no_like))


                user_data = cursor.fetchall()

        if operation == "Reshearing" or operation =="Lamination":
            with CursorFromConnectionFromPool() as cursor:
                if unit == '0':
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                               "length > 0 and smpl_no like %s order by smpl_no asc", (smpl_no,))
                else:
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length > 0  and unit = %s and smpl_no like %s order by smpl_no asc", (str(unit), smpl_no))
                user_data = cursor.fetchall()

        if user_data:
            for lst in user_data:
                cs = CurrentStock(smpl_no=lst[1], weight=Decimal(lst[2]), numbers=int(lst[3]), width=Decimal(lst[4]),
                                  length=Decimal(lst[5]), status=lst[6], customer=lst[7], thickness=Decimal(lst[8]),
                                  grade=lst[9], unit=lst[10], packet_name = lst [11])
                cs_lst.append(cs)

                cs_id_lst.append(lst[0])
            return zip(cs_id_lst, cs_lst)
        else:
            return None

    @classmethod
    def smpl_list_for_processing(cls, operation, customer_type, unit):
        user_data = []
        cs_lst = []
        cs_id_lst = []

        if operation == "CTL" or operation == "Slitting":
            with CursorFromConnectionFromPool() as cursor:
                if customer_type == "smpl":
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                                   "length = 0 and unit = %s  and customer not like 'TSDPL' order by smpl_no asc", (str(unit),))
                if customer_type == "tr":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and unit = %s  and customer like 'TSDPL' order by smpl_no asc", (str(unit),))
                user_data = cursor.fetchall()

        if operation == "Narrow_CTL":
            with CursorFromConnectionFromPool() as cursor:
                if customer_type == "smpl":
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP')"
                                   " and "
                                   "length = 0 and unit = %s  and customer not like 'TSDPL' and width <=800 order by "
                                   "smpl_no asc", (str(unit),))
                if customer_type == "tr":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and unit = %s  and customer like 'TSDPL' and width <=800 order by smpl_no asc"
                        , (str(unit),))
                user_data = cursor.fetchall()

        if operation == "Mini_Slitting":
            with CursorFromConnectionFromPool() as cursor:
                if customer_type == "smpl":
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP')"
                                   " and "
                                   "length = 0 and unit = %s  and customer not like 'TSDPL' and width <=600 order by "
                                   "smpl_no asc", (str(unit),))
                if customer_type == "tr":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and unit = %s  and customer like 'TSDPL' and width <=500 order by smpl_no asc"
                        , (str(unit),))
                user_data = cursor.fetchall()

        if operation == "Reshearing" or operation =="Lamination" or operation == "Levelling":
            with CursorFromConnectionFromPool() as cursor:
                if customer_type == "smpl":
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                               "length > 0  and unit = %s and customer not like 'TSDPL' order by smpl_no asc", (str(unit),))
                if customer_type == "tr":
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                               "length > 0  and unit = %s and customer like 'TSDPL' order by smpl_no asc", (str(unit),))
                user_data = cursor.fetchall()

        if user_data:
            for lst in user_data:
                cs = CurrentStock(smpl_no=lst[1], weight=Decimal(lst[2]), numbers=int(lst[3]), width=Decimal(lst[4]),
                                  length=Decimal(lst[5]), status=lst[6], customer=lst[7], thickness=Decimal(lst[8]),
                                  grade=lst[9], unit=lst[10], packet_name = lst [11])
                cs_lst.append(cs)

                cs_id_lst.append(lst[0])
            return zip(cs_id_lst, cs_lst)
        else:
            return None

    @classmethod
    def load_smpl_by_smplno(cls,smpl_no, unit):
        user_data = []
        cs_lst = []
        cs_id_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from current_stock where smpl_no = %s and unit = %s ",(smpl_no, unit))
            user_data = cursor.fetchall()
            if user_data:
                for lst in user_data:
                    cs = CurrentStock(smpl_no=lst[1], weight=Decimal(lst[2]), numbers=int(lst[3]), width=Decimal(lst[4]),
                                      length=Decimal(lst[5]), status=lst[6], customer=lst[7], thickness=Decimal(lst[8]),
                                      grade=lst[9], unit=lst[10], packet_name = lst [11])
                    cs_lst.append(cs)
                    cs_id_lst.append(lst[0])

        return zip(cs_id_lst, cs_lst)

    @classmethod
    def get_smpl_for_fg_to_wip(cls, smpl_no):
        user_data = []
        cs_lst = []
        cs_id_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from current_stock where smpl_no = %s and status = 'FG'",(smpl_no,))
            user_data = cursor.fetchall()

            if user_data:
                for lst in user_data:
                    cs = CurrentStock(smpl_no=lst[1], weight=Decimal(lst[2]), numbers=int(lst[3]), width=Decimal(lst[4]),
                                      length=Decimal(lst[5]), status=lst[6], customer=lst[7], thickness=Decimal(lst[8]),
                                      grade=lst[9], unit=lst[10], packet_name=lst[11])
                    cs_lst.append(cs)
                    cs_id_lst.append(lst[0])

            return zip(cs_id_lst, cs_lst)

    @classmethod
    def load_smpl_for_history(cls, smpl_no):
        cs_lst = []
        user_data = []

        with CursorFromConnectionFromPool() as cursor:
            user_data = cursor.execute("select * from current_stock where smpl_no = %s",(smpl_no, ))

            user_data = cursor.fetchall()

            if user_data:
                for lst in user_data:
                    cs = CurrentStock(smpl_no=lst[1], weight=Decimal(lst[2]), numbers=int(lst[3]),
                                      width=Decimal(lst[4]),
                                      length=Decimal(lst[5]), status=lst[6], customer=lst[7], thickness=Decimal(lst[8]),
                                      grade=lst[9], unit=lst[10], packet_name = lst [11])
                    cs_lst.append(cs)


                return cs_lst
            else:
                return None

    @classmethod
    def load_smpl_by_id(cls, cs_id):
        user_data = []
        cs_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from current_stock where cs_id = %s", (cs_id,))
            user_data = cursor.fetchone()

            if user_data:
                cs = CurrentStock(smpl_no=user_data[1], weight=Decimal(user_data[2]), numbers=int(user_data[3]),
                                  width=Decimal(user_data[4]), length=Decimal(user_data[5]), status=user_data[6],
                                  customer=user_data[7], thickness=Decimal(user_data[8]), grade=user_data[9],
                                  unit=user_data[10], packet_name = user_data[11])

                return cs
            else:
                return None

    @classmethod
    def change_wt(cls, smpl_no, width, length, processed_wt, actual_no_of_pieces, sign, status):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                           "and length = %s and status = %s", (smpl_no, width, length, status))
            user_data = cursor.fetchone()
            if user_data:
                weight = Decimal(user_data[0])
                numbers = Decimal(user_data[1])
                cs_id = int(user_data[3])
                if sign == "minus":
                    new_weight = weight - Decimal(processed_wt)
                    new_weight = round(new_weight,3)
                    if numbers > 1:
                        new_numbers = numbers - Decimal(actual_no_of_pieces)
                    else:
                        new_numbers = numbers
                if sign == "plus":
                    new_weight = weight + Decimal(processed_wt)
                    new_weight = round(new_weight, 3)
                    # if numbers > 1:
                    new_numbers = numbers + Decimal(actual_no_of_pieces)
                    #else:
                    #    new_numbers = numbers

                if new_weight < 0.5 and sign == "minus" and length == 0:
                    #OrderDetail.complete_processing_on_del(smpl_no, width, length)
                    #CurrentStock.delete_record(cs_id)

                    cursor.execute("delete from current_stock where cs_id = %s", (cs_id,))

                    # This is done when the RM is over but for some reason the order could not be completed
                    # This could when the RM is thickness is more or wrong calc of material or processing mistake/change

                    return "complete"
                else:
                    cursor.execute("update current_stock set weight = %s, numbers = %s where cs_id = %s",
                                   (new_weight, new_numbers, cs_id))
                    return "continue"
            else:
                return "insert"




    @classmethod
    def delete_record(cls, cs_id):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('delete from current_stock where cs_id = %s',(cs_id,))

    @classmethod
    def get_stock(cls, stock_type,unit):
        user_data = []
        cs_lst=[]
        cs_id_lst =[]

        if stock_type == 'All':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where unit = '%s' order by smpl_no asc",(unit,))
                user_data = cursor.fetchall()
        else:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where status = %s and unit = %s order by smpl_no asc",(stock_type,unit))
                user_data = cursor.fetchall()

        for lst in user_data:
            cs = CurrentStock(smpl_no=lst[1],weight = Decimal(lst[2]),numbers=int(lst[3]),width=Decimal(lst[4]),
                              length=Decimal(lst[5]),status=lst[6],customer=lst[7], thickness=Decimal(lst[8]),
                              grade=lst[9],unit=lst[10], packet_name = lst [11])
            cs_lst.append(cs)
            cs_id_lst.append(lst[0])
        return zip(cs_id_lst,cs_lst)

    @classmethod
    def rm_list_for_hold(cls):
        user_data = []
        cs_lst = []
        cs_id_lst =[]
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from current_stock where status = 'RM' order by smpl_no asc")
            user_data = cursor.fetchall()
        for lst in user_data:
            cs = CurrentStock(smpl_no=lst[1],weight = Decimal(lst[2]),numbers=int(lst[3]),width=Decimal(lst[4]),
                              length=Decimal(lst[5]),status=lst[6],customer=lst[7], thickness=Decimal(lst[8]),
                              grade=lst[9],unit=lst[10], packet_name = lst [11])
            cs_lst.append(cs)
            cs_id_lst.append(lst[0])
        return zip(cs_id_lst,cs_lst)

    @classmethod
    def rm_list_for_unhold(cls):
        user_data = []
        cs_lst = []
        cs_id_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from current_stock where status = 'RM - On Hold'")
            user_data = cursor.fetchall()
        for lst in user_data:
            cs = CurrentStock(smpl_no=lst[1], weight=Decimal(lst[2]), numbers=int(lst[3]), width=Decimal(lst[4]),
                              length=Decimal(lst[5]), status=lst[6], customer=lst[7], thickness=Decimal(lst[8]),
                              grade=lst[9], unit=lst[10], packet_name = lst [11])
            cs_lst.append(cs)
            cs_id_lst.append(lst[0])
        return zip(cs_id_lst,cs_lst)

    @classmethod
    def transfer_material_cls(cls,cs_id, unit):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update current_stock set unit = %s where cs_id = %s",
                           (unit, cs_id))

    @classmethod
    def customer_list_for_dispatch(cls):
        customer_lst = []
        user_data = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select distinct customer from current_stock where status='FG' order by customer asc")
            user_data = cursor.fetchall()
        for lst in user_data:
            customer_lst.append(lst[0])
        return customer_lst


    @classmethod
    def get_stock_by_customer(cls, customer, display_type):
        user_data = []
        cs_lst = []
        cs_id_lst = []
        if display_type == 'FG':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer=%s and status = 'FG' order by smpl_no asc",(customer,))
                user_data = cursor.fetchall()
        if display_type == 'FGandRM':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer=%s and (status = 'FG' or status = 'RM') order by smpl_no asc", (customer,))
                user_data = cursor.fetchall()
        for lst in user_data:
            cs = CurrentStock(smpl_no=lst[1],weight = Decimal(lst[2]),numbers=int(lst[3]),width=Decimal(lst[4]),
                              length=Decimal(lst[5]),status=lst[6],customer=lst[7], thickness=Decimal(lst[8]),
                              grade=lst[9],unit=lst[10], packet_name = lst [11])
            cs_lst.append(cs)
            cs_id_lst.append(lst[0])

        return zip(cs_id_lst, cs_lst)


    def check_if_size_exists(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from current_stock where smpl_no = %s and thickness = %s and width = %s "
                           "and length = %s and status = %s and unit = %s and customer = %s",
                           (self.smpl_no, self.thickness, self.width, self.length, self.status, self.unit,
                            self.customer))
            user_data = cursor.fetchone()

            if user_data:
                '''cs = CurrentStock(smpl_no=user_data[1], weight=Decimal(user_data[2]), numbers=int(user_data[3]),
                                  width=Decimal(user_data[4]), length=Decimal(user_data[5]), status=user_data[6],
                                  customer=user_data[7], thickness=Decimal(user_data[8]), grade=user_data[9],
                                  unit=user_data[10], packet_name = user_data[11])'''

                return True
            else:
                return False

    @classmethod
    def csid_exists(cls, cs_rm_id):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from current_stock where cs_id = %s",
                           (cs_rm_id,))
            user_data = cursor.fetchone()

            if user_data:
                cs = CurrentStock(smpl_no=user_data[1], weight=Decimal(user_data[2]), numbers=int(user_data[3]),
                                  width=Decimal(user_data[4]), length=Decimal(user_data[5]), status=user_data[6],
                                  customer=user_data[7], thickness=Decimal(user_data[8]), grade=user_data[9],
                                  unit=user_data[10], packet_name = user_data[11])

                return cs
            else:
                return None