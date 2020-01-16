require 'net/http'
require 'uri'
require 'date'

def get_time()
  return DateTime.now.strftime('%s').to_i
end

start = get_time()
timeout = 30 # seconds

uri = URI.parse('http://127.0.0.1:15000/ready')
while ((get_time() - start) < timeout)
  begin
    response = Net::HTTP.get_response(uri)
    if response.code.to_i == 200
      puts "Istio proxy is ready!"
      exit(0)
    else
      puts "Istio proxy is up, but not ready"
    end
  rescue Errno::ECONNREFUSED
    puts 'Waiting for Istio proxy to come up'
  end
  sleep(1)
end
raise StandardError.new "Timed out waiting for Istio proxy to come up"
