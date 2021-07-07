from application import app
import os
from werkzeug.utils import secure_filename

def save_file(file,type):
    file_name = secure_filename(file.filename)
    file_ext = file_name.split('.')[1]
    folder = os.path.join(app.root_path, 'static/'+type+'/')
    file_path = os.path.join(folder, file_name)
    try:
        file.save(file_path)
        return True, file_name
    except:
        return False, file_name

def delete_image(file, type):
    try:
        os.remove(os.path.join(app.root_path, 'static/'+type+'/'+file))
        return True
    except:
        return False

