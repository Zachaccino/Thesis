import React from 'react'
import { ResponsiveLine } from '@nivo/line'
import WindowDimensions from './WindowDimensions'


function LineGraph(props) {
  return (
    <div style={{ height: 300 }}>
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
          legend: 'Seconds before now',
          legendOffset: 36,
          legendPosition: 'middle'
        }}
        axisLeft={{
          orient: 'left',
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: props.yLabel,
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
        animate={false}
        legends={[
          {
            anchor: 'bottom-right',
            direction: 'row',
            justify: false,
            translateX: 0,
            translateY: 45,
            itemsSpacing: 0,
            itemDirection: 'left-to-right',
            itemWidth: 80,
            itemHeight: 20,
            itemOpacity: 0.75,
            symbolSize: 12,
            symbolShape: 'circle',
            symbolBorderColor: 'rgba(0, 0, 0, .5)',
            effects: [
            
            ]
          }
        ]}
      />
    </div>
  )
}

export default LineGraph
