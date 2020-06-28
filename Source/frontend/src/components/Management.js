import React from 'react'
import Grid from '@material-ui/core/Grid'
import ContentTitle from './ContentTitle'
import Paper from '@material-ui/core/Paper'
import { makeStyles } from '@material-ui/core/styles'
import Typography from '@material-ui/core/Typography'
import Box from '@material-ui/core/Box'
import TextField from '@material-ui/core/TextField'
import Button from '@material-ui/core/Button';
import { useState, useEffect } from 'react';
import RemoteServer from './RemoteServer';
import axios from 'axios';


const useStyles = makeStyles((theme) => ({
  paper: {
    padding: theme.spacing(3),
  },
}));


function RegionRegistrationCard() {
  const classes = useStyles();
  const [region, setRegion] = useState("");

  const registerRegion = () => {
    axios.post(RemoteServer() + '/register_region', { "region_name": region})
    setRegion("")
  }

  return (
    <Paper variant="outlined" className={classes.paper}>
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="stretch"
        spacing={2}
      >
        <Grid item>
          <Typography variant="h6" color='textSecondary'>
            <Box fontWeight="fontWeightBold">
              Region Registration
            </Box>
          </Typography>
        </Grid>
        <Grid item>
          <TextField id="RegionName" label="Region Name" variant="outlined" value={region} onChange={(e, v) => { setRegion(e.target.value) }} />
        </Grid>
      </Grid>
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="flex-end"
      >
        <Grid item>
          <Button variant="contained" color="secondary" onClick={registerRegion}>
            Add New Region
          </Button>
        </Grid>
      </Grid>
    </Paper>
  )
}


function PanelRegistrationCard() {
  const classes = useStyles();
  const [region, setRegion] = useState("");
  const [deviceID, setDeviceID] = useState("");

  const assignRegion = () => {
    axios.post(RemoteServer() + '/assign_to_region', { "region_name": region, "device_id": deviceID })
    setRegion("")
    setDeviceID("")
  }

  return (
    <Paper variant="outlined" className={classes.paper}>
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="stretch"
        spacing={2}
      >
        <Grid item>
          <Typography variant="h6" color='textSecondary'>
            <Box fontWeight="fontWeightBold">
              Region Registration
            </Box>
          </Typography>
        </Grid>
        <Grid item>
          <TextField id="PanelID" label="Panel ID" variant="outlined" value={deviceID} onChange={(e, v) => { setDeviceID(e.target.value) }} />
        </Grid>
        <Grid item>
          <TextField id="RegionName" label="Region Name" variant="outlined" value={region} onChange={(e, v) => { setRegion(e.target.value) }}/>
        </Grid>
      </Grid>
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="flex-end"
      >
        <Grid item>
          <Button variant="contained" color="secondary" onClick={assignRegion}>
            Add New Panel
          </Button>
        </Grid>
      </Grid>
    </Paper>
  )
}


function Management() {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <ContentTitle title="Management" />
      </Grid>
      <Grid item xs={12}>
        <RegionRegistrationCard />
      </Grid>
      <Grid item xs={12}>
        <PanelRegistrationCard />
      </Grid>
    </Grid>
  )
}

export default Management
