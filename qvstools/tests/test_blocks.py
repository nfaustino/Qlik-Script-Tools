import unittest, re, os
from qvstools.blocks import *

class TestBlock(unittest.TestCase):
	def setUp(self):
		print ("SETUP!")

	def tearDown(self):
		print ("TEAR DOWN!")
		#Delete output file:
		outputfiles = ['testoutput.txt']
		try:
			delete = [os.remove(x) for x in outputfiles]
		except FileNotFoundError:
			print('No files to delete.')

	def test_Block(self):
		print("Testing Block Class")
		goodblock = Block('good block','good description','good type','good text')
		self.assertEqual(goodblock.name, 'good block')
		self.assertEqual(goodblock.description,'good description')
		self.assertEqual(goodblock.type, 'good type')
		self.assertEqual(goodblock.text, 'good text')

	def test_BlockLibrary(self):
		print('Testing Block Library Class')
		#Create a block lib.
		myblocklib = BlockLibrary('Test')
		self.assertEqual(myblocklib.name,'Test')
		#Add a block from a text file.
		myblocklib.add_text_block('Testblock','Test of Main block','BlockType','blocks/source/test_replacelist.qvs')
		self.assertEqual(myblocklib.blocks['Testblock'].name,'Testblock')
		self.assertEqual(myblocklib.blocks['Testblock'].description, 'Test of Main block')
		self.assertEqual(myblocklib.blocks['Testblock'].type, 'BlockType')
		with open('blocks/source/test_replacelist.qvs','r') as comparetext:
			text_original = comparetext.read()
			text_scrubbed = '\n'.join([line for line in text_original.split('\n') if not re.search(r"//\(@[\d]",line) ]) 
			self.assertEqual(myblocklib.blocks['Testblock'].text,text_scrubbed)
		self.assertEqual(set(myblocklib.blocks['Testblock'].replacelist), set([('@0','Test Replace definition 0'),('@1','Test Replace definition 1'),('@2','Test Replace definition 2')]))
		#print(myblocklib.blocks['Testblock'].text)
		#Pickle that block.
		myblocklib.pickle_block(myblocklib.blocks['Testblock'])
		#Remove it from the library.
		myblocklib.remove_block('Testblock')
		self.assertEqual(len(myblocklib.blocks.keys()),0)
		#Unpickle that block.
		#Test that block still has the same contents.
		myblocklib.add_pickled_block('Blocks/Testblock.p')
		with open('blocks/source/test_replacelist.qvs','r') as comparetext:
			text_original = comparetext.read()
			text_scrubbed = '\n'.join([line for line in text_original.split('\n') if not re.search(r"//\(@[\d]",line) ]) 
			self.assertEqual(myblocklib.blocks['Testblock'].text,text_scrubbed)
		#Test write a block
		myblocklib.blocks['Testblock'].write('testoutput.txt',['foo','bar','bad'])
		#Test string replacement.
		myblocklib.add_text_block('TestReplaceBlock','TestReplaceBlock','ReplaceType','Blocks/source/block_CallMeta.qvs')
		myblocklib.blocks['TestReplaceBlock'].write('testoutput.txt',['myTable'])

	def test_writeTab(self):
		BlockLibrary.write_tab('TABNAME','testoutput.txt','w')	#Can call without instantiating because staticmethod. Yay!
		with open('testoutput.txt','r') as comparetext:
			self.assertEqual(comparetext.read(),'\n///$tab TABNAME\n')



	def test_QVD_write(self):
		print('Testing QVD load script writing.')
		#Load a qvd.
		tablename = 'Blah'
		testqvd = QVD(r'qvstools\tests\testdata\Test.qvd')
		#create a block library:
		myblocklib = BlockLibrary('Test')
		#Generate a block from my qvd.
		myblocklib.add_qvd_block(r'qvstools\tests\testdata\Test.qvd','QVD_testqvd',tablename=tablename,prefix='XX')
		myblocklib.add_text_block('DEF_META','Meta SUB Definition','SUB','blocks/source/sub_Metadata.qvs')
		myblocklib.add_text_block('CALL_META','Call meta block','BLOCK','blocks/source/block_CallMeta.qvs')
		myblocklib.add_text_block('INIT_META','Initialise meta block','BLOCK','blocks/source/block_InitMeta.qvs')

		myblocklib.blocks['DEF_META'].write('testoutput.txt',mode='w')
		myblocklib.blocks['INIT_META'].write('testoutput.txt')
		myblocklib.blocks['QVD_testqvd'].write('testoutput.txt')
		myblocklib.blocks['CALL_META'].write('testoutput.txt',[tablename])

	def test_add_directory_qvd(self):
		print('Testing loading a directory of qvds.')
		#create a block library:
		myblocklib = BlockLibrary('Test')
		#Load directory:
		myblocklib.add_directory_qvd(r'qvstools\tests\testdata')
		#Write blocks to file.
		for block in [b for b in myblocklib.blocks if myblocklib.blocks[b].type == 'QVD']:
			myblocklib.blocks[block].write('testoutput.txt')

	def test_load_defaults(self):
		print('Testing loading the default blocks when creating a library.')
		myblocklib = BlockLibrary('Test',load_defaults = True)

	def test_xml_write(self):
		myblocklib = BlockLibrary('Test',load_defaults = True)
		for block in myblocklib.blocks:
			myblocklib.block_to_xml(block,directory='blocks')

	def test_xml_read(self):
		myblocklib = BlockLibrary('Test')
		myblocklib.add_text_block('Default_Call_Meta','Block to run after loading a table,  takes the name of the table as the replacelist.','BLOCK','blocks/source/block_CallMeta.qvs')
		#Copy block for comparison.
		myblocklib.blocks['A']=myblocklib.blocks['Default_Call_Meta']
		#Write and read back (will overwrite):
		myblocklib.block_to_xml('Default_Call_Meta',directory='blocks')
		myblocklib.add_xml_block('blocks/Default_Call_Meta.xml')
		a = myblocklib.blocks['A']
		b = myblocklib.blocks['Default_Call_Meta']
		self.assertEqual(a.type,b.type)
		self.assertEqual(a.text,b.text)
		self.assertEqual(a.description,b.description)
		self.assertEqual(a.replacelist,b.replacelist)





if __name__ == '__main__':
        unittest.main()