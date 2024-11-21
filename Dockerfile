FROM python:3

RUN pip install requests
RUN pip install pydantic

# Adding numpy
RUN pip install numpy

# Adding textblob
RUN pip install textblob 

#Important so we will have access to the run.sh file 
COPY . . 

CMD ["sh", "run.sh"]
