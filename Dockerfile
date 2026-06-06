FROM apify/actor-python:3.11

WORKDIR /usr/src/app

# Install actor + SDK deps
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and install the sol package
COPY . .
RUN pip install --no-cache-dir src/

CMD ["python", "main.py"]
