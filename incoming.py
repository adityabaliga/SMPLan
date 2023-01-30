from xml.dom.minidom import parse
import xml.dom.minidom
import os
from database import CursorFromConnectionFromPool
import datetime
from decimal import *


class Incoming:
    def __init__(self, smpl_no, customer, incoming_date, thickness, width, length, grade, weight, numbers, mill,
                 mill_id, remarks, unit):
        # incoming_string=incoming_str.split(',')
        self.smpl_no = smpl_no
        self.customer = customer
        self.incoming_date = incoming_date
        self.thickness = thickness
        self.width = width
        self.length = length
        self.grade = grade
        self.weight = weight
        self.numbers = numbers
        self.mill = mill
        self.mill_id = mill_id
        self.remarks = remarks
        self.unit = unit

    @classmethod
    def fromfile(cls, filename):
        # Adding the path to the filename to open PDF file
        # From http://stackoverflow.com/questions/36476659/how-to-add-a-relative-path-in-python-to-find-image-and-other-
        # file-with-a-short-p
        # script_dir = os.path.dirname("D:/MRV/")  # <-- absolute dir the script is in
        # rel_path = filename + '.xml'
        abs_file_path = filename

        # Extracting the xml tree in to collection
        DOMTree = xml.dom.minidom.parse(abs_file_path)
        collection = DOMTree.documentElement

        # Extract incoming date and convert it into a compatible date type
        incoming_date_coll = collection.getElementsByTagName("DATE")
        incoming_date = datetime.datetime.strptime(incoming_date_coll[0].childNodes[0].data, '%Y%m%d').date()

        # The function will return a list because the xml could have more than one RMs
        incoming_lst = []

        # Customer name is extracted
        customer = collection.getElementsByTagName("PARTYNAME")

        # This entire set is for each entry of a SMPL. Each SMPL's details have to be extracted from this
        raw_material = collection.getElementsByTagName("ALLINVENTORYENTRIES.LIST")

        for rm in raw_material:

            # SMPL No. extracted
            smpl_no = rm.getElementsByTagName("BATCHNAME")[0]

            # The dimensions of the coil are extracted and then split and then stored separately as thk, width & length
            stock_item = rm.getElementsByTagName("STOCKITEMNAME")[0]
            coil_dim = stock_item.firstChild.data

            # In tally, sometimes RM is added when incoming is sheets or slit coils. This is to remove that
            coil_dim = coil_dim.replace('RM','')
            coil_dim = coil_dim.upper()
            coil_dimension = coil_dim.split('X')

            # Coil Dimension has to be split in to length, width and thickness
            # If the split array has third element, it is assumed as the length --> it is a sheet
            # For a coil, the length is stored as 0
            length = 0.0
            if len(coil_dimension) > 2:
                tmp_length = coil_dimension[2].split(' ')
                if tmp_length[1].isdigit():
                    length = Decimal(tmp_length[1])
            width = Decimal(coil_dimension[1])
            thickness = Decimal(coil_dimension[0])

            # Weight is extracted
            weight_coll = rm.getElementsByTagName("ACTUALQTY")[0]
            weight_list = weight_coll.firstChild.data.split(' ')
            weight = Decimal(weight_list[1])

            # Grade is extracted
            # Changed of Material Receipt Voucher changed in Tally
            # grade = rm.getElementsByTagName("BASICUSERDESCRIPTION")
            mat_type = rm.getElementsByTagName("UDF:RNMTRLTYPEBATCH")
            mat_grade = rm.getElementsByTagName("UDF:RNGRADEBATCH")
            mat_coating = rm.getElementsByTagName("UDF:RNCOATBATCH")
            mat_scams_no = rm.getElementsByTagName("UDF:RNCUSTIDBATCH")
            grade = rm.getElementsByTagName("UDF:RNGRADEBATCH")

            # Numbers of RM is extracted. In the xml, the numbers are suffixed with MT. This is split and numbers kept
            numbers_coll = rm.getElementsByTagName("UDF:SBATCHNOOFPCS")
            if numbers_coll.length <1:
                numbers_coll = rm.getElementsByTagName("UDF:_UDF_721427290")
            if(numbers_coll.length >=1):
                numbers_list = numbers_coll[0].firstChild.data.split(' ')
                numbers = Decimal(numbers_list[1])
            else:
                numbers =0

            # Mill and Mill ID are extracted
            mill_id = rm.getElementsByTagName("UDF:RNMFDID")

            mill = rm.getElementsByTagName("UDF:RNMFR")

            unit = ''
            if smpl_no.childNodes[0].data.startswith('2SMPL') or smpl_no.childNodes[0].data.startswith('TTS') or smpl_no.childNodes[0].data.startswith('TSL'):
                unit = '2'
            if smpl_no.childNodes[0].data.startswith('SMPL'):
                unit = '1'

            # incoming_coil = smpl_no.childNodes[0].data + "," + customer[0].childNodes[0].data+ "," + incoming_date + "," + thickness+ "," + width+ "," + length+ "," + grade[0].firstChild.data+ "," + weight+ "," + numbers+ "," +mill[0].firstChild.data+ "," + mill_id[0].firstChild.data+ "," + " "

            # Incoming object created and appended to the list that is to be returned
            # Remove all spaces from the SMPL in tally, this will keep searching simple
            _smpl_no = smpl_no.childNodes[0].data.replace(" ","")
            _customer = customer[0].childNodes[0]._data



            # In Tally, Material receipt was implemented by splitting these fields. Earlier they were all
            # together as part of the userdescription field
            # I am building the string so we can split it in javascript and build the fields for sticker
            _grade = "MAT TYPE: "
            if mat_type:
                _grade += mat_type[0].firstChild._data
            _grade += "; GRADE: "
            if mat_grade:
                _grade += mat_grade[0].firstChild._data
            _grade += "; COATING: "
            if mat_coating:
                _grade += mat_coating[0].firstChild._data
            _grade += "; "
            if mat_scams_no:
                _grade += "SCAMS No: " + mat_scams_no[0].firstChild._data
            _grade += ";"

            # Additional comments have been added in this node in Tally such as for ID and IS grade
            # All this is being extracted and added to the grade column
            #if grade:
            #   for gr in grade:
            #        _grade += gr.firstChild._data + ". "
            #else:
            #    _grade = ''
            if mill:
                _mill = mill[0].firstChild._data
            else:
                _mill = ''
            if mill_id:
                _mill_id = mill_id[0].firstChild._data
            else:
                _mill_id = ''
            incoming_coil = Incoming(_smpl_no, _customer, incoming_date, thickness, width, length, _grade, weight, numbers,
                                     _mill, _mill_id, '', unit)

            # print (incoming_coil.smpl_no + " " + incoming_coil.incoming_date.strftime('%d%m%Y'))
            incoming_lst.append(incoming_coil)

        return incoming_lst

    def savetodb(self):
        with CursorFromConnectionFromPool() as cursor:
            # with psycopg2.connect(user='postgres', password='smpl@526', database='SMPL', host='localhost') as connection:
            #    with connection.cursor() as cursor:
            cursor.execute('insert into Incoming (SMPL_No, Customer, Incoming_Date, Thickness, Width, '
                           'Length, Grade, Weight, Numbers, Mill, Mill_ID, Remarks, Unit) values(%s,%s,%s,%s,%s,%s,%s,%s,'
                           '%s,%s,%s,%s, %s)', (self.smpl_no, self.customer, self.incoming_date, self.thickness, self.width,
                                            self.length, self.grade, self.weight, self.numbers, self.mill, self.mill_id,
                                            self.remarks, self.unit))

    @classmethod
    def load_smpl_by_smpl_no(cls, smpl_no):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('select * from incoming where smpl_no = %s', (smpl_no,))
            user_data = cursor.fetchone()
            if user_data:
                return cls(smpl_no=user_data[1], customer=user_data[2], incoming_date=change_date_format(user_data[3]), thickness=user_data[4],
                           width=user_data[5], length=user_data[6], grade=user_data[7], weight=user_data[8],
                           numbers=user_data[9],
                           mill=user_data[10], mill_id=user_data[11], remarks=user_data[12], unit = user_data[13])
            else:
                return False

    @classmethod
    def update_remarks_by_smpl_no(cls, remarks, smpl_no):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute('update incoming set Remarks = %s where smpl_no = %s', (remarks, smpl_no))



    @classmethod
    def update_remarks(cls,remarks,smpl_no):
        remarks = " " + remarks
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("update incoming set remarks = remarks || %s where smpl_no = %s",
                           (remarks, smpl_no))


    @classmethod
    def smpl_no_list_for_history(cls,smpl_no):
        query_smpl_no = '%' + smpl_no + '%'
        smpl_no_lst = []
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select smpl_no from incoming where smpl_no like %s order by smpl_no asc",(query_smpl_no,))
            user_data = cursor.fetchone()
        if user_data:
            for smpl_no in user_data:
                smpl_no_lst.append(smpl_no)

        return smpl_no_lst

    @classmethod
    def get_scams_no(cls, scams_no):
        query_scams_no = '%' + scams_no + '%'
        smpl_no_lst = []
        smpl_no = ''
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select smpl_no from incoming where grade like %s order by smpl_no asc", (query_scams_no,))
            user_data = cursor.fetchone()
        for smpl_no in user_data:
            smpl_no_lst.append(smpl_no)
        return smpl_no_lst

    @classmethod
    def get_daily_report(cls, report_date):
        with CursorFromConnectionFromPool() as cursor:
            cursor.execute("select customer, sum(weight), unit from incoming where incoming_date = %s group by "
                           "customer, unit",(report_date,))
            user_data=cursor.fetchall()

        return user_data

def change_date_format(date):
    # split_date = date.split('-')
    # new_date = split_date[2] + '-' + split_date[1] + '-' + split_date[0]
    new_date = date.strftime('%d/%m/%Y')
    return new_date