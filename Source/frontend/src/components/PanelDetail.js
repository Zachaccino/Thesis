import React from 'react'
import Grid from '@material-ui/core/Grid';
import ContentTitle from './ContentTitle'
import TrendCard from './TrendCard'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles';
import Box from '@material-ui/core/Box';
import Paper from '@material-ui/core/Paper';
import Slider from '@material-ui/core/Slider';
import Button from '@material-ui/core/Button';
import { useState, useEffect } from 'react';
import { useParams } from "react-router";
import RemoteServer from './RemoteServer';
import axios from 'axios';
import StatusCard from "./StatusCard";


const useStyles = makeStyles((theme) => ({
  paper: {
    padding: theme.spacing(2),
  },
}));


function SliderControlPanel(name, def, step, min, max, event_code) {
  const classes = useStyles();
  const [sliderValue, setsliderValue] = useState(5)
  let { panel } = useParams();

  const pushEvent = () => {
    axios.post(RemoteServer() + '/push_event', { "device_id": panel, "event_code": event_code, "event_value": sliderValue })
  }

  return (
    <Paper variant="outlined" className={classes.paper}>
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="stretch"
      >
        <Grid item>
          <Typography variant="h6" color='textSecondary'>
            <Box fontWeight="fontWeightBold">
              {name}
            </Box>
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="subtitle1" color='textSecondary'>
            <Box fontWeight="fontWeightBold">
              You have selected {sliderValue}.
            </Box>
          </Typography>
        </Grid>
        <Grid item>
          <Slider
            defaultValue={def}
            onChange={(e, v) => { setsliderValue(v) }}
            aria-labelledby="discrete-slider"
            valueLabelDisplay="auto"
            step={step}
            marks
            min={min}
            max={max}
          />
        </Grid>
      </Grid>
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="flex-end"
      >
        <Grid item>
          <Button variant="contained" color="primary" onClick={pushEvent}>
            Commit Changes
          </Button>
        </Grid>
      </Grid>
    </Paper>
  )
}

function SwitchControlPanel(name, action, event_code, event_value) {
  const classes = useStyles();
  let { panel } = useParams();

  const pushEvent = () => {
    axios.post(RemoteServer() + '/push_event', { "device_id": panel, "event_code": event_code, "event_value": event_value })
  }

  return (
    <Paper variant="outlined" className={classes.paper}>
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="stretch"
      >
        <Grid item>
          <Typography variant="h6" color='textSecondary'>
            <Box fontWeight="fontWeightBold">
              {name}
            </Box>
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="subtitle1" color='textSecondary'>
            <Box fontWeight="fontWeightBold">
              This will shutdown the power converter.
            </Box>
          </Typography>
        </Grid>
        <Grid item>
          <Grid
            container
            direction="column"
            justify="center"
            alignItems="flex-end"
          >
            <Grid item>
              <Button variant="contained" color="primary" onClick={pushEvent}>
                Shutdown
              </Button>
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </Paper>
  )
}


function CurrentControlPanel() {
  return (
    SliderControlPanel("Change Current", 5, 1, 0, 15, "current")
  )
}

function VoltageControlPanel() {
  return (
    SliderControlPanel("Change Voltage", 5, 1, 0, 15, "voltage")
  )
}

function PowerControlPanel() {
  return (
    SwitchControlPanel("Power Setting", "Shutdown", "powerdown", 1)
  )
}

function PanelDetail(props) {
  let { panel } = useParams();
  const [region, setRegion] = useState("Loading");
  const [status, setStatus] = useState("Loading");
  const [current, setCurrent] = useState();
  const [voltage, setVoltage] = useState();
  const [power, setPower] = useState();

  useEffect(() => {
    const fetchData = () => {
      axios.post(RemoteServer() + '/panel_detail', { "device_id": panel })
        .then(res => {
          setRegion(res.data["Payload"]["region"])
          setStatus(res.data["Payload"]["status"])
          setCurrent(res.data["Payload"]["current_graph"])
          setVoltage(res.data["Payload"]["voltage_graph"])
          setPower(res.data["Payload"]["power_graph"])
        });
    };

    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, 1000);

    return () => clearInterval(interval);
  }, []);


  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <ContentTitle title={"Device Control Panel"} />
      </Grid>
      <Grid item xs={4}>
        <StatusCard title="Device ID" value={panel} />
      </Grid>
      <Grid item xs={4}>
        <StatusCard title="Region" value={region} />
      </Grid>
      <Grid item xs={4}>
        <StatusCard title="Status" value={status} />
      </Grid>
      <Grid item xs={12}>
        <TrendCard title="Power Output" data={power} max={250} yLabel={"Power (watt)"} />
      </Grid>
      <Grid item xs={12}>
        <TrendCard title="Current" data={current} max={15} yLabel={"Current (ampere)"} />
      </Grid>
      <Grid item xs={12}>
        <TrendCard title="Voltage" data={voltage} max={15} yLabel={"Voltage (volt)"} />
      </Grid>
      <Grid item xs={6}>
        <CurrentControlPanel />
      </Grid>
      <Grid item xs={6}>
        <VoltageControlPanel />
      </Grid>
      <Grid item xs={12}>
        <PowerControlPanel />
      </Grid>
    </Grid>
  )
}

export default PanelDetail
