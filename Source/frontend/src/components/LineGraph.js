import React from 'react'
import { ResponsiveLine } from '@nivo/line'
import WindowDimensions from './WindowDimensions'


function LineGraph(props) {
  const { _, height } = WindowDimensions();

  return (
      <div style={{height: 500}}>
        <ResponsiveLine
          data={props.data}
          margin={{ top: 10, right: 15, bottom: 50, left: 50 }}
          xScale={{ type: 'point' }}
          yScale={{ type: 'linear', min: 0, max: props.max, stacked: false, reverse: false }}
          axisTop={null}
          axisRight={null}
          axisBottom={{
            orient: 'bottom',
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'transportation',
            legendOffset: 36,
            legendPosition: 'middle'
          }}
          axisLeft={{
            orient: 'left',
            tickSize: 5,
            tickPadding: 5,
            tickRotation: 0,
            legend: 'count',
            legendOffset: -40,
            legendPosition: 'middle'
          }}
          lineWidth={4}
          enableGridX={false}
          enableGridY={false}
          enablePoints={false}
          pointSize={10}
          pointColor={{ theme: 'background' }}
          pointBorderWidth={2}
          pointBorderColor={{ from: 'serieColor' }}
          pointLabel="y"
          pointLabelYOffset={-12}
          enableArea={true}
          useMesh={true}
          legends={[]}
        />
      </div>
  )
}

export default LineGraph
