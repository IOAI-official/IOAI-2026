First, transcribe every audio chunks using an allowed ASR model. 

Then extract simple acoustic features, such as the mean and standard deviation of MFCC coefficients, and use them to group the chunks into two speakers. 

The two prefix chunks tell you which group is Speaker A and which is Speaker B. 

Assuming the speakers alternate, search for the order that produces the most natural dialogue while preserving both semantic and acoustic continuity.
