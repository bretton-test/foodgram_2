FROM python:3.7-slim
WORKDIR /app
COPY ./ .
RUN pip3 install -r requirements.txt --no-cache-dir
#RUN --mount=type=cache,target=/root/.cache/pip \
#        pip3 install -r requirements.txt
CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0:8000" ]
