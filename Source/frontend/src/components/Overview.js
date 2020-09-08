import React from 'react'
import Grid from '@material-ui/core/Grid';
import ContentTitle from './ContentTitle'
import StatusCard from './StatusCard'
import TrendCard from './TrendCard'
import RemoteServer from './RemoteServer';
import axios from 'axios';
import { useState, useEffect } from 'react';


function Overview() {
  const [health, setHealth] = useState("Loading");
  const [operatingCounts, setOperatingCounts] = useState("Loading");
  const [offlineCounts, setOfflineCounts] = useState("Loading");
  const [failureCounts, setFailureCounts] = useState("Loading");
  const [failurePercentage, setFailurePercentage] = useState("Loading");
  const [powerIn, setPowerIn] = useState("Loading");
  const [powerOut, setPowerOut] = useState("Loading");
  const [serverStatus, setServerStatus] = useState("Loading");
  const [regionCounts, setRegionCounts] = useState("Loading");

  useEffect(() => {
    const fetchData = () => {
      axios.get(RemoteServer() + '/overview')
        .then(res => {
          setHealth(res.data["Payload"]["health"])
          setOperatingCounts(res.data["Payload"]["operating_counts"])
          setOfflineCounts(res.data["Payload"]["offline_counts"])
          setFailureCounts(res.data["Payload"]["failure_counts"])
          setFailurePercentage(res.data["Payload"]["failure_percentage"])
          setPowerOut(res.data["Payload"]["power_out"])
          setPowerIn(res.data["Payload"]["power_in"])
          setServerStatus(res.data["Payload"]["server_status"])
          setRegionCounts(res.data["Payload"]["region_counts"])
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
        <ContentTitle title="System Overview" />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatusCard title="System Health" value={health} />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatusCard title="Operating Panels" value={operatingCounts} />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatusCard title="Offline Panels" value={offlineCounts} />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatusCard title="Failure Panels" value={failureCounts} />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatusCard title="Failure Percentage" value={failurePercentage} />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatusCard title="Output Power" value={powerOut} />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatusCard title="Input Power" value={powerIn} />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatusCard title="Server Status" value={serverStatus} />
      </Grid>
      <Grid item xs={6} sm={3}>
        <StatusCard title="Region Counts" value={regionCounts} />
      </Grid>
    </Grid>
  )
}

export default Overview
