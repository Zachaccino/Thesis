function RemoteSocket() {
    const deploy = true;
    if (deploy) {
        return "http://54.153.219.233:5000";
    } else {
        return "http://127.0.0.1:5000";
    }
}

export default RemoteSocket;
  