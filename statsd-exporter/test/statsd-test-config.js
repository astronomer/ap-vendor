{
  backends: [ "./backends/repeater" ],
  debug: true,
  repeater: [ { host: 'statsd-exporter', port: 9125 }]
}
