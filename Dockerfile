#Local
#FROM python:3.9

#Lambda
FROM amazon/aws-lambda-python:3.9

COPY ./ ${LAMBDA_TASK_ROOT}
COPY requirements.txt  .

#Lambda
RUN yum -y install gcc gcc-c++ libc-dev

RUN pip3 install --upgrade pip
RUN pip3 install wheel
RUN pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

#Local
#CMD [ "python",  "./run_local.py" ]

#Lambda
CMD [ "lambda_function.handler" ]