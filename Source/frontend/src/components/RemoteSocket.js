function RemoteSocket() {
    const deploy = false;
    if (deploy) {
        return "http://3.24.141.26:5000";
    } else {
        return "http://127.0.0.1:5000";
    }
}

export default RemoteSocket;
  