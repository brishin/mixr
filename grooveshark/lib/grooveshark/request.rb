module Grooveshark
  module Request
    API_BASE        = 'cowbell.grooveshark.com'
    UUID            = 'C6842191-CE14-400C-AC03-5560A5706465'
    CLIENT          = 'htmlshark'
    CLIENT_REV      = '20120312'
    COUNTRY         = {"ID"=>223,"CC1"=>0,"CC2"=>0,"CC3"=>0,"CC4"=>1073741824,"DMA"=>501,"IPR"=>0}
    TOKEN_TTL       = 120 # 2 minutes
    
    # Client overrides for different methods
    METHOD_CLIENTS = {
      'getStreamKeyFromSongIDEx' => 'jsqueue' 
    }
    
    # Perform API request
    def request(method, params={}, secure=false)
      refresh_token if @comm_token
      
      agent = METHOD_CLIENTS.key?(method) ? METHOD_CLIENTS[method] : CLIENT
      url = "#{secure ? 'https' : 'http'}://#{API_BASE}/more.php?#{method}"
      body = {
        'header' => {
          'session' => @session,
          'uuid' => UUID,
          'client' => agent,
          'clientRevision' => CLIENT_REV,
          'country' => COUNTRY
        },
        'method' => method,
        'parameters' => params
      }
      body['header']['token'] = create_token(method) if @comm_token
      
      begin
        data = RestClient.post(
          url, body.to_json,
          :content_type => :json,
          :accept => :json,
          :cookie => "PHPSESSID=#{@session}"
        )
      rescue Exception => ex
        raise GeneralError    # Need define error handling
      end
      
      data = JSON.parse(data)
      data = data.normalize if data.kind_of?(Hash)
      
      if data.key?('fault')
        raise ApiError.new(data['fault'])
      else
        data['result']
      end
    end
    
    # Refresh communications token on ttl
    def refresh_token
      get_comm_token if Time.now.to_i - @comm_token_ttl > TOKEN_TTL
    end
  end
end