import React from 'react'
import Grid from '@material-ui/core/Grid';
import ContentTitle from './ContentTitle'
import LiveCard from './LiveCard'
import { useState, useEffect } from 'react';
import RemoteServer from './RemoteServer';
import axios from 'axios';


function CardsForAllRegions() {
  const cards = []
  const [regions, setRegions] = useState([]);
  const [powerIns, setPowerIns] = useState([]);
  const [powerOuts, setPowerOuts] = useState([]);

  useEffect(() => {
    const fetchData = () => {
      axios.get(RemoteServer() + '/regions')
        .then(res => {
          setRegions(res.data["Payload"]["Regions"])
          setPowerIns(res.data["Payload"]["In"])
          setPowerOuts(res.data["Payload"]["Out"])
        });
    };

    fetchData();

    const interval = setInterval(() => {
      fetchData();
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  for (var i = 0; i < regions.length; i++) {
    const redirectURL = "/panels/" + regions[i]
    cards.push(
      <Grid item xs={6} sm={3}>
        <LiveCard title={regions[i]} value={powerOuts[i]} to={redirectURL} />
      </Grid>
    )
  }
  return cards
}


function Regions() {
  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <ContentTitle title="Regions" />
      </Grid>
      <CardsForAllRegions />
    </Grid>
  )
}

export default Regions
