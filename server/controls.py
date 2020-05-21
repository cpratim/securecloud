import json
import os
from zipfile import ZipFile 


def read_data(f):
	with open(f, 'r') as df:
		return json.loads(df.read())

def dump_data(f, d):
	with open(f, 'w') as df:
		json.dump(d, df, indent=4)

def create_folder(location, name):
	if name in os.listdir(location): return False
	os.mkdir(f'{location}/{name}')
	return True

def get_files(location, data):
	files = data
	for stage in location:
		if len(stage) > 0: files = files[stage]
	return files
  
def paths(directory): 
	file_paths = []
	path = directory.split('/')
	for root, directories, files in os.walk(directory): 
		root = '/'.join((root.split('/')[len(path):]))
		for filename in files: 
			filepath = os.path.join(root, filename) 
			file_paths.append(filepath) 
	return file_paths         
  
def zip_(directory, output): 
	file_paths = paths(directory)
	owd = os.getcwd()
	os.chdir(directory)
	for file_name in file_paths: 
		with ZipFile(output,'w') as zip: 
			for file in file_paths: 
				zip.write(file) 
	os.chdir(owd)
	os.rename(f'{directory}/{output}', f'packets/{output}')


def extract(directory, output):
	with ZipFile(directory, 'r') as handle:
		handle.extractall(output)