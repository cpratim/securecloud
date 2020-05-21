from flask import Flask, send_file, jsonify, request, render_template, redirect, session, url_for
from controls import read_data, dump_data, get_files, zip_, extract
import os
import os.path
from config import SECRET, ADMIN
from random import randint

app = Flask(__name__)
datafile = 'data.json'
app.config['SECRET_KEY'] = SECRET
ignored = ['files', '.password', '.protected']

###################################################################################
######################################HELPERS######################################
###################################################################################

def build_path(location):
    l = ['storage'] + location
    path = []
    for i in range(len(l)):
        sub_path = '/'
        for j in range(i + 1):
            sub_path += l[j] + '/'
        if i == len(l) - 1: path.append((l[i], sub_path, True))
        else: path.append((l[i], sub_path, False))
    return path

def handle_url(url):
    if url[-3:] == 'ico': return (None, None)
    s = url.split('/')[3:]
    type_ = s[0]
    location = s[1:]
    if location[-1] == '': location = location[:-1]
    return (type_, location)

def is_image(file):
    types = ['jpeg', 'png', 'jpg', 'raw']
    filename = file.split('/')[-1]
    filetype = filename.split('.')[-1]
    if filetype.lower() in types: return True
    return False


###################################################################################
######################################BACKEND######################################
###################################################################################

@app.route('/download')
def download():
    location = request.args['d']
    if len(location.split('/')[-1].split('.')) > 1:
        return send_file(location, as_attachment=True)
    output = [stage for stage in location.split('/')][-1] + '.zip'
    if output in os.listdir('packets'): os.system(f'rm packets/{output}')
    zip_(location, output)
    return send_file(f'packets/{output}', as_attachment=True)

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    data = read_data(datafile)
    destination = request.args['d']
    location = destination.split('/')[1::]
    key = [k for k in request.files][0]
    file = request.files[key]
    filename = file.filename
    if filename.split('.')[1] != 'zip':
        if os.path.exists(f'{destination}/{filename}'):
            return 'failed'
        if destination == 'storage':
            file.save(f'storage/{filename}')
            data['files'].append(filename)
        else:
            endpoint = data
            for stage in location:
                endpoint = endpoint[stage]
            endpoint['files'].append(filename)
            filepath = '/'.join(location) + '/' + filename
            file.save(f'storage/{filepath}')
        dump_data(datafile, data)
        return 'success'
    else:
        print(f'{destination}/{filename}')
        file.save(f'packets/{filename}')
        extract(f'packets/{filename}', 'packets')
        os.system(f'rm packets/{filename}')
        filename = [name for name in os.listdir('packets') if len(name.split('.')) == 1][0]
        if os.path.isdir(f'{destination}/{filename}'):
            os.system(f'rm -r packets/{filename}')
            return 'failed'
        directory = os.walk(f'packets/{filename}')
        dump = {}
        for l, folders, files in directory:
            endpoint = dump
            stages = l.split('/')
            target = stages[-1]
            for stage in stages[1:-1]:
                endpoint = endpoint[stage]
            endpoint[target] = {'files': files, '.protected': False, '.password': ''}
        if 'p' in request.args:
            password = request.args['p']
            dump[filename]['.protected'] = True
            dump[filename]['.password'] = password
        if destination == 'storage':
            data[filename] = dump[filename]
            os.rename(f'packets/{filename}', f'storage/{filename}')
        else:
            endpoint = data
            for stage in location:
                endpoint = endpoint[stage]
            endpoint[filename] = dump[filename]
            os.rename(f'packets/{filename}', f'{destination}/{filename}')
        dump_data(datafile, data)
        return 'success'

@app.route('/delete')
def delete():
    location = request.args['d']
    data = read_data(datafile)
    target = location.split('/')[-1]
    path = '/'.join(location.split('/')[0:-1])
    stages = location.split('/')[1:-1]
    endpoint = data
    for stage in stages:
        endpoint = endpoint[stage]
    if len(target.split('.')) == 1:
        del endpoint[target]
        os.system(f'rm -r {location}')
    else:
        endpoint['files'].remove(target)
        os.system(f'rm {location}')
    dump_data(datafile, data)
    return redirect(path)

@app.route('/create')
def create():
    location = request.args['d']
    data = read_data(datafile)
    stages = location.split('/')[1:]
    if os.path.isdir(location):
        return 'failed'
    endpoint = data
    path = ''
    for stage in stages:
        path += stage + '/'
        if not stage in [key for key in endpoint]:
            endpoint[stage] = {'files': []}
            os.mkdir(f'storage/{path}')
        endpoint = endpoint[stage]
    dump_data(datafile, data)
    return 'success'

@app.route('/json', methods=['GET', 'POST'])
def json():
    from forms import VerifyForm
    verify_form = VerifyForm()
    if verify_form.validate_on_submit():
        password = verify_form.password.data
        if password == ADMIN:
            session['verified'] = True
            return send_file('data.json')
        else:
            messages = ['Incorrect Password.']
            return render_template('verify.html', verify_form=verify_form, messages=messages, alert_type='danger')
    return render_template('verify.html', verify_form=verify_form)

###################################################################################
#####################################FRONTEND######################################
###################################################################################

@app.route('/')
def index():
    if 'verified' in session:
        if session['verified'] is True:
            if 'redirect' in session:
                r_ = session['redirect']
                session.pop('redirect')
                return redirect(r_) 
            return redirect(url_for('storage'))
    return redirect(url_for('verify'))


@app.route('/verify', methods=['GET', 'POST'])
def verify():
    from forms import VerifyForm
    if 'verified' in session: 
        if session['verified'] is True: return redirect(url_for('index'))
    verify_form = VerifyForm()
    if verify_form.validate_on_submit():
        password = verify_form.password.data
        if password == SECRET:
            session['verified'] = True
            return redirect(url_for('index'))
        else:
            messages = ['Incorrect Password.']
            return render_template('verify.html', verify_form=verify_form, messages=messages, alert_type='danger')
    return render_template('verify.html', verify_form=verify_form)

@app.route('/storage')
def storage():
    return redirect('/storage/')

@app.route('/storage/static/<string:folder>/<string:file>')
def stylesheet(folder, file):
    return send_file(f'static/{folder}/{file}')

@app.route('/image')
def image():
    location = request.args['d']
    if os.path.isfile(location):
        if is_image(location):
            return send_file(location)
    return send_file('static/misc/file.png')

@app.route('/view')
def view():
    location = request.args['d']
    if 'verified' not in session: 
        session['redirect'] = f'/view?d={location}'
        return redirect(url_for('index'))
    if session['verified'] is not True: 
        session['redirect'] = f'/view?d={location}'
        return redirect(url_for('index'))
    return send_file(location)

@app.route('/share')
def share():
    if 't' in request.args:
        test = request.args['t']
        print(test)
    return ''

@app.route('/logout')
def logout():
    session.pop('verified')
    return redirect(url_for('index'))


@app.errorhandler(404)
def storage(e):
    if 'verified' not in session: return redirect(url_for('index'))
    if session['verified'] is not True: return redirect(url_for('index'))
    url = request.url
    type_, location = handle_url(url)
    if request.method == 'POST':
        data = read_data(datafile)
        if len(request.form) == 0:
            file = request.files['file']
            filename = file.filename
            endpoint = data
            for stage in location:
                endpoint = endpoint[stage]
            endpoint['files'].append(filename)
            dump_data(datafile, data)
            filepath = '/'.join(location) + '/' + filename
            file.save(f'storage/{filepath}')
            return redirect(url)
        else:
            try:
                foldername = request.form['foldername']
                password = request.form['password']
                protected = False
                if len(password) > 0: protected = True 
                endpoint = data
                for stage in location:
                    endpoint = endpoint[stage]
                endpoint[foldername] = {'files': [], '.protected': protected, '.password': password}
                dump_data(datafile, data)
                filepath = '/'.join(location) + '/' + foldername
                os.mkdir(f'storage/{filepath}')
                return redirect(url)
            except Exception as e:
                pass
    if type_ is None: return ''
    if type_ == 'storage':
        data = read_data('data.json')
        if len(location) == 0:
            folders = [key for key in data if key not in ignored]
            files = data['files']
            path =  [('storage', '/storage/', True)]
            destination = 'storage/'
            return render_template('storage.html', files=files, folders=folders, path=path, destination=destination)
        try:
            if len(location[-1].split('.')) > 1:
                filepath = 'storage/' + '/'.join(location)
                if not os.path.isfile(filepath): return f'File {filepath} Does NOT Exist'
                return send_file(filepath)
            sub = get_files(location, data)
            path = build_path(location)
            folders = [key for key in sub if key not in ignored]
            files = sub['files']
            destination = 'storage/' + '/'.join(location) + '/'
            if sub['.protected'] is True:
                from forms import VerifyForm
                password = sub['.password']
                verify_form = VerifyForm()
                if verify_form.validate_on_submit():
                    attempt = verify_form.password.data
                    if password == attempt:
                        return render_template('storage.html', files=files, folders=folders, path=path, destination=destination)
                    else:
                        messages = ['Incorrect Password.']
                        return render_template('protected.html', verify_form=verify_form, messages=messages, alert_type='danger', destination=destination)
                return render_template('protected.html', verify_form=verify_form, destination=destination)
            return render_template('storage.html', files=files, folders=folders, path=path, destination=destination)
        except Exception as e:
            return 'Destination Does not Exist'
    return 'no'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80)