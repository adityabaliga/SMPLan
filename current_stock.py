from database import CursorFromConnectionFromPool
from decimal import *
from order_detail import OrderDetail
from psycopg2.extras import execute_values
from datetime import datetime
import uuid
import json
from flask import jsonify
from pathlib import Path
import io


class CurrentStock:
    def __init__(self, smpl_no, customer, weight, numbers, thickness, width, length, status, grade, unit, packet_name,
                 length2, date, processing_id, second_customer, net_wt, lami = ''):
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
        self.date = date
        self.processing_id = processing_id
        self.second_customer = second_customer
        self.net_wt = net_wt
        self.lami = lami


    def save_to_db(self):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("insert into current_stock (smpl_no,weight,numbers,width,length,status,customer,thickness"
                           ",grade, unit, packet_name, length2, date, processing_id, second_customer, net_wt, lami) "
                           "values (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                           (self.smpl_no, self.weight, self.numbers, self.width, self.length, self.status, self.customer,
                           self.thickness, self.grade, self.unit, self.packet_name, self.length2, self.date,
                            self.processing_id, self.second_customer, self.net_wt, self.lami))

    def update_status(self, status):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update current_stock set status = %s where smpl_no = %s and width = %s and length = %s and lami = %s",
                           (status, self.smpl_no, self.width, self.length, self.lami))

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
                                      grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12],
                                      date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt = lst[16])
                    cs_lst.append(cs)

                return cs_lst
            else:
                return None

    @classmethod
    def smpl_list_for_place_order(cls, string):
        user_data = []
        cs_lst = []
        cs_id_lst = []
        result_list = []
        if string == 'SMPL':
            query = ("select cs_id, smpl_no, thickness, width, length, status, incoming_weight, numbers, customer, grade, "
                     "available_weight, unit from available_coils_for_order "
                     "where customer not like 'TSDPL%' and status = 'RM' or status = 'HC' order by smpl_no asc")
        if string == 'TR':
            query = ("select cs_id, smpl_no, thickness, width, length, status, incoming_weight, numbers, customer, grade, "
                     "available_weight, unit from available_coils_for_order "
                     "where customer like 'TSDPL%'  and status = 'RM' or status = 'HC' order by smpl_no asc")
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(query)
            user_data = cursor.fetchall()

        if user_data:
            return user_data
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
                                  grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12],
                                  date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt= lst[16])
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
                                   "length = 0 and unit = %s  and customer not like 'TSDPL' and width <=1000 order by "
                                   "smpl_no asc", (str(unit),))
                if customer_type == "tr":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and unit = %s  and (smpl_no like 'TR%%' or smpl_no like '2TR%%') and width <=1000 order by smpl_no asc"
                        , (str(unit),))
                if customer_type == "tts":
                    cursor.execute(
                        "select * from current_stock where (status = 'RM' or status = 'HC' or status= 'WIP') and "
                        "length = 0 and unit = %s  and smpl_no like 'TTS%%' and width <=1000 order by smpl_no asc"
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
                                  grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12],
                                  date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt=lst[16])
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
                                      grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12],
                                      date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt= lst[16],
                                      lami= lst[20])
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
                                      grade=lst[9], unit=lst[10], packet_name=lst[11], length2 = lst[12],
                                      date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt=lst[16],
                                      lami = lst[20])
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
                                      grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12],
                                      date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt= lst[16],
                                      lami = lst[21])
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
                                  unit=user_data[10], packet_name = user_data[11], length2 = user_data[12],
                                  date = user_data[13], processing_id= user_data[14], second_customer= user_data[15],
                                  net_wt= user_data[16], lami = user_data[21])

                return cs
            else:
                return None

    @classmethod
    def change_wt(cls, smpl_no, width, length, processed_wt, actual_no_of_pieces, sign, status, length2, lami, packet_name = ""):
        with CursorFromConnectionFromPool() as cursor:
            if packet_name == "":
                cursor.execute("select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                               "and length = %s and status = %s and length2 = %s and lami = %s",
                               (smpl_no, width, length, status, length2, lami))
                user_data = cursor.fetchone()
            else:
                cursor.execute(
                    "select weight, numbers, unit, cs_id from current_stock where smpl_no = %s and width = %s "
                    "and length = %s and status = %s and packet_name = %s and length2 = %s and lami = %s",
                    (smpl_no, width, length, status, packet_name, length2, lami))
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
            if unit == 'All':
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select * from current_stock order by unit, smpl_no asc")
                    user_data = cursor.fetchall()
            else:
                with CursorFromConnectionFromPool() as cursor:
                    cursor.execute("select * from current_stock where unit = %s order by smpl_no asc", (unit,))
                    user_data = cursor.fetchall()
        else:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where status = %s and unit = %s order by smpl_no asc",(stock_type,unit))
                user_data = cursor.fetchall()

        for lst in user_data:
            cs = CurrentStock(smpl_no=lst[1],weight = Decimal(lst[2]),numbers=int(lst[3]),width=Decimal(lst[4]),
                              length=Decimal(lst[5]),status=lst[6],customer=lst[7], thickness=Decimal(lst[8]),
                              grade=lst[9],unit=lst[10], packet_name = lst [11], length2 = lst[12],
                              date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt= lst[16])
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
                              grade=lst[9],unit=lst[10], packet_name = lst [11], length2 = lst[12],
                              date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt= lst[16],
                              lami = lst[20])
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
                              grade=lst[9], unit=lst[10], packet_name = lst [11], length2 = lst[12],
                              date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt= lst[16],
                              lami = lst[20])
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
    def customer_list_for_stock(cls):
        customer_lst = []
        user_data = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select distinct customer, SUM(CASE WHEN status = 'RM' THEN weight ELSE 0 END) "
                           "AS RM_quantity, "
                           "SUM(CASE WHEN status = 'WIP' THEN weight ELSE 0 END) AS WIP_quantity,"
                           "SUM(CASE WHEN status = 'FG' THEN weight ELSE 0 END) AS FG_quantity "
                           "from current_stock "
                           "group by customer "
                           "order by customer asc ")
            user_data = cursor.fetchall()
        if user_data:
            return user_data
        else:
            return 0


    @classmethod
    def get_stock_by_customer(cls, customer, display_type):
        user_data = []
        cs_lst = []
        cs_id_lst = []
        if display_type == 'FG':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer like %s and status = 'FG' order by smpl_no, packet_name asc",(customer,))
                user_data = cursor.fetchall()
        if display_type == 'FGHonda':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer like %s and status = 'FG' order by smpl_no, packet_name asc",(customer,))
                user_data = cursor.fetchall()

        if display_type == 'FGandRM':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer like %s and (status = 'FG' or status = 'RM') order by status, smpl_no, packet_name  asc", (customer,))
                user_data = cursor.fetchall()
        if display_type == 'FGandWIP':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer like %s and (status = 'FG' or status = 'WIP') order by  status, smpl_no, packet_name asc", (customer,))
                user_data = cursor.fetchall()
        if display_type == 'All':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer like %s order by status, smpl_no, packet_name asc", (customer,))
                user_data = cursor.fetchall()
        if display_type == 'AllminusScrap':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer like %s and status != 'SCRAP' order by status, smpl_no, packet_name asc", (customer,))
                user_data = cursor.fetchall()
        if display_type == 'Scrap':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer like %s and status = 'SCRAP' order by status, smpl_no, packet_name asc", (customer,))
                user_data = cursor.fetchall()
        if display_type == 'RMFGForScrap':
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("select * from current_stock where customer like %s and (status = 'RM' or status = 'WIP') order by weight, smpl_no, status, smpl_no asc", (customer,))
                user_data = cursor.fetchall()
        for lst in user_data:
            cs = CurrentStock(smpl_no=lst[1],weight = Decimal(lst[2]),numbers=int(lst[3]),width=Decimal(lst[4]),
                              length=Decimal(lst[5]),status=lst[6],customer=lst[7], thickness=Decimal(lst[8]),
                              grade=lst[9],unit=lst[10], packet_name = lst [11], length2 = lst[12],
                              date = lst[13], processing_id= lst[14], second_customer= lst[15], net_wt= lst[16],
                              lami = lst[20])
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
    def get_cs_for_qr_dispath(cls, smpl_no, packet_name, width, length, status, customer, length2, unit, numbers):
        cs_lst = []
        cs_id_lst = []
        with CursorFromConnectionFromPool() as cursor:

            cursor.execute(
                "select * from current_stock where smpl_no = %s and width = %s "
                "and length = %s and status = %s and packet_name = %s and customer = %s and length2= %s and numbers= %s",
                (smpl_no, width, length, status, packet_name, customer, length2, numbers))
            user_data = cursor.fetchone()


            if user_data:

                cs = CurrentStock(smpl_no=user_data[1], weight=Decimal(user_data[2]), numbers=int(user_data[3]),
                                  width=Decimal(user_data[4]), length=Decimal(user_data[5]),
                                  status=user_data[6], customer=user_data[7],
                                  thickness=Decimal(user_data[8]), grade=user_data[9],
                                  unit=user_data[10], packet_name=user_data[11], length2 = user_data[12],
                                  date = user_data[13], processing_id= user_data[14], second_customer= user_data[15],
                                  net_wt= user_data[16], lami = user_data[20])
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
                                  unit=user_data[10], packet_name = user_data[11], length2 = user_data[12],
                                  date = user_data[13], processing_id= user_data[14], second_customer= user_data[15],
                                  net_wt= user_data[16], lami = user_data[20])

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
                           "where extract(month from processing_date) = %s and extract(year from processing_date) = %s "
                           "group by operation order by operation asc",
                           (month, year))
            user_data = cursor.fetchall()
            if user_data:
                return user_data
            else:
                return None

    @classmethod
    def customer_wise_month_data(cls, month, year):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select 	i.customer AS customer_group, "
                           "sum(p.total_processed_wt) as processed_wt FROM processing p "
                           "left JOIN incoming i ON i.smpl_no = p.smpl_no where "
                           "(extract(month from p.processing_date) = %s and extract (year from p.processing_date) = %s)"
                           "group by customer_group order by processed_wt desc",
                           (month, year))
            user_data = cursor.fetchall()
            if user_data:
                return user_data
            else:
                return None

    @classmethod
    def customer_wise_machine_wise_month_data(cls, month, year):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("SELECT i.customer, pd.operation, SUM(p.total_processed_wt) AS total_weight FROM processing p "
                           "JOIN incoming i ON p.smpl_no = i.smpl_no JOIN "
                           "( SELECT DISTINCT processing_id, operation FROM processing_detail ) "
                           "pd ON pd.processing_id = p.processing_id WHERE "
                           "extract(month from p.processing_date) = %s and extract (year from p.processing_date) = %s "
                           "GROUP BY i.customer, pd.operation ORDER BY i.customer,pd.operation",
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
                           "(width = 565 and length = 645) or (width = 655 and length = 740) or "
                           "(width = 720 and length = 860) or (width = 570 and length = 650) or "
                           "(width = 810 and length = 1010)) "
                           "group by width, length, customer order by customer, width")
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
                           "order by cs.customer, cs.width")
            user_data = cursor.fetchall()
        if user_data:
            return user_data
        else:
            return None

    @classmethod
    def getStickerList(cls, smpl_no):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(" select * from sticker where smpl_no = %s",(smpl_no,))

            user_data = cursor.fetchall()
        if user_data:
            return user_data
        else:
            return None


    @classmethod
    def add_weight(cls, cs_id, new_wt):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update current_stock set weight = %s where cs_id = %s",(new_wt, cs_id))


    @classmethod
    def get_sticker(cls, smpl_no, packet_name, thickness, width, length):
        if length == 0:
            length = ' Coil'
        size = str(thickness) + '0 X ' + str(width) + ' X ' + str(length)

        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select * from sticker where smpl_no = %s and packet_name = %s and size = %s"
                           " order by sticker_id",
                           (smpl_no, packet_name, size))
            user_data = cursor.fetchall()
        if user_data:
            return user_data[0]
        else:
            return None


    @classmethod
    def mark_for_scrap(cls, cs_id_lst):
        # This is to update status of stock to scrap
        try:
            with CursorFromConnectionFromPool() as cursor:
                cursor.execute("CREATE TEMP TABLE temp_ids (id INTEGER PRIMARY KEY) ON COMMIT DROP")

                execute_values(
                    cursor,
                    "INSERT INTO temp_ids (id) VALUES %s",
                    [(id,) for id in cs_id_lst],
                    page_size=1000
                )

                cursor.execute("update current_stock set status = 'SCRAP' from temp_ids where "
                               "current_stock.cs_id = temp_ids.id")
            return 'Status updated'



        except Exception as e:
            error_message = f"Unexpected error: {str(e)}"
            logging.error(error_message)
            return error_message


    @classmethod
    def get_cs_by_size(cls, smpl_no, width, length, length2, packet_name):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(
                "select * from current_stock where smpl_no = %s and width = %s "
                "and length = %s and packet_name = %s and length2 = %s",
                (smpl_no, width, length, packet_name, length2))
            user_data = cursor.fetchone()
        if user_data:
            cs = CurrentStock(smpl_no=user_data[1], weight=Decimal(user_data[2]), numbers=int(user_data[3]),
                              width=Decimal(user_data[4]), length=Decimal(user_data[5]), status=user_data[6],
                              customer=user_data[7], thickness=Decimal(user_data[8]), grade=user_data[9],
                              unit=user_data[10], packet_name=user_data[11], length2=user_data[12],
                              date=user_data[13], processing_id=user_data[14], second_customer=user_data[15],
                              net_wt=user_data[16], lami = user_data[20])

            return cs
        else:
            return None

    @classmethod
    def get_unexported_fg_by_size(cls, smpl_no=None):
        """
        Get all FG grouped by size that haven't been completely exported
        """
        query = """SELECT fg_size,  thickness, width, length, smpl_no, processing_id, packet_count, total_quantity, total_weight, packets, cs_ids, earliest_production_date, latest_production_date, unexported_packet_count FROM exportable_fg_view WHERE any_exported = FALSE """

        params = []
        if smpl_no:
            query += " AND smpl_no = %s"
            params.append(smpl_no)

        query += " ORDER BY smpl_no, fg_size"

        with CursorFromConnectionFromPool() as cursor:
            cursor.execute(query, params)
            columns = [desc[0] for desc in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results


    @classmethod
    def export_fg_to_tally(cls, smpl_no, fg_size_description, thickness, width, length, cs_ids_str):
        """
        Export a specific FG size group to Tally
        cs_ids_str: comma-separated packet IDs (e.g., "1,5,12,18")
        """

        cs_ids = []
        try:
            print(f"Step 1: Initialized cs_ids as empty list: {cs_ids}")

            # Convert to string just to be safe
            cs_ids_str = str(cs_ids_str).strip()
            print(f"Step 2: After str() and strip(): '{cs_ids_str}'")

            # Split by comma
            split_result = cs_ids_str.split(',')
            print(f"Step 3: After split by comma: {split_result}")
            print(f"Step 3: Number of parts: {len(split_result)}")

            # Process each part
            print(f"Step 4: Processing each part...")
            for i, part in enumerate(split_result):
                print(f"  Part {i}: '{part}' (type: {type(part)}, len: {len(part)})")
                stripped = part.strip()
                print(f"    After strip: '{stripped}' (type: {type(stripped)}, len: {len(stripped)})")

                if stripped and stripped != '':
                    try:
                        int_value = int(stripped)
                        print(f"    Converted to int: {int_value}")
                        cs_ids.append(int_value)
                    except ValueError as ve:
                        print(f"    ERROR converting to int: {ve}")
                else:
                    print(f"    Skipping empty part")

            print(f"Step 5: Final cs_ids list: {cs_ids}")
            print(f"Step 5: Length of cs_ids: {len(cs_ids)}")

            if not cs_ids:
                print("ERROR: cs_ids is still empty after processing!")
                return {'success': False, 'message': 'Could not parse CS IDs'}

            # Continue with rest of function...
            print(f"Step 6: CS IDs successfully parsed: {cs_ids}")
        except ValueError as e:
            return {
                'success': False,
                'message': f'Invalid CS IDs format: {str(e)}'
            }
            if not cs_ids:
                return {
                    'success': False,
                    'message': 'No packets selected'
                }

        try:
            with CursorFromConnectionFromPool() as cursor:

                # Fetch all packets for this group
                placeholders = ','.join(['%s'] * len(cs_ids))
                query = f"""
                SELECT cs_id, smpl_no, thickness, width, length, weight, numbers, packet_name, customer, grade, date FROM current_stock WHERE cs_id IN ({placeholders}) AND tally_exported = FALSE
                """

                cursor.execute(query, cs_ids)
                packets = cursor.fetchall()

                if not packets:
                    return {
                        'success': False,
                        'message': 'No unexported packets found'
                    }

                # Calculate totals
                total_weight = sum(p[5] for p in packets)
                total_quantity = sum(p[6] for p in packets)

                # Calculate totals
                total_weight = 0
                total_quantity = 0

                for packet in packets:
                    # packet = (cs_id, smpl_no, thickness, width, length, weight, numbers, packet_name, customer, grade, date)
                    total_weight += packet[5]  # weight
                    total_quantity += packet[6]  # numbers

                    # Generate batch ID and filename
                    batch_id = f"TALLY_{smpl_no}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"

                    # Format filename: smpl_no_fgsize_date.xml
                    # Clean fg_size for filename (remove spaces, special chars)
                    fg_size_clean = fg_size_description.replace(' ', '_').replace('x', 'x')
                    date_str = datetime.now().strftime('%d%m%Y')
                    xml_filename = f"{smpl_no}_{fg_size_clean}_{date_str}.xml"


                # Generate XML for Tally
                xml_content = cls.generate_tally_stock_journal_xml(
                    smpl_no=smpl_no,
                    fg_size=fg_size_description,
                    thickness=thickness,
                    width=width,
                    length=length,
                    total_quantity=total_quantity,
                    total_weight=total_weight,
                    packets=packets,
                    batch_id=batch_id
                )

                # Log the export
                log_query = """
                INSERT INTO tally_export_log 
                (export_batch_id, fg_size_description, total_quantity, total_weight, 
                 smpl_no, packet_count, xml_generated, xml_filename, xml_content, exported_by)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """

                cursor.execute(log_query, (
                    batch_id,
                    fg_size_description,
                    total_quantity,
                    total_weight,
                    smpl_no,
                    len(packets),
                    True,
                    xml_filename,
                    xml_content,
                    'system'  # or get from session
                ))

                # Update current_stock records
                for packet in packets:
                    cs_id = packet[0]
                    packet_name = packet[7]
                    weight = packet[5]
                    numbers = packet[6]

                    update_query = """
                                    UPDATE current_stock
                                    SET tally_exported = TRUE,
                                        tally_export_date = CURRENT_TIMESTAMP,
                                        tally_export_batch_id = %s
                                    WHERE cs_id = %s
                                    """
                    cursor.execute(update_query, (batch_id, cs_id))

                    # Log the mapping
                    mapping_query = """
                    INSERT INTO tally_export_packet_map 
                    (export_batch_id, cs_id, packet_name, weight, numbers)
                    VALUES (%s, %s, %s, %s, %s)
                    """
                    cursor.execute(mapping_query, (
                        batch_id,
                        cs_id,
                        packet[7],  # packet_name
                        packet[5],  # weight
                        packet[6]  # numbers
                    ))

                return {
                    'success': True,
                    'batch_id': batch_id,
                    'fg_size': fg_size_description,
                    'packet_count': len(packets),
                    'total_quantity': total_quantity,
                    'total_weight': total_weight,
                    'xml_generated': True,
                    'xml_filename': f"{batch_id}.xml",
                    'message': f'Export successful. {len(packets)} packets exported.'
                }

        except Exception as e:
           return {
                'success': False,
                'message': f'Error during export: {str(e)}'
            }


    @classmethod
    def generate_tally_stock_journal_xml(cls, smpl_no, fg_size, thickness, width, length,
                                         total_quantity, total_weight, packets, batch_id):
        """
        Generate Tally XML for Stock Journal entry
        """
        try:
            # Format FG size: if length is 0, replace with "Coils"
            if length == 0 or length == '0':
                fg_size_formatted = f"{thickness} x {width} x Coils"
            else:
                fg_size_formatted = fg_size

            # Add space after coil prefixes
            smpl_no_formatted = cls.format_coil_number(smpl_no)


            xml = f"""<?xml version="1.0" encoding="utf-8"?>
            <TALLY>
              <STOCKJOURNAL>
                <GUID>{uuid.uuid4().hex.upper()}</GUID>
                <DATE>{datetime.now().strftime('%Y-%m-%d')}</DATE>
                <REFERENCE>SJ-{batch_id}</REFERENCE>
                <NOTES>Auto-generated from Production System - FG: {fg_size}</NOTES>
                <LINEITEM>
                  <ITEM>{fg_size}</ITEM>
                  <QUANTITY>{total_quantity}</QUANTITY>
                  <BASEUNITS>{total_weight}</BASEUNITS>
                  <UNIT>MT</UNIT>
                  <COIL_NUMBER>{smpl_no_formatted}</COIL_NUMBER>
                  <THICKNESS>{thickness}</THICKNESS>
                  <WIDTH>{width}</WIDTH>
                  <LENGTH>{length}</LENGTH>
                  <PACKET_DETAILS>
            """

            # Add details of each packet
            print(f"Adding {len(packets)} packets to XML...")
            for i, packet in enumerate(packets):
                cs_id = packet[0]
                coil = packet[1]
                thick = packet[2]
                w = packet[3]
                l = packet[4]
                weight = packet[5]
                qty = packet[6]
                pkt_name = packet[7] if packet[7] else "Unknown"
                cust = packet[8] if packet[8] else "N/A"
                grade = packet[9] if packet[9] else "N/A"
                prod_date = packet[10] if packet[10] else datetime.now().date()


                xml += f"""        <PACKET>
                      <PACKET_ID>{cs_id}</PACKET_ID>
                      <PACKET_NAME>{pkt_name}</PACKET_NAME>
                      <COIL_NUMBER>{smpl_no_formatted}</COIL_NUMBER>
                      <QUANTITY>{qty}</QUANTITY>
                      <WEIGHT>{weight}</WEIGHT>
                      <CUSTOMER>{cust}</CUSTOMER>
                      <GRADE>{grade}</GRADE>
                      <PRODUCTION_DATE>{prod_date}</PRODUCTION_DATE>
                    </PACKET>
            """
                print(f"  Packet {i + 1}: {pkt_name} - {qty} qty, {weight} kg")

            xml += """      </PACKET_DETAILS>
                </LINEITEM>
              </STOCKJOURNAL>
            </TALLY>"""

            return xml

        except Exception as e:
            print(f"Error generating XML: {str(e)}")
            import traceback
            traceback.print_exc()
            return None


    @classmethod
    def format_coil_number(cls, coil_number):
        """
        Format coil number by adding space after prefix
        Examples: SMPL1111A -> SMPL 1111A, 2SMPL2222B -> 2SMPL 2222B, TR123 -> TR 123
        """
        coil_number = str(coil_number).strip()

        # Define prefixes to look for
        prefixes = ['SMPL', '2SMPL', '4SMPL', 'TR']

        for prefix in prefixes:
            if coil_number.upper().startswith(prefix):
                # Get the prefix part and the rest
                prefix_part = coil_number[:len(prefix)]
                rest_part = coil_number[len(prefix):]

                # Add space if there's something after the prefix
                if rest_part:
                    return f"{prefix_part} {rest_part}"

        # If no prefix matches, return as is
        return coil_number