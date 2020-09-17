import React from 'react';
import AppBar from '@material-ui/core/AppBar';
import CssBaseline from '@material-ui/core/CssBaseline';
import Drawer from '@material-ui/core/Drawer';
import Toolbar from '@material-ui/core/Toolbar';
import Typography from '@material-ui/core/Typography'
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import { makeStyles } from '@material-ui/core/styles';
import ListItemIcon from '@material-ui/core/ListItemIcon';
import ListItemText from '@material-ui/core/ListItemText';
import DashboardIcon from '@material-ui/icons/Dashboard';
import TripOriginIcon from '@material-ui/icons/TripOrigin';
import SettingsIcon from '@material-ui/icons/Settings';
import Divider from '@material-ui/core/Divider';
import TuneIcon from '@material-ui/icons/Tune';
import Box from '@material-ui/core/Box';
import {
  BrowserRouter as Router,
  Switch,
  Route
} from "react-router-dom";

import Overview from "./components/Overview";
import Regions from './components/Regions'
import Management from './components/Management'
import Panels from './components/Panels';
import PanelDetail from './components/PanelDetail';


const drawerWidth = 240;
const appBarHeight = 65;

const useStyles = makeStyles((theme) => ({
  appBar: {
    zIndex: theme.zIndex.drawer + 1,
    background: 'white',
  },
  drawer: {
    width: drawerWidth,
    flexShrink: 0,
  },
  drawerPaper: {
    width: drawerWidth,
  },
  drawerContainer: {
    overflow: 'auto',
  },
  content: {
    marginLeft: drawerWidth,
    marginTop: appBarHeight,
    padding: theme.spacing(3),
  },
}));


function CustomAppBar() {
  const classes = useStyles();

  return (
    <AppBar position="fixed" className={classes.appBar}>
      <Toolbar>
        <Typography variant="h5" color='textPrimary'>
          <Box fontWeight="fontWeightBold">
            HYPERLYNK
          </Box>
        </Typography>
      </Toolbar>
    </AppBar>
  )
}

function CustomDrawer() {
  const classes = useStyles();

  return (
    <Drawer
      className={classes.drawer}
      variant="permanent"
      classes={{
        paper: classes.drawerPaper,
      }}
    >
      <Toolbar />
      <List>
        <ListItem button component="a" href="/">
          <ListItemIcon>
            <DashboardIcon />
          </ListItemIcon>
          <ListItemText primary={"Overview"} />
        </ListItem>
        <ListItem button component="a" href="/regions">
          <ListItemIcon>
            <TripOriginIcon />
          </ListItemIcon>
          <ListItemText primary={"Regions"} />
        </ListItem>
        <ListItem button component="a" href="/management">
          <ListItemIcon>
            <SettingsIcon />
          </ListItemIcon>
          <ListItemText primary={"Management"} />
        </ListItem>
      </List>
      <Divider />
      <List>
        <ListItem button>
          <ListItemIcon>
            <TuneIcon />
          </ListItemIcon>
          <ListItemText primary={"App Settings"} />
        </ListItem>
      </List>
    </Drawer>
  )
}

function Main() {
  const classes = useStyles();

  return (
    <Router>
      <div className={classes.content}>
        <Switch>
          <Route path="/regions" children={<Regions />} />
          <Route path="/panels/:region" children={<Panels />} />
          <Route path="/paneldetail/:panel" children={<PanelDetail />} />
          <Route path="/management" children={<Management />} />
          <Route path="/" children={<Overview />} />
        </Switch>
      </div>
    </Router>
  )
}

function App() {
  return (
    <React.Fragment>
      <CssBaseline />
      <CustomAppBar />
      <CustomDrawer />
      <Main />
    </React.Fragment>
  );
}

export default App;
