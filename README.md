## CREATE IMAGE
docker build -t eurotek .

## RUN CONTAINER
docker run -d -p 10000:10000 --name my-container eurotek  
