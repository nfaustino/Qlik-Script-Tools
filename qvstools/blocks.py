#Module for storing blocks.
import pickle
import xml.etree.ElementTree as ET
import sys, os, unicodedata, re

### Methods

def write_tab(name,intofile,mode='a'):
	"Adds a tab line to the file."
	"Standard function that doesnt need to be part of blocklibrary."
	with open(intofile,mode) as outputfile:
		outputfile.write('///$tab ' + name + '\n')
	return

### Classes

class Block:
	def __init__(self,b_name,b_description,b_type,b_text,b_replacelist=[]):
		self.name = b_name
		self.description = b_description
		self.type = b_type
		self.text = b_text
		self.replacelist = b_replacelist

	def write(self,intofile,replacelist=[],mode='a'):
		"""Appends a block to a file."""
		#Check that replacelist length is correct for block.
		if len(replacelist) != len(self.replacelist):
			raise NameError('Replacelist requires {0} items but supplied {1}.'.format(len(self.replacelist),len(replacelist)))
			return
		print('Writing block {0} to file.'.format(self.name))
		#Replace @1 notation in block with user specified text.
		blocktext = self.text
		for i  in range(0,len(replacelist)):
			blocktext = blocktext.replace('@' + str(i),replacelist[i]) #This doesnt seem to be working...
		#Write output to file.		
		with open(intofile,mode) as outputfile:
			outputfile.write(blocktext)
		return	
		
class BlockLibrary:
	"""This adds an easy way to bundle together the qvblocks scripts in a single file."""

	def __init__(self,name,load_defaults=False):
		self.name = name
		self.blocks = {}
		if load_defaults:
			for pfile in [f for f in os.listdir('Blocks') if f.startswith('Default_')]:
				self.add_pickled_block(os.path.join('Blocks',pfile))
		else:
			pass
		# Block groups is a  dict of groups of blocks. 
		# Each group is a list that should be written in order.
		# Each item in the list is a tuple (block,replacelist). block just points to a key in self.blocks. It isnt a block itself.
		

	def add_pickled_block(self,blockfile, rename = False):
		with open(blockfile,'rb') as pickled:
			block = pickle.load(pickled)
		if rename:
			block.name = rename
		self.blocks[block.name] = block

	def add_text_block(self,b_name,b_description,b_type,b_textfile):
		"""Adds a block from a text file given the rest of the inputs."""
		with open(b_textfile,'r') as textfile:
			b_text = textfile.read()
			b_replacelist = re.findall(r"//\((@[\d]),\s?\'([\w\s,.?!()$]*)\'\)",b_text) #Returns a list of tuples. 
			#Scrub replacelist lines from text file.
			b_text = '\n'.join([line for line in b_text.split('\n') if not re.search(r"//\(@[\d]",line) ])
			
			self.blocks[b_name] = Block(b_name,b_description,b_type,b_text,b_replacelist)	

	def remove_block(self,block):
		del self.blocks[block]

	def pickle_block(self,block):
		with open('Blocks/'+block.name+'.p','wb') as blockfile:
			pickle.dump(block,blockfile)

	def add_qvd_block(self,qvd,name=''):
		"""Takes a qvd object and writes a simple load statement for it.
		Load Statement example:
		TableName:
		Load
			ID	as _KEY_ID //(optional)
		,	A	as TA_A
		,	B	as TA_B
		,	C	as TA_C
		From [Filepath.qvd] (qvd);
		"""		
		if name:
			qvdname = name
		else:
			qvdname = 'QVD_' + os.path.basename(qvd.filename)[0:-4]	
		blocktext = '\n'
		blocktext = blocktext + qvd.table + ':\nLoad\n'
		#Optionalkeyload would go here.
		for field in qvd.fields:
			blocktext = blocktext + '\t[' + field + ']\tas\t[' + qvd.tablePrefix + field + '],\n'
		blocktext = blocktext + '\t' + "'ALL_" + qvd.table.upper() + "'\tas\t" + 'ALL_' + qvd.table.upper() + '\n'
		blocktext = blocktext + 'from [' + qvd.abspath + '] (qvd)\n'
		blocktext = blocktext + ';\n'
		self.blocks[qvdname] = Block(
			'QVD_' + qvd.table, 
			'Generated qvd block. QVD File: ' + qvd.abspath,
			'QVD',
			blocktext
			)

	def add_directory_QVDs(self,directory):
		files = [f for f in os.listdir(directory) if os.path.basename(f)[-4:] == '.qvd']
		for f in files:
			block = QVD(os.path.join(directory,f))
			self.add_qvd_block(block)

	def add_directory_blocks(self,directory):		
		files = [f for f in os.listdir(directory) if os.path.basename(f)[-2:] == '.p']
		for f in files:
			self.add_pickled_block(f)
			
	def split_block_tabs(self,block):
		blocktext = block.text
		#Tab looks like //$tab something.
		tabs = [] //will be a list of blocks.
		current_tab = []
		tab_name = block.name + '_TAB1'
		for line in blocktext.split('\n'):
			if line.startswith('///$tab'): #Beginning of new tab.
				if current_tab = []: #Hadnt found any actual text yet.
					tab_name = line[6:] # Remainder of line.
					pass
				else: #Create block to append to tab.
					tab_block = Block(
						tab_name,
						'tab belonging to block: {0}'.format(block.name),
						'TAB',
						'\n'.join(current_tab)
					)
					tabs.append(tab_block) # Add to tabs.
					current_tab = [] #Restart current tab.
					tab_name = line[6:] # Remainder of line - name of next tab.
			else:
				current_tab.append(line) ##Add line to tab.
		return tabs

class QVD:
	"""Takes a qvd file and makes a python class with its xml header info."""

	def __init__(self,qvdfile,tablename=False,prefix=False):
		self.qvdheader = self.loadqvdfile(qvdfile)
		
		def setprops(qvdfile,tablename,prefix):
			#Turn fields and table name into some useful attributes of the class.
			##First do attributes that will be used in the script, here we can transform them to be more useful.
			self.fields = [e.text for e in self.qvdheader.findall('.//FieldName')]
			if tablename:
				self.table = tablename
			else:
				self.table 	= ''.join([c for c in self.qvdheader.find('.//TableName').text if not c.isspace()])
			if prefix:
				self.tablePrefix = prefix + '_'
			else:
				self.tablePrefix = self.table[0:2].upper() + '_'
			self.filename = os.path.basename(qvdfile)
			self.abspath = os.path.abspath(qvdfile)
			##Second covert some of the xml items into attributes directly. These are more for information purposes. Here we preserve Names from the
			self.CreatorDoc = self.qvdheader.find('.//CreatorDoc').text
			self.CreateUtcTime = self.qvdheader.find('.//CreateUtcTime').text

		setprops(qvdfile,tablename,prefix)

	def loadqvdfile(self, infile):
		with open(infile,'rb') as qvdfile:
			endphrase =  '</QvdTableHeader>'
			filedata = ''
			while filedata[-len(endphrase):] != endphrase: 
				byte = qvdfile.read(1)
				try:
					x = unicodedata.category(byte.decode("utf-8",'ignore'))
				except TypeError:
					print('Unexpected end of file...')
					break	
				else:
					filedata += byte.decode("utf-8",'ignore')		
		return ET.fromstring(filedata)
