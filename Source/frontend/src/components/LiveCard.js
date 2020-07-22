import React from 'react'
import { useState } from 'react';
import Card from '@material-ui/core/Card';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography'
import { makeStyles } from '@material-ui/core/styles';
import Box from '@material-ui/core/Box';
import CardActionArea from '@material-ui/core/CardActionArea';
import { Link } from 'react-router-dom';


const useStyles = makeStyles((theme) => ({
  grid: {
    padding: theme.spacing(2),
  },
}));


function LiveCard(props) {
  const classes = useStyles();

  return (
    <Card variant="outlined">
      <CardActionArea component={ Link } to={props.to} disableRipple={true}>
        <Grid
          container
          direction="column"
          justify="center"
          alignItems="flex-start"
          className={classes.grid}
        >
          <Grid item>
            <Typography variant="h6" color='textSecondary'>
              <Box fontWeight="fontWeightBold">
                {props.title}
              </Box>
            </Typography>
          </Grid>
          <Grid item>
            <Typography variant="h4" color='textPrimary'>
              {props.value}
            </Typography>
          </Grid>
        </Grid>
      </CardActionArea>
    </Card>

  )
}

export default LiveCard
