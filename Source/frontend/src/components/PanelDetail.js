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
import openSocket from 'socket.io-client';
import RemoteSocket from "./RemoteSocket"
import Panels from './Panels';


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

function SwitchControlPanel(name, action, desc, event_code, event_value) {
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
              {desc}
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
                {action}
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
    SwitchControlPanel("Power Setting", "Shutdown", "This will shutdown the power converter.", "powerdown", 1)
  )
}

function PanelDetail(props) {
  let { panel } = useParams();
  const [region, setRegion] = useState("Loading");
  const [status, setStatus] = useState("Loading");
  const [aggregation, setAggregation] = useState(true);
  const [current, setCurrent] = useState();
  const [voltage, setVoltage] = useState();
  const [pwr, setPwr] = useState();
  const [efficiency, setEfficiency] = useState();
  const [refreshPeriod, setRefreshPeriod] = useState(1000*10);
  const [loading, setLoading] = useState(true);

  const socket = openSocket(RemoteSocket());
  const [realData, setRealData] = useState({});
  const [aggrData, setAggrData] = useState({});

  function AggregationSwitch(name, action) {
    const classes = useStyles();
    let { panel } = useParams();
  
    const toggleAggregationMode = () => {
      if (aggregation) {
        setAggregation(false)
      } else {
        setAggregation(true)
      }
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
                Data Aggregation
              </Box>
            </Typography>
          </Grid>
          <Grid item>
            <Typography variant="subtitle1" color='textSecondary'>
              <Box fontWeight="fontWeightBold">
                Toggle between showing data sampled every second or every minute.
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
                <Button variant="contained" color="primary" onClick={toggleAggregationMode}>
                  Toggle
                </Button>
              </Grid>
            </Grid>
          </Grid>
        </Grid>
      </Paper>
    )
  }
  
  useEffect(() => {
    axios.post(RemoteServer() + '/panel_detail', { "device_id": panel, "aggregation": true})
      .then(res => {
        setAggrData(res.data)
      });
    axios.post(RemoteServer() + '/panel_detail', { "device_id": panel, "aggregation": false})
      .then(res => {
        setRealData(res.data)
      });
    setLoading(false);
  }, [aggregation]);

  useEffect(() => {
    socket.emit('frontend_connect', {'content': panel})
    socket.on('aggregate_update', (data) => {
      setAggrData(data);
    });
    socket.on('realtime_update', (data) => {
      setRealData(data);
    });
  }, []);

  useEffect(() => {
    if (!aggregation && !loading) {
      setRegion(realData["Payload"]["region"])
      setStatus(realData["Payload"]["status"])
      setCurrent(realData["Payload"]["current_graph"])
      setVoltage(realData["Payload"]["voltage_graph"])
      setPwr(realData["Payload"]["pwr_graph"])
      setEfficiency(realData["Payload"]["efficiency_graph"])
    }
  }, [realData, aggregation]);

  useEffect(() => {
    if (aggregation && !loading) {
      setRegion(aggrData["Payload"]["region"])
      setStatus(aggrData["Payload"]["status"])
      setCurrent(aggrData["Payload"]["current_graph"])
      setVoltage(aggrData["Payload"]["voltage_graph"])
      setPwr(aggrData["Payload"]["pwr_graph"])
      setEfficiency(aggrData["Payload"]["efficiency_graph"])
    }
  }, [aggrData, aggregation]);




  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <ContentTitle title={"Device Information"} />
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
        <ContentTitle title={"Statistics"} />
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Current" data={current} max={10} yLabel={"Current (A)"} />
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Voltage" data={voltage} max={35} yLabel={"Voltage (V)"} />
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Power" data={pwr} max={260} yLabel={"Power (watt)"} />
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Efficiency" data={efficiency} max={100} yLabel={"Percentage"} />
      </Grid>
      <Grid item xs={12}>
        <ContentTitle title={"Control Panel"} />
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
      <Grid item xs={12}>
        <AggregationSwitch />
      </Grid>
    </Grid>
  )
}

export default PanelDetail
