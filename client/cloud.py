import requests
import os
from zipfile import ZipFile
from random import randint
import sys
from tqdm import tqdm

test_base = 'http://localhost'
default_base = 'http://xdmoan.org'

def paths(directory): 
	file_paths = [] 
	for root, directories, files in os.walk(directory): 
		for filename in files: 
			filepath = os.path.join(root, filename) 
			file_paths.append(filepath) 
	return file_paths         
  
def zip_(directory, output): 
	file_paths = paths(directory)
	for file_name in tqdm(file_paths): 
		with ZipFile(output,'w') as zip: 
			for file in file_paths: 
				zip.write(file) 

def extract(directory, output):
	with ZipFile(directory, 'r') as handle:
		handle.extractall(output)

packet = lambda: 'packet' + str(randint(0, 1000)) + '.zip'


def post_file(location, filename, base, password=None):
	print(f'Uploading {filename}...')
	try:
		with open(filename, 'rb') as handle:
			status = requests.post(f'{base}/upload?d={location}', files={filename: handle})
			if status.text == 'success': print(f'Uploaded {filename} to {base}/{location}')
			else: print(f'{filename} already exists {base}/{location}')
	except Exception as E:
		output = packet()
		print(f'Zipping {filename} to {output}')
		zip_(filename, output)
		with open(output, 'rb') as handle:
			if password is None:
				status = requests.post(f'{base}/upload?d={location}', files={output: handle})
			else:
				status = requests.post(f'{base}/upload?d={location}&p={password[1::]}', files={output: handle})
			if status.text == 'success': print(f'Uploaded {filename} to {base}/{location}')
			else: print(f'{filename} already exists at {base}/{location}')
		os.system(f'rm {output}')

def create_file(location, base):
	print(f'Creating {location} on {base}')
	status = requests.get(f'{base}/create?d={location}')
	if status.text =='success': print(f'{location} Created')
	else: print(f'{location} already exists')

def delete_file(location, base):
	print(f'Deleting {location} from {base}')
	requests.get(f'{base}/delete?d={location}')
	print(f'{location} deleted')

def get_file(location, base):
	print(f'Requesting {location} from {base}')
	req = requests.get(f'{base}/download?d={location}')
	filename = [stage for stage in location.split('/') if stage != ''][-1]
	if len(filename.split('.')) == 1:
		handle_name = filename + '.zip'
		with open(handle_name, 'wb') as handle:
			handle.write(req.content)
		print(f'Retrieved {handle_name} from {base}')
		print(f'Extracting {handle_name} to {filename}')
		extract(handle_name, filename)
		print(f'{filename} Successfully Saved')
		os.system(f'rm {handle_name}')
	else:
		with open(filename, 'wb') as handle:
			handle.write(req.content)
		print(f'{filename} Successfully Saved')


test_mode = True

if __name__ == '__main__':
	type_ = sys.argv[1]
	location = sys.argv[2]
	if test_mode: base = test_base
	else: base = default_base
	if type_.lower() == '-u' or type_.lower() == '-upload':
		file = sys.argv[3]
		password = None
		if len(sys.argv) > 4:
			password = sys.argv[4]
		post_file(location, file, base, password=password)
	elif type_.lower() == '-d' or type_.lower() == '-download':
		get_file(location, base)
	elif type_.lower() == '-r' or type_.lower() == '-remove':
		delete_file(location, base)
	elif type_.lower() == '-c' or type_.lower() == '-create':
		create_file(location, base)
	else:
		print(f'Unknown Commaand: {type_}')


