from werkzeug.utils import secure_filename
import os


class FileUploader:
    upload_path = "../projects/static/files/"
    allowed_extensions = set(['pdf', 'png', 'jpg', 'jpeg', 'gif'])

    # This method retrieves all the filenames from the directory for the SMPL number. For the file type in question,
    # it gets the last file added to it, adds one to it and returns it. This number is appended to the filename of the new
    # file
    @classmethod
    def file_list_check(cls, path, file_type):
        # Get all file names from directory
        if not os.path.exists(path):
            os.makedirs(path)
            return "1"
        else:
            file_list = os.listdir(path)

        file_type_list=[]
        if file_list:
            for filename in file_list:
                if file_type in filename:
                    file_type_list.append(filename)

        if len(file_type_list) > 0:
            max_file_name = max(file_type_list)
            max_file_name_no_ext = max_file_name.split('.')
            max_file_name_split = max_file_name_no_ext[0].split('_')
            number_position = len(max_file_name_split)
            max_file_number = int(max_file_name_split[number_position -1]) + 1

            return str(max_file_number)

        else:
            return "1"



    # This function is to upload the files related to the SMPL entered
    # file_type can be cust_order, smpl_order, prod_rprt
    # The files are stored in the directory named after the SMPL. The directory is created if doesn't exist
    # The file name will be the smpl_no_file_type_number.
    # For the number, all the filenames are extracted from the directory for the file type. Add one to the highest one
    # and then saved
    # If entension of any file is incorrect, then added to return_file_list and returned for message saying these files
    # couldn't be saved
    # reference : http://flask.pocoo.org/docs/0.12/patterns/fileuploads/ for file upload
    # make directory: https://stackoverflow.com/questions/273192/how-can-i-create-a-directory-if-it-does-not-exist
    # upload multiple files: https://stackoverflow.com/questions/11817182/uploading-multiple-files-with-flask
    @classmethod
    def upload_files(cls, smpl_no, file_type, files):

        return_file_list = ""
        for f in files:
            filename = secure_filename(f.filename)
            file_extension = filename.rsplit('.', 1)[1].lower()

            if file_extension in FileUploader.allowed_extensions:
                path = FileUploader.upload_path + smpl_no
                #file_list_check = path + "/" + file_type + "*.*"
                max_file_number = str(FileUploader.file_list_check(path, file_type))

                filename = smpl_no + "_" + file_type + "_" + str(max_file_number) + '.' + file_extension

                f.save(os.path.join(path, filename))

            else:
                return_file_list +=  "," + filename

        return return_file_list

    @classmethod
    def get_files_for_smpl_no(cls,smpl_no):
        file_list = []
        path = FileUploader.upload_path + smpl_no #+ '/*.*'
        if os.path.isdir(path):
            file_list = os.listdir(path)
        #file_list = glob.glob(path)
        if file_list:
            return file_list
        else:
            return ['No files found']