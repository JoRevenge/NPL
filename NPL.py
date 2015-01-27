#Import libraries 
import pandas as pd
import numpy as np
import pylab as P
import csv
import urllib2
from sklearn.ensemble import RandomForestRegressor
from decimal import Decimal
import random

# ---------------------------------------------------------#
#                           Get data                       #
# ---------------------------------------------------------#

# import sample data from S3 
url = 'https://trello-attachments.s3.amazonaws.com/54522d0bd5a9e7596679dd06/54c620fa57b111af46716e5c/a79bc405e58353ef79e2bbbf9adc3290/Mock_data_LGD_-_Sheet1.csv'
response = urllib2.urlopen(url)

# convert csv data to pandas dataframe 
loans = pd.read_csv(response)


# ---------------------------------------------------------#
#                      Get rid of nulls                    #
# ---------------------------------------------------------#

# Drop rows with null variables
loans = loans.dropna()

# ---------------------------------------------------------#
#                Replace currency with Decimal             #
# ---------------------------------------------------------#

# define what being currency means: 
def is_currency(serie):
	if loans[serie].dtypes == 'object':
		if loans[serie].iloc[1][0] == '$': #if it has a $ on its first line
			return True
	else: 
		return False

# Get a list of index names: 
loan_parameters = list(loans.columns.values)

for parameter in loan_parameters:
	if is_currency(parameter):
		loans[parameter] = loans[parameter].map(lambda x: float(x.replace('$', '').replace(',','')))
		# these should not be floats, for greater accuracy they should be Decimal

# ---------------------------------------------------------#
#                 Make categorical data numerical          #
# ---------------------------------------------------------#

#define what being categorical means: 
def is_categorical(serie):
	first = loans[serie].iloc[1]  #first line
	#if the first line is a string, then true 
	if  isinstance(first, str):
		return True
	else: 
		return False

# make a map of unique values and corresponding numerical values: 
def map_uniques(serie):
	# we want to build a dictionary of {unique0: 0, unique1 : 1, ... }
	uniques = loans[serie].unique()
	num_map = {}
	index = 0 
	for unique in uniques:
		num_map[unique]= index
		index += 1 
	return num_map

# map the unique values to the numerical values: 
def map_series(serie):
	loans[serie] = loans[serie].map(map_uniques(serie)) 

# Turn all categorical parameters into numerical parameters  
for parameter in loan_parameters:
	if is_categorical(parameter):
		map_series(parameter)


# ---------------------------------------------------------#
#                   Drop unnecessary columns               #
#           (might come from user interface later)         #
#          (Should also drop all the Object dtypes)        #
# ---------------------------------------------------------#

# drop the random generator 
loans = loans.drop(['Random stuff'], axis = 1) # axis 1 means column


# ---------------------------------------------------------#
#             Split into test and training data            #
# ---------------------------------------------------------#


# separate data into training and test sets 
def split_dataframe(dataframe): 

	# initialize empty training and test sets 
	full_set = dataframe.values
	training_set = []
	test_set = []
	num_rows = loans.shape[0]
	percent_test = 0.3

	#randomly assign lines to either trainig or test
	for line in range(0,num_rows):
		i = random.random()
		if i < percent_test:
			training_set.append(full_set[line])
			#print(full_set[line])
		else: 
			test_set.append(full_set[line])
	return test_set, training_set

#create test and training set
test_set, training_set = split_dataframe(loans)

# ---------------------------------------------------------#
#         Split the training set into data and target      #
# ---------------------------------------------------------#

num_cols = len(training_set[0])-1

def split_target (set): 
	data = []
	target = []
	for line in set:
 		data.append(line[0:num_cols])
		target.append(line[num_cols])
	return data, target 

#tests: 
#print 'first line of the training data is %s ' % train_data[0]
#print 'first line of the training targets is %s' % train_target[0]

# ---------------------------------------------------------#
#       Create list in the right format for scikit         #
# ---------------------------------------------------------#

train_data, train_target = split_target(training_set)
train_set = [train_data,train_target]

# ---------------------------------------------------------#
#                     Generate forest                      #
# ---------------------------------------------------------#

# random forest code
rf = RandomForestRegressor(n_estimators=150, min_samples_split=2, n_jobs=-1)

# fit the training data
print('fitting the model')
predictor = rf.fit(train_data, train_target)
# run model against test data
#print predictor
predictions = rf.predict(train_data)

for i in range(0,5):
	predicted = predictions [i]
	actual = train_target[i]
	print 'Predicted: %1.0f' % predicted
	print 'Correct: %1.0f' % actual
	print ''
