Facter.add("server_class") do
  setcode do
      %x{ . /etc/bbc.conf && echo ${SERVER_CLASS} }.chomp
  end
end
Facter.add("server_env") do
  setcode do
      %x{ . /etc/bbc.conf && echo ${SERVER_ENV} }.chomp
  end
end
Facter.add("server_datacentre") do
  setcode do
      %x{ . /etc/bbc.conf && echo ${SERVER_DATACENTRE} }.chomp
  end
end

begin
   if Facter.ipaddress_eth0
      Facter.add("back_ip")  do
         setcode do
            Facter.ipaddress_eth0
         end
      end
   end
rescue
end

begin
   if Facter.ipaddress_eth1
      Facter.add("front_ip")  do
         setcode do
            Facter.ipaddress_eth1
         end
      end
   end
rescue
end

begin
   Facter.add('redhat_release') do
      # should also include CentOS
      confine :operatingsystem => :RedHat
      setcode do
         if FileTest.exists?('/etc/redhat-release')
            txt = File.read('/etc/redhat-release')
            if txt =~ /release (\d+\.\d+)/
               # return the bit in brackets
               $1
            end
         end
      end
   end
rescue
end
