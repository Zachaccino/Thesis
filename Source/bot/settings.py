DEVELOPMENT_ADDRESS = '127.0.0.1'

DEPLOYMENT_ADDRESS = '3.24.141.26'

DEPLOY = True

SERVER_ADDRESS = DEPLOYMENT_ADDRESS if DEPLOY else DEVELOPMENT_ADDRESS

BACKEND_PORT = 8000

BACKEND_ADDRESS = 'http://' + SERVER_ADDRESS + ":" + str(BACKEND_PORT)

COUNT = 1