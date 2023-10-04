from database import CursorFromConnectionFromPool
from decimal import *
from order_detail import OrderDetail


class CurrentStock:
    def __init__(self, smpl_no, customer, weight, numbers, thickness, width, length, status, grade, unit, packet_name, length2):
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
        self.length2 = length2

    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("insert into current_stock (smpl_no,weight,numbers,width,length,status,customer,thickness"
                           ",grade, unit, packet_name, length2) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                           (self.smpl_no, self.weight, self.numbers, self.width, self.length, self.status, self.customer,
                           self.thickness, self.grade, self.unit, self.packet_name, self.length2))

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
                                      grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12])
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
                                  grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12])
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

        if operation == "Narrow_CTL" or operation == "Trap_NCTL":
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
                                   "length = 0 and smpl_no like %s and width <=600 order by "
                                   "smpl_no asc", (smpl_no_like,))
                else:
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP')"
                                   " and "
                                   "length = 0 and unit = %s  and smpl_no like %s and width <=600 order by "
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
                                  grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12])
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
                if customer_type == "tts":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0  and unit = %s and smpl_no like 'TTS%%' order by smpl_no asc", (str(unit),))
                if customer_type == "tr":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and unit = %s  and (smpl_no like 'TR%%' or smpl_no like '2TR%%') order by smpl_no asc", (str(unit),))

                user_data = cursor.fetchall()

        if operation == "Narrow_CTL" or operation == "Trap_NCTL":
            with CursorFromConnectionFromPool() as cursor:
                if customer_type == "smpl":
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP')"
                                   " and "
                                   "length = 0 and unit = %s  and customer not like 'TSDPL' and width <=800 order by "
                                   "smpl_no asc", (str(unit),))
                if customer_type == "tr":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and unit = %s  and (smpl_no like 'TR%%' or smpl_no like '2TR%%') and width <=800 order by smpl_no asc"
                        , (str(unit),))
                if customer_type == "tts":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and unit = %s  and smpl_no like 'TTS%%' and width <=800 order by smpl_no asc"
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
                        "length = 0 and unit = %s  and (smpl_no like 'TR%%' or smpl_no like '2TR%%') and width <=600 order by smpl_no asc"
                        , (str(unit),))
                if customer_type == "tts":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and unit = %s  and smpl_no like 'TTS%%' and width <=600 order by smpl_no asc"
                        , (str(unit),))
                user_data = cursor.fetchall()

        if operation == "Reshearing" or operation =="Lamination" or operation == "Levelling" or operation == "Trap_Reshearing":
            with CursorFromConnectionFromPool() as cursor:
                if customer_type == "smpl":
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                               "length > 0  and unit = %s and customer not like 'TSDPL' order by smpl_no asc", (str(unit),))
                if customer_type == "tr":
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                               "length > 0  and unit = %s and (smpl_no like 'TR%%' or smpl_no like '2TR%%') order by smpl_no asc", (str(unit),))
                if customer_type == "tts":
                    cursor.execute("select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                               "length > 0  and unit = %s and smpl_no like 'TTS%%' order by smpl_no asc", (str(unit),))
                user_data = cursor.fetchall()

        if user_data:
            for lst in user_data:
                cs = CurrentStock(smpl_no=lst[1], weight=Decimal(lst[2]), numbers=int(lst[3]), width=Decimal(lst[4]),
                                  length=Decimal(lst[5]), status=lst[6], customer=lst[7], thickness=Decimal(lst[8]),
                                  grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12])
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
                                      grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12])
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
                                      grade=lst[9], unit=lst[10], packet_name=lst[11], length2 = lst[12])
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
                                      grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12])
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
                                  unit=user_data[10], packet_name = user_data[11], length2 = user_data[12])

                return cs
            else:
                return None

    @classmethod
    def change_wt(cls, smpl_no, width, length, processed_wt, actual_no_of_pieces, sign, status, length2, packet_name = ""):
        with CursorFromConnectionFromPool() as cursor:
            if packet_name == "":
                cursor.execute("select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                               "and length = %s and status = %s and length2 = %s",
                               (smpl_no, width, length, status, length2))
                user_data = cursor.fetchone()
            else:
                cursor.execute(
                    "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                    "and length = %s and status = %s and packet_name = %s and length2 = %s",
                    (smpl_no, width, length, status, packet_name, length2))
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

                if (new_weight < 0.5 and sign == "minus" and Decimal(length) == 0) or ((new_weight < 0.2) and sign == "minus" and Decimal(length) > 0):
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
                cursor.execute("select * from current_stock where unit = %s order by smpl_no asc",(unit,))
                user_data = cursor.fetchall()
        else:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where status = %s and unit = %s order by smpl_no asc",(stock_type,unit))
                user_data = cursor.fetchall()

        for lst in user_data:
            cs = CurrentStock(smpl_no=lst[1],weight = Decimal(lst[2]),numbers=int(lst[3]),width=Decimal(lst[4]),
                              length=Decimal(lst[5]),status=lst[6],customer=lst[7], thickness=Decimal(lst[8]),
                              grade=lst[9],unit=lst[10], packet_name = lst [11], length2 = lst[12])
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
                              grade=lst[9],unit=lst[10], packet_name = lst [11], length2 = lst[12])
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
                              grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12])
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
                cursor.execute("select * from current_stock where customer=%s and status = 'FG' order by smpl_no, packet_name asc",(customer,))
                user_data = cursor.fetchall()
        if display_type == 'FGandRM':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer=%s and (status = 'FG' or status = 'RM') order by status, smpl_no, packet_name  asc", (customer,))
                user_data = cursor.fetchall()
        if display_type == 'FGandWIP':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer=%s and (status = 'FG' or status = 'WIP') order by  status, smpl_no, packet_name asc", (customer,))
                user_data = cursor.fetchall()
        if display_type == 'All':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer=%s order by status, smpl_no, packet_name asc", (customer,))
                user_data = cursor.fetchall()
        for lst in user_data:
            cs = CurrentStock(smpl_no=lst[1],weight = Decimal(lst[2]),numbers=int(lst[3]),width=Decimal(lst[4]),
                              length=Decimal(lst[5]),status=lst[6],customer=lst[7], thickness=Decimal(lst[8]),
                              grade=lst[9],unit=lst[10], packet_name = lst [11], length2 = lst[12])
            cs_lst.append(cs)
            cs_id_lst.append(lst[0])

        return zip(cs_id_lst, cs_lst)


    def check_if_size_exists(self):
        with CursorFromConnectionFromPool() as cursor:
            if self.status == 'FG':
                cursor.execute("select * from current_stock where smpl_no = %s and thickness = %s and width = %s "
                               "and length = %s and status = %s and unit = %s and customer = %s and packet_name = %s",
                               (self.smpl_no, self.thickness, self.width, self.length, self.status, self.unit,
                                self.customer, self.packet_name))
            else:
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
    def get_cs_for_qr_dispath(cls, smpl_no, packet_name, width, length, status, customer, length2, unit):
        cs_lst = []
        cs_id_lst = []
        with CursorFromConnectionFromPool() as cursor:
            if unit == '2':
                cursor.execute(
                    "select * from current_stock where smpl_no = %s and width = %s "
                    "and length = %s and status = %s and packet_name = %s and customer = %s and length2= %s",
                    (smpl_no, width, length, status, packet_name, customer, length2))
                user_data = cursor.fetchone()
            else:
                cursor.execute("select * from current_stock where smpl_no = %s and width = %s "
                               "and length = %s and status = %s and customer = %s",
                               (smpl_no, width, length, status, customer))
                user_data = cursor.fetchone()
            if user_data:

                cs = CurrentStock(smpl_no=user_data[1], weight=Decimal(user_data[2]), numbers=int(user_data[3]),
                                  width=Decimal(user_data[4]), length=Decimal(user_data[5]),
                                  status=user_data[6], customer=user_data[7],
                                  thickness=Decimal(user_data[8]), grade=user_data[9],
                                  unit=user_data[10], packet_name=user_data[11], length2 = user_data[12])
                cs_lst.append(cs)
                cs_id_lst.append(user_data[0])
                return zip(cs_id_lst, cs_lst)
            else:
                return None


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
                                  unit=user_data[10], packet_name = user_data[11], length2 = user_data[12])

                return cs
            else:
                return None

    @classmethod
    def monthly_report_dtl(cls, month, year):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select processing_date, operation, sum(total_processed_wt) as total_wt, sum(total_cuts) "
                "as total_cuts, sum(production_time + setting_time) as total_time from processing p "
                "where extract(month from processing_date) = %s and extract(year from processing_date) = %s"
                "group by processing_date, operation order by processing_date desc, operation asc", (month, year))
            user_data = cursor.fetchall()
            if user_data:
                return user_data
            else:
                return None

    @classmethod
    def monthly_report_hdr(cls, month, year):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select operation, sum(total_processed_wt) as total_wt, sum(total_cuts) "
                           "as total_cuts, sum(production_time + setting_time) as total_time from processing p "
                           "where extract(month from processing_date) = %s and extract(year from processing_date) = %s"
                           "group by operation order by operation asc",
                           (month, year))
            user_data = cursor.fetchall()
            if user_data:
                return user_data
            else:
                return None

    @classmethod
    def getHondaFGStock(cls):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select width, length, customer, sum(numbers) as numbers, round(sum(numbers)/300,2) as "
                           "packets from current_stock cs where (customer like 'TT STEEL%' or customer like 'HONDA%') "
                           "and ((width = 530 and length =765) or (width = 575 and length =640) or "
                           "(width = 600 and length =820) or (width = 720 and length =745) or "
                           "(width = 370 and length =415) or (width = 430 and length =455) or "
                           "(width = 510 and length =785) or (width = 600 and length =660) or "
                           "(width = 550 and length =790) or (width = 590 and length =705) or "
                           "(width = 515 and length =715) or (width = 620 and length =675) or "
                           "(width = 520 and length =765) or (width = 565 and length =645) or "
                           "(width = 570 and length =830) or (width = 600 and length =715) or "
                           "(width = 565 and length = 645) or (width = 655 and length = 740)) "
                           "group by width, length, customer order by width, customer")
            user_data = cursor.fetchall()
        if user_data:
            return user_data
        else:
            return None


    @classmethod
    def getHondaWIPStock(cls):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select cs.width, sum(cs.weight) as tot_wt, sum(cs.numbers) as tot_nos, "
                           "cs.customer from current_stock cs where cs.length = 0 and cs.status ='WIP' "
                           "and (cs.customer like 'TT STEEL%' or cs.customer like 'HONDA%') and ((cs.width = 530) or "
                           "(cs.width = 575) or (cs.width = 600) or (cs.width = 720) or (cs.width = 510) or "
                           "(cs.width = 600) or (cs.width = 550) or (cs.width = 590) or (cs.width = 570) or "
                           "(cs.width = 515) or (cs.width = 620) or (cs.width = 520) or "
                           "(cs.width = 565) or (cs.width = 600) or (cs.width = 370) or "
                           "(cs.width = 430) or (cs.width = 565) or (cs.width = 655)) group by cs.width, cs.customer "
                           "order by cs.width, cs.customer")
            user_data = cursor.fetchall()
        if user_data:
            return user_data
        else:
            return None


