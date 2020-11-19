echo "Select the project to deply by index:"
echo "[1] Mongo DB"
echo "[2] Backend"
echo "[3] Frontend"
echo "[4] Bot"
echo "[5] Governor"
echo "[6] Pulsar"
echo "[7] Redis"
echo "[8] Socket"
echo "[9] All"
echo "[10] Remove All"
read INDEX


if [ $INDEX = "1" ] || [ $INDEX = "9" ]; then
    docker run -d -p 27017:27017 --name mongodb -e MONGO_INITDB_ROOT_USERNAME="hyperlynk" -e MONGO_INITDB_ROOT_PASSWORD="OnePurpleParrot" mongo

elif [ $INDEX = "2" ] || [ $INDEX = "9" ]; then
    cd ./backend
    docker build --tag backend:2.0 .
    docker run -p 8000:8000 --detach --name backend backend:2.0 

elif [ $INDEX = "3" ] || [ $INDEX = "9" ]; then
    cd ./frontend
    docker build --tag frontend:2.0 .
    docker run -p 80:80 --detach --name frontend frontend:2.0

elif [ $INDEX = "4" ] || [ $INDEX = "9" ]; then
    cd ./bot
    docker build --tag bot:1.0 .
    docker run --detach --name bot bot:1.0 

elif [ $INDEX = "5" ] || [ $INDEX = "9" ]; then
    cd ./governor
    docker build --tag governor:1.0 .
    docker run --detach --name governor governor:1.0

elif [ $INDEX = "6" ] || [ $INDEX = "9" ]; then
    docker run -it --name=pulsar -p 6650:6650 -p 8080:8080 --detach apachepulsar/pulsar:2.6.1 bin/pulsar standalone

elif [ $INDEX = "7" ] || [ $INDEX = "9" ]; then
    docker run --name=redis0 --publish=6379:6379 --hostname=redis --restart=on-failure --detach redis:latest
    docker run --name=redis1 --publish=6380:6379 --hostname=redis --restart=on-failure --detach redis:latest

elif [ $INDEX = "8" ] || [ $INDEX = "9" ]; then
    cd ./realtime
    docker build --tag realtime:2.0 .
    docker run -p 5000:5000 -p 5001:5001 --detach --name realtime realtime:2.0 

elif [ $INDEX = "10" ]; then
    docker rm --force mongodb
    docker rm --force backend
    docker rm --force frontend
    docker rm --force bot
    docker rm --force governor
    docker rm --force pulsar
    docker rm --force redis0
    docker rm --force redis1
    docker rm --force realtime
elif [ $INDEX = "11" ]; then
    docker rm --force mongodb
    docker rm --force backend
    docker rm --force realtime
else
    echo "Index is not valid."
fi
