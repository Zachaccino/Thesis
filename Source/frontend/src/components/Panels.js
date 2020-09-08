import React from 'react'
import Grid from '@material-ui/core/Grid';
import ContentTitle from './ContentTitle'
import LiveCard from './LiveCard'
import { useParams } from "react-router";
import { useState, useEffect } from 'react';
import RemoteServer from './RemoteServer';
import axios from 'axios';


function CardsForAllPanels() {  
  const cards = []
  let { region } = useParams();
  const [panels, setPanels] = useState([]);
  const [powerIns, setPowerIns] = useState([]);
  const [powerOuts, setPowerOuts] = useState([]);

  useEffect(() => {
    const fetchData = () => {
      axios.post(RemoteServer() + '/panels', { "region_name": region })
        .then(res => {
          setPanels(res.data["Payload"]["Panels"])
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

  for (var i = 0; i < panels.length; i++) {
    cards.push(
      <Grid item xs={12} sm={6} md={3}>
        <LiveCard title={panels[i]} value={powerOuts[i]} to={"/paneldetail/" + panels[i]} />
      </Grid>
    )
  }

  return cards
}


function Panels() {
  let { region } = useParams();

  return (
    <Grid container spacing={3}>
      <Grid item xs={12}>
        <ContentTitle title={region} />
      </Grid>
      <CardsForAllPanels />
    </Grid>
  )
}

export default Panels
