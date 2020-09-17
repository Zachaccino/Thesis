import React from 'react'
import { ResponsiveLine } from '@nivo/line'
import WindowDimensions from './WindowDimensions'

const lineGraphSettings = {
  theme: {
    fontSize: 17,
    axis: {
      legend: {
        text: {
          fontSize: 17
        }
      }
    }
  }
}

function LineGraph(props) {
  return (
    <div style={{ height: 350 }}>
      <ResponsiveLine
        data={props.data}
        margin={{ top: 10, right: 15, bottom: 40, left: 70 }}
        xScale={{ type: 'point' }}
        yScale={{ type: 'linear', min: -5, max: props.max, stacked: false, reverse: false }}
        axisTop={null}
        axisRight={null}
        axisBottom={{
          orient: 'bottom',
          tickSize: 0,
          tickPadding: 5,
          tickRotation: 90,
          legend: 'Time Delta',
          legendOffset: 30,
          legendPosition: 'middle',
          format: () => null,
        }}
        axisLeft={{
          orient: 'left',
          tickSize: 5,
          tickPadding: 5,
          tickRotation: 0,
          legend: props.yLabel,
          legendOffset: -60,
          legendPosition: 'middle'
        }}
        lineWidth={2}
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
        theme={lineGraphSettings.theme}
        legends={[
          {
            anchor: 'bottom-right',
            direction: 'row',
            justify: false,
            translateX: -15,
            translateY: 38,
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
