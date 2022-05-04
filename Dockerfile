FROM python:3.9.10
ADD make_plot/ .
RUN pip install --trusted-host pypi.python.org -r requirements.txt
ENTRYPOINT ["python", "main.py"]