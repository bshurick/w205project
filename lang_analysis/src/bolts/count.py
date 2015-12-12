from __future__ import absolute_import, print_function, unicode_literals
from collections import Counter
from streamparse.bolt import Bolt
import psycopg2
import datetime as DT
TBL='tweet_word_count'

class TweetCounter(Bolt):
	def initialize(self, conf, ctx):
		self.counts = Counter()
		
	def process(self, tup):
		word = tup.values[0]
		word = word.lower()
		
		conn = psycopg2.connect("user=postgres")
		cur = conn.cursor()
		cur.execute('''SELECT * from public.{}
			WHERE word='{}' and day='{}' and language='{}';'''.format(
				TBL, word, DT.datetime.now().strftime('%Y-%m-%d'),'es'))
		if cur.fetchone():
			SQL = '''UPDATE public.{} 
				SET cnt=cnt+{}
				WHERE word='{}'
				AND day='{}'
				AND language='{}';
			'''.format(TBL,1,word,
					DT.datetime.now().strftime('%Y-%m-%d'),'es')
		else:
			SQL = '''INSERT INTO public.{}
				(language, day, word, cnt)
				VALUES ('{}','{}','{}','{}');
				'''.format(TBL,'es',DT.datetime.now().strftime('%Y-%m-%d'),
						word, 1)
		cur.execute(SQL)
		conn.commit()
		cur.close()
		conn.close()
		
		# emit
		# Increment the local count
		self.counts[word] += 1
		self.emit([word, self.counts[word]])
		#self.log('{}: {}'.format(word, self.counts[word]))

