import React from 'react'
import Paper from '@material-ui/core/Paper';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles';
import Box from '@material-ui/core/Box';

/*
Props:

title - Status title.
value - Value of the status.
*/


const useStyles = makeStyles((theme) => ({
  paper: {
    padding: theme.spacing(2),
  },
  topItem: {
    marginTop: theme.spacing(2),
  },
  bottomItem: {
    marginBottom: theme.spacing(2),
  }
}));

function StatusCard(props) {
  const classes = useStyles();

  return (
    <Paper variant="outlined" className={classes.paper}>
      <Grid
        container
        direction="column"
        justify="center"
        alignItems="center"
      >
        <Grid item className={classes.topItem}>
          <Typography variant="h6" color='textSecondary'>
            <Box fontWeight="fontWeightBold">
              {props.title}
            </Box>
          </Typography>
        </Grid>
        <Grid item className={classes.bottomItem}>
          <Typography variant="h4" color='textPrimary'>
              {props.value}
          </Typography>
        </Grid>
      </Grid>
    </Paper>
  )
}

export default StatusCard
