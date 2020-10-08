function RemoteServer() {
  const deploy = true;
  if (deploy) {
    return "http://54.153.219.233:8000";
  } else {
    return "http://127.0.0.1:8000";
  }
}

export default RemoteServer;
