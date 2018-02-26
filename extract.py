import os
import csv 

directory = os.getcwd()
newfile = open("comments/comments.csv", 'w')
writer = csv.writer(newfile, delimiter='\t')

for filename in os.listdir(directory):
   if filename.endswith(".csv"):
   		with open(filename, 'rb') as csvfile:
   			writer.writerow(["Comments/Replies"])
   			reader = csv.reader(csvfile, delimiter='\t')
   			for row in reader:
   				if len(row) >= 9:
	   				if row[7]:
	   					writer.writerow([row[7]])
	   				if row[8]:
	   					writer.writerow([row[8]])

	   		csvfile.close()
 
newfile.close()