import React from 'react'
import { useState } from 'react'
import Paper from '@material-ui/core/Paper'
import Grid from '@material-ui/core/Grid'
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles'
import Box from '@material-ui/core/Box'
import LineGraph from './LineGraph'
import LinearProgress from '@material-ui/core/LinearProgress';


const useStyles = makeStyles((theme) => ({
  paper: {
    padding: theme.spacing(3),
  },
}));

function GraphLoader(props) {
  if (typeof props.data === 'undefined') {
    return (
      <LinearProgress />
    )
  } else {
    return (
      <LineGraph data={props.data} max={props.max} yLabel={props.yLabel}/>
    )
  }
}


function TrendCard(props) {
  const classes = useStyles();
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
              {props.title}
            </Box>
          </Typography>
        </Grid>
        <Grid item>
          <GraphLoader data={props.data} max={props.max} yLabel={props.yLabel}/>
        </Grid>
      </Grid>
    </Paper>
  )
}

export default TrendCard
