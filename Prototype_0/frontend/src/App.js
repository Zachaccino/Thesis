import React from 'react';
import CssBaseline from '@material-ui/core/CssBaseline';
import AppBar from '@material-ui/core/AppBar';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles';
import Card from '@material-ui/core/Card';
import CardContent from '@material-ui/core/CardContent';
import Grid from '@material-ui/core/Grid';
import axios from 'axios';
import { useState, useEffect } from 'react';
import LineGraph from './components/LineGraph';
import Button from '@material-ui/core/Button';
import TextField from '@material-ui/core/TextField';
import RemoteServer from './components/RemoteServer';


const useStyles = makeStyles(theme => ({
  title: {
    flexGrow: 1,
    color: 'white',
    backgroundColor: '#1b1b1b'
  },
  card: {
    minWidth: 275,
    padding: theme.spacing(1),
  },
  consoleItem: {
    padding: 10,
  },
  actionBtn: {
    marginLeft: 20,
    marginRight: 20,
    paddingTop: 15,
    paddingBottom: 15
  }
}))


function CustomAppBar(props) {
  const classes = useStyles;
  return (
    <AppBar position="sticky">
      <Toolbar className={classes.title}>
        <Typography variant="h6" className={classes.title}>
          Power Management Console
        </Typography>
      </Toolbar>
    </AppBar>
  )
}


function DeviceCard(props) {
  const classes = useStyles();
  const [voltage, setVoltage] = useState(5);
  const [ampere, setAmpere] = useState(2);

  const setOutputVoltage = () => {
    axios.post('http://' + RemoteServer() + '/add_event', {
    uid: props.device,
    event:"setVoltage",
    value: voltage
  })};

  const setOutputAmpere = () => {
    axios.post('http://' + RemoteServer() + '/add_event', {
    uid: props.device,
    event:"setAmpere",
    value: ampere
  })};

  const setPowerDown = () => {
    axios.post('http://' + RemoteServer() + '/add_event', {
    uid: props.device,
    event:"powerDown",
    value: 0
  })};

  return (
    <Card className={classes.card}>
      <CardContent>
        <Typography variant="h4" align="left" className={classes.root}>
          Device {props.device}
        </Typography>
        <LineGraph data={props.data}/>
        <Button variant="contained" color="primary" className={classes.actionBtn} onClick={setOutputVoltage}>
          Set Voltage
        </Button>
        <TextField id="standard-basic" variant="outlined" label="Target Voltage" type="number" onChange={(e) => {setVoltage(e.target.value)}} value={voltage}/>
        <Button variant="contained" color="primary" className={classes.actionBtn} onClick={setOutputAmpere}>
          Set Ampere
        </Button>
        <TextField id="standard-basic" variant="outlined" label="Target Ampere" type="number" onChange={(e) => {setAmpere(e.target.value)}} value={ampere}/>
        <Button variant="contained" color="primary" className={classes.actionBtn} onClick={setPowerDown}>
          Force Shutdown
        </Button>
      </CardContent>
    </Card>
  )
}


function Console(props) {
  const classes = useStyles();
  const [telemetries, setTelemetries] = useState({});
  const cards = Object.keys(telemetries).map(key =>
      <Grid item xs={12} className={classes.consoleItem}>
        <DeviceCard device={key} data={telemetries[key]}/>
      </Grid>
    )

  useEffect(() => {
    const fetchData = async () => {
      const res = await axios('http://' + RemoteServer() + '/overview');
      setTelemetries(res.data);
    };

    const interval = setInterval(() => {
      fetchData();
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  return (
    <Grid container>
      {cards}
    </Grid>
  )
}


function App() {
  return (
    <React.Fragment>
      <CssBaseline />
      <CustomAppBar />
      <Console />
    </React.Fragment>
  );
}

export default App;
