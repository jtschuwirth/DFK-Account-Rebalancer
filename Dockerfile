
FROM amazon/aws-lambda-python:3.9

COPY ./ ${LAMBDA_TASK_ROOT}

# Install the function's dependencies using file requirements.txt
# from your project folder.

COPY requirements.txt  .
RUN yum -y install gcc gcc-c++ libc-dev
RUN pip3 install --upgrade pip
RUN  pip3 install -r requirements.txt --target "${LAMBDA_TASK_ROOT}"

CMD [ "lambda_function.handler" ]