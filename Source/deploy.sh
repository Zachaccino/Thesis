echo "Select the project to deply by index:"
echo "[1] Mongo DB"
echo "[2] Backend"
echo "[3] Frontend"
echo "[4] Bot"
echo "[5] Governor"
echo "[6] All"
echo "[7] Remove All"
read INDEX

SERVER_ADDRESS=192.168.1.14


if [ $INDEX = "1" ] || [ $INDEX = "6" ]; then
    docker run -d -p 27017:27017 --name mongodb -e MONGO_INITDB_ROOT_USERNAME="hyperlynk" -e MONGO_INITDB_ROOT_PASSWORD="OnePurpleParrot" mongo

elif [ $INDEX = "2" ] || [ $INDEX = "6" ]; then
    cd ./backend
    docker build --tag backend:2.0 .
    docker run -e "SERVER_ADDRESS=$SERVER_ADDRESS" -p 8000:8000 --detach --name backend backend:2.0 

elif [ $INDEX = "3" ] || [ $INDEX = "6" ]; then
    cd ./frontend
    docker build --tag frontend:2.0 .
    docker run -p 80:80 --detach --name frontend frontend:2.0

elif [ $INDEX = "4" ] || [ $INDEX = "6" ]; then
    cd ./bot
    docker build --tag bot:1.0 .
    docker run -e "SERVER_ADDRESS=$SERVER_ADDRESS" --detach --name bot bot:1.0 

elif [ $INDEX = "5" ] || [ $INDEX = "6" ]; then
    cd ./governor
    docker build --tag governor:1.0 .
    docker run -e "SERVER_ADDRESS=$SERVER_ADDRESS" --detach --name governor governor:1.0

elif [ $INDEX = "7" ]; then
    docker rm --force mongodb
    docker rm --force backend
    docker rm --force frontend
    docker rm --force bot
    docker rm --force governor

else
    echo "Index is not valid."
fi
