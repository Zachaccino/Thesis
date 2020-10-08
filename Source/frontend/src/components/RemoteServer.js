function RemoteServer() {
  const deploy = true;
  if (deploy) {
    return "http://3.24.141.26:8000";
  } else {
    return "http://127.0.0.1:8000";
  }
}

export default RemoteServer;
