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

  const [realtimeCurrent, setRealtimeCurrent] = useState([{"id": "Input", "data": []}, {"id": "Output", "data": []}]);
  const [realtimeVoltage, setRealtimeVoltage] = useState([{"id": "Input", "data": []}, {"id": "Output", "data": []}]);
  const [realtimePwr, setRealtimePwr] = useState([{"id": "Input", "data": []}, {"id": "Output", "data": []}]);
  const [realtimeEfficiency, setRealtimeEfficiency] = useState([{"id": "Input", "data": []}, {"id": "Output", "data": []}]);

  const [aggregateCurrent, setAggregateCurrent] = useState([{"id": "Input", "data": []}, {"id": "Output", "data": []}]);
  const [aggregateVoltage, setAggregateVoltage] = useState([{"id": "Input", "data": []}, {"id": "Output", "data": []}]);
  const [aggregatePwr, setAggregatePwr] = useState([{"id": "Input", "data": []}, {"id": "Output", "data": []}]);
  const [aggregateEfficiency, setAggregateEfficiency] = useState([{"id": "Input", "data": []}, {"id": "Output", "data": []}]);

  const socket = openSocket(RemoteSocket());
  
  useEffect(() => {
    const fetchRealtimeData = () => {
      axios.post(RemoteServer() + '/panel_detail', { "device_id": panel, "aggregation": false})
        .then(res => {
          setRegion(res.data["Payload"]["region"])
          setStatus(res.data["Payload"]["status"])
          setRealtimeCurrent(res.data["Payload"]["current_graph"])
          setRealtimeVoltage(res.data["Payload"]["voltage_graph"])
          setRealtimePwr(res.data["Payload"]["pwr_graph"])
          setRealtimeEfficiency(res.data["Payload"]["efficiency_graph"])
        });
    };

    const fetchAggregateData = async () => {
      axios.post(RemoteServer() + '/panel_detail', { "device_id": panel, "aggregation": true})
        .then(res => {
          setRegion(res.data["Payload"]["region"])
          setStatus(res.data["Payload"]["status"])
          setAggregateCurrent(res.data["Payload"]["current_graph"])
          setAggregateVoltage(res.data["Payload"]["voltage_graph"])
          setAggregatePwr(res.data["Payload"]["pwr_graph"])
          setAggregateEfficiency(res.data["Payload"]["efficiency_graph"])
        });
    };

    // Preload Graph Data.
    fetchRealtimeData();
    fetchAggregateData();


    // Provide the telemetry (A list). 
    // An element to be added (A data point).
    // index of 0 is INPUT, index of 1 is OUTPUT.
    const shiftAddTelemetryStacked = (oldList, inputElem, outputElem) => {
      let list = oldList.slice(0)
      for (let i = 0; i < list[0]["data"].length - 1; i++) {
        list[0]["data"][i]["y"] = list[0]["data"][i+1]["y"]
        list[1]["data"][i]["y"] = list[1]["data"][i+1]["y"]
      }
      if (list[0]["data"].length !== 0) {
        list[0]["data"][list[0]["data"].length - 1]["y"] = inputElem
        list[1]["data"][list[1]["data"].length - 1]["y"] = outputElem
      }
      return list
    };

    const shiftAddTelemetry = (oldList, elem) => {
      let list = oldList.slice(0)
      for (let i = 0; i < list[0]["data"].length - 1; i++) {
        list[0]["data"][i]["y"] = list[0]["data"][i+1]["y"]
      }
      if (list[0]["data"].length !== 0) {
        list[0]["data"][list[0]["data"].length - 1]["y"] = elem
      } 
      return list
    };

    // Update Graph Data.
    socket.emit('frontend_connect', {'content': panel})

    socket.on('aggregate_update', (data) => {
      setAggregateCurrent(oldTele => {
        return shiftAddTelemetryStacked(oldTele, data["CURRENT_IN"], data["CURRENT_OUT"])
      })
      setAggregateVoltage(oldTele => {
        return shiftAddTelemetryStacked(oldTele, data["VOLTAGE_IN"], data["VOLTAGE_OUT"])
      })
      setAggregatePwr(oldTele => {
        return shiftAddTelemetryStacked(oldTele, data["CURRENT_IN"] * data["VOLTAGE_IN"], data["CURRENT_OUT"] * data["VOLTAGE_OUT"])
      })
      setAggregateEfficiency(oldTele => {
        return shiftAddTelemetry(oldTele, (data["CURRENT_OUT"] * data["VOLTAGE_OUT"]) / (data["CURRENT_IN"] * data["VOLTAGE_IN"]+0.00001) * 100)
      })
    });

    socket.on('realtime_update', (data) => {
      setRealtimeCurrent(oldTele => {
        return shiftAddTelemetryStacked(oldTele, data["CURRENT_IN"], data["CURRENT_OUT"])
      })
      
      setRealtimeVoltage(oldTele => {
        return shiftAddTelemetryStacked(oldTele, data["VOLTAGE_IN"], data["VOLTAGE_OUT"])
      })

      setRealtimePwr(oldTele => {
        return shiftAddTelemetryStacked(oldTele, data["CURRENT_IN"] * data["VOLTAGE_IN"], data["CURRENT_OUT"] * data["VOLTAGE_OUT"])
      })

      setRealtimeEfficiency(oldTele => {
        return shiftAddTelemetry(oldTele, (data["CURRENT_OUT"] * data["VOLTAGE_OUT"]) / (data["CURRENT_IN"] * data["VOLTAGE_IN"]+0.00001) * 100)
      })
    });
  }, []);

  useEffect(()=>{
    const interval = setInterval(() => {
      socket.emit("keep_alive");
    }, 1000*60);

    return () => clearInterval(interval);
  }, [])

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
        <ContentTitle title={"Aggregate Statistics"} />
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Current" data={aggregateCurrent} max={10} yLabel={"Current (A)"} legend={"Recorded Data (Last 4 Hrs)"}/>
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Voltage" data={aggregateVoltage} max={35} yLabel={"Voltage (V)"} legend={"Recorded Data (Last 4 Hrs)"}/>
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Power" data={aggregatePwr} max={260} yLabel={"Power (watt)"} legend={"Recorded Data (Last 4 Hrs)"}/>
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Efficiency" data={aggregateEfficiency} max={100} yLabel={"Percentage"} legend={"Recorded Data (Last 4 Hrs)"}/>
      </Grid>
      <Grid item xs={12}>
        <ContentTitle title={"Realtime Statistics"} />
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Current" data={realtimeCurrent} max={10} yLabel={"Current (A)"} legend={"Recorded Sample (This Session)"}/>
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Voltage" data={realtimeVoltage} max={35} yLabel={"Voltage (V)"} legend={"Recorded Sample (This Session)"}/>
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Power" data={realtimePwr} max={260} yLabel={"Power (watt)"} legend={"Recorded Sample (This Session)"}/>
      </Grid>
      <Grid item xs={6}>
        <TrendCard title="Efficiency" data={realtimeEfficiency} max={100} yLabel={"Percentage"} legend={"Recorded Sample (This Session)"}/>
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
    </Grid>
  )
}

export default PanelDetail
