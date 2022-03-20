function RemoteSocket() {
    const deploy = true;
    if (deploy) {
        return "http://192.168.1.13:";
    } else {
        return "http://127.0.0.1:";
    }
}

export default RemoteSocket;
  