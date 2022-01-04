FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /work
WORKDIR /work
COPY requirements.txt /work/
COPY settings.py /work/
COPY urls.py /work/
COPY mng/ /work/mng
COPY modifier.py /work/
RUN chmod +x /work/modifier.py
RUN pip install -r requirements.txt

COPY run.sh /run.sh
RUN chmod +x /run.sh

EXPOSE 8000

CMD /run.sh
