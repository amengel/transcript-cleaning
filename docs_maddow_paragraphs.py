## Purpose: read in text documents and split into CSV

import csv
import os
import string # to test for punctuation and whitespace
import itertools # for combinding lists of lists into single list


## specify file path here
direct = '~/Dropbox/Vandy/Prospectus Prelims/race rhetoric/case studies/Race stories/TV Transcripts/Maddow/All'
years = ['2008','2009','2010','2011','2012', '2013', '2014', '2015', '2016']
rows = [['show_id', 'document_id', 'date', 'show', 'text', 'speaker']]


for y in years:
	f_names = os.listdir(direct + '/' + y)
	if f_names[0] == '.DS_Store':
		f_names.pop(0)

	for indiv_f in f_names:
		print(indiv_f)
		## Reading in the docs
		f_path = direct + '/' + y  + '/' + indiv_f
		with open(f_path, 'r') as f:
			docs = f.read()
		f.close()
			# Splitting on newlines
		
		docs = docs.split('\f')
		
		for d in docs:
			lines = d.split('\n')
			for n in xrange(0,len(lines)):
				# finding the "XXX words line"
				if len(lines[n]) > 6:
					if lines[n][0].isdigit() and lines[n][-5:] == 'words':
						word_count_position = n
					elif lines[n][0:11] == '\xc2\xa9oxant Inc' and lines[n].strip().lower()[-16:] == 'rights reserved.':
						copyright_position = n 
					elif lines[n][0:9] == 'Copyright' and lines[n].strip().lower()[-16:] == 'rights reserved.':
						copyright_position = n 
					elif lines[n][0:8] == 'Document' and len(lines[n].strip().split(' ')) == 2:
						show_id = lines[n].strip().split(' ')[1]
						document_end_position = n
			
			show = lines[word_count_position + 2]
			date = lines[word_count_position + 1]

			#print(date)

			txt = '\n'.join(lines[copyright_position + 2:document_end_position - 1])

			# error handling for showdates with no episode but transcript still generated
			if len(txt) > 800:
				# Capture all possible speaking instances:
				ind = [pos for pos, char in enumerate(txt) if char == ':']
				
				breaks = []
				# test characters before the index. Capitals are speaker information that I'm splitting on
				for c in ind:
					brk = ''
					for i in xrange(0,c+1):
						if txt[c+1] not in string.whitespace:
							break
						# cleaning up for error handling given interjections
						elif txt[c-i-3:c-i] == ' OK':
							break
						elif txt[c-i] in string.whitespace and txt[c-i-1] in string.punctuation.replace(',', '').replace('"', '').replace('.', '') and txt[c-i-2].isupper() == False:
							break
						elif txt[c-i-6:c-i] == 'CLIPS)' or txt[c-i-5:c-i] == 'CLIP)':
							break
						elif txt[c-i-3:c-i] == '...':
							break
						elif txt[c-i-3:c-i] == ': (':
							break
						elif txt[c-i] in string.whitespace and txt[c-i-1] == '.' and txt[c-i-2].isupper() == False:
							brk += txt[c-i]
							break
						elif txt[c-i] in string.whitespace and txt[c-i-2] == '.' and txt[c-i-3].isupper() == False:
							brk += txt[c-i]
							break
						elif txt[c-i].isupper() == True or txt[c-i] in string.whitespace or txt[c-i] in string.punctuation:
							brk += txt[c-i]
						elif 'voice' in txt[c-11:c] and txt[c-15:c-13].isupper() == True:
							brk += txt[c-i]
						else:
							break
					# Reverse character string to pass as cutpoint
					breaks.append(brk[::-1])

				# Cleaning up breaks conceptually too small
				breaks = filter(lambda x: len(x) >= 3, breaks)
				for i in xrange(0, len(breaks)):
					if breaks[i][0] in string.punctuation:
						breaks[i] = breaks[i][1:]

				body = []
				for i in xrange(0,len(breaks)):
					# can i append breaks[i] and then the text to include the speaker?
					if i == 0:
						body.append(txt.split(breaks[i], 1)[0])
						txt = txt.split(breaks[i], 1)[1]
					else:
						body.append(breaks[i-1] + txt.split(breaks[i], 1)[0])
					if i > 0 and len(txt.split(breaks[i], 1)) == 2:
						txt = txt.split(breaks[i], 1)[1]
					if i == len(breaks) - 1:
						body.append(breaks[i] + txt)

				body.pop(0)
				# And splitting on paragraphing
				for i in xrange(0, len(body)):
					body[i] = body[i].split('\n\n')

				# Flattening to single list
				body = list(itertools.chain.from_iterable(body))
				# Removing empty docs from splitting
				body = filter(lambda x: x.strip(), body)

				# Cleaning up to add to CSV as speaker docvar
				speak = []
				for i in xrange(0,len(breaks)):
					spk = breaks[i].replace(':', '').replace('\n', '').strip()
					if len(spk) == 0:
						continue
					elif len(spk) <= 3 and spk[0].isupper() == False:
						continue
					for j in xrange(0, len(spk)):
						if spk[0] == '.' or spk[0] == '"':
							spk = spk[1:]
					if spk[0] == '(' and ')' in spk:
						d1 = spk.index('(')
						d2 = spk.index(')')
						spk = spk[d2+1:]
					speak.append(spk)

				speak = list(set(speak))
				speak = filter(lambda x: len(x) >= 2, speak)

				for b in xrange(0,len(body)):
					# eliminating inappropriate documents based on transitions to audio/video clips
					if body[b].lower().strip()[0:6] == '(begin' and len(body[b]) <= 30:
						pass
					elif body[b].lower().strip()[0:4] == '(end' and len(body[b]) <= 30:
						pass
					elif body[b].lower().strip()[0:11] == '(commercial' and len(body[b]) <= 25:
						pass
					elif 'laughter' in body[b].lower().strip() and len(body[b]) <= 15:
						pass
					elif 'unintelligible' in body[b].lower().strip() and len(body[b]) <= 18:
						pass
					elif body[b].lower().strip()[0:6] == '(cross' and len(body[b]) <= 15:
						pass
					elif 'cheers' in body[b].lower().strip()[:10] and len(body[b]) <= 22:
						pass
					elif 'applause' in body[b].lower().strip() and len(body[b]) <= 22:
						pass
					elif body[b].lower().strip()[0:25] == 'this is a rush transcript':
						pass
					elif body[b].lower().strip()[0:33] == 'content and programming copyright':
						pass		
					else:
						row = []
						document_id = show_id +'_' + str(b + 1) 
						# adding in speaker notes
						# check to see if body field matches speaker tags
						for i in speak:
							#print(i)
							spk = ''
							if i + ':' in body[b]:
								spk = i
								break
							elif b != 0:
								spk = rows[len(rows)-1][5]
						objects = [show_id, document_id, date, show, body[b], spk]
						
						for o in objects:
							o = o.replace('\r', ' ')
							o = o.replace('\n', ' ')
							o = o.replace('|', '')
							o = o.replace('^M', '')
							row.append(o)
						
						rows.append(row)

# ## Writing everything to a CSV
with open('~/Dropbox/Vandy/Prospectus Prelims/race rhetoric/case studies/Race stories/Maddow0816_graphs_out1_all.csv', 'w') as f:
	doc_csv = csv.writer(f, delimiter='|')
	doc_csv.writerows(rows)

f.close()
	