import json
import sys
sys.path.insert(0,'../')
import jwzthreading_r as th
import unittest
import os

sys.path.insert(0,'../')
from mboxparser import MboxParser

class Test_Mbox_Mails(unittest.TestCase):

	def setUp(self):
		try:
			os.remove('testoutput.json')
		except OSError:
			pass

		self.mparser = MboxParser()

	def test(self):
		"""
		This function checks whether the count of values 
		in dictionary output of jwzthreading_r.py for each
		Message-ID is equal to the count of property ID in 
		testoutput.json file.
		
		"""
		value_count=0
		original_count=0
		mbox = self.mparser.create_json('xen-devel-2016-05', 'testoutput.json', file=True)
		messages = th.message_details('xen-devel-2016-05', file=True)
		#print(messages.items())
		for key,value in messages.items():
			value_count=0
			original_count = len(value)
			with open('testoutput.json') as f:
				for line in f:
					while True:
						try:
							jfile=json.loads(line)
							break
						except ValueError:
							line += next(f)


					if jfile['property'] == key:
						value_count = value_count + 1

			self.assertEquals(original_count+1,value_count,"Equal")

	def tearDown(self):
		del self.mparser

if __name__ == '__main__':
	unittest.main()
