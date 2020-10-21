function RemoteSocket() {
    const deploy = true;
    if (deploy) {
        return "http://3.24.141.26:";
    } else {
        return "http://127.0.0.1:";
    }
}

export default RemoteSocket;
  