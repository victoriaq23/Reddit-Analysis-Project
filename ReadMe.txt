***********************************************************************************************************************************
*This ZIP file contains the following:
***** redditData: a folder that contains .csv files of collected Reddit data 
***** trainingData: a folder containing .csv files of text data labeled with emotions and associated weights collected from a survey
      ** expanded using ConceptNet 
***** conceptNetData.py: a file containing functions that were used to expand the original training dataset of 60 words using ConceptNet
***** dataVist.py: a file containing functions used to generate data visualizations of prediction results created by using redditData 
      ** .csv files as inputs to the multi-class text classification model contained in emotionalAnalysis6.py
***** emotionalAnalysis6.py: a file containing a multi-class text classification model that was used in my projecct to conduct
      ** an emotional analysis of Reddit text data
***** JSONConverter.py: a file containing functions used to download Reddit text data from the Pushshift database
***** JSONConverterMultiprocessing.py: a file containing a version of the JSONConverter.py data collector that is modified to 
      ** use multiprocessing when cleaning collected data to decrease runtime
***** sentimentAnalysisDataVis.py: a file containing functions used to run predictions on the pre-trained sentiment analysis model
      ** VADER and create data visualizations based on those prediction results
***********************************************************************************************************************************

Credits and Acknowledgments:
*Project creator: Victoria Quin (Wellesley College, class of 2023)
*Project mentor: Dr. Randall E. Cone (Salisbury University)
*Project director: Dr. Enyue (Annie) Lu

**Funding for this project was provided by NSF Grant CCF-1757017 under the Research Experiences for Undergraduates (REU) program**

*Training data was collected through a survey created by myself and fellow researcher Aron Lankford (Swarthmore College, class of 2022)
*Thank you to Salisbury University and the HPCL Lab

***********************************************************************************************************************************

Contact Information:

*email: vq1@wellesley.edu

***********************************************************************************************************************************

Instructions:

*Packages and libraries used:
  * NLTK
  * pandas
  * plotly
  * numpy
  * tensorflow
  * keras
  * sklearn

*** Data Collection:
  * use either the JSONConverter.py or JSONConverterMultiprocessing.py file (JSONConverter.py is slightly more reliable,
  * especially for computers with less processing power) to collect text data from Reddit (these data collector programs
  * are designed to collect one specified month's worth of data at a time from one specified subreddit, user will also
  * be required to input whether comment data or submission data is collected for each run) 

*** Sentiment Analysis:
  * use the sentimentAnalysisDataVis.py file to run collected Reddit data through the VADER pre-trained sentiment analysis
  * model (part of the NLTK library) and generate a scatterplot or bar chart (of averages) data visualization
  
*** Emotional Analysis (multi-class text classification): 
  * use the emotionalAnalysis6.py file to train the multi-class text classification neural network model (built with Keras)
  * on collected training data (which can be expanded as needed using functions contained in the conceptNetData.py file)
  * and run predictions on collected Reddit data using the marked cell; data visualizations (a bar chart of average
  * weights) can be created by using the functions contained in the dataVis.py file

***********************************************************************************************************************************

Known bugs: 
* the JSONConverterMultiprocessing.py file will sometimes freeze when collecting large amounts of data, this may 
* be a memory issue, but I have not found a definite solution to that issue yet (except to run the serial implementation
* found in JSONConverter.py instead when the multiprocessing version encounters issues)

Troubleshooting: 
** Note: make sure the specified input paths (when working with reading from and writing to text files) are correct

* I got some strange errors when initially trying to train the text classification model in emotionalAnalysis6.py; 
* I was able to fix these issues by uninstalling and re-installing the packages/libraries that were generating the errors
* (StackOverflow was helpful in this case)

***********************************************************************************************************************************
  