import React from 'react'
import Box from '@material-ui/core/Box';
import Typography from '@material-ui/core/Typography'

/*
Props:

title - Title of the content.
*/

function ContentTitle(props) {
  return (
    <Typography variant="h5" color='textPrimary'>
      <Box fontWeight="fontWeightBold">
        {props.title}
      </Box>
    </Typography>
  )
}

export default ContentTitle
