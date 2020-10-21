docker rm -f realtime

cd ./realtime
docker build --tag realtime:2.0 .
docker run -p 5000:5000 -p 5001:5001 --name realtime realtime:2.0