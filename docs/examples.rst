Examples
=========

Extending The Service
---------------------

Creating XML-RPC Methods
````````````````````````
There are a few rules to remember when making new XML-RPC methods.
   - All exposed methods are in views.py
   - If you import functions you don't want exposed rename them to start with a _
   - Always follow the reST documentation in the docstring. When a user hits the service with a browser it will be rendered as help.
   - The format for XML-RPC methods is grouper__method_name(). For instance, the function called test__return_only_true will be mapped into test.return_only_true.
   - The first variable to any function should always be auth, a tuple of username and password to authenticate with as the function will get wrapped with an authentication check at register time.

Here is an example XML-RPC method that will register as test.my_remote_method.::

   def test__my_remote_method(auth):
       """
       Just returns True.

       :Parameters:
          - `auth`: the username, password tuple to authenticate with.
       """
       return True


Working With Func Through Parallel Python
`````````````````````````````````````````
Since Func requires root to access the library, and it's not a good idea to run web services as root, a special Parallel Python process runs as root with access to func. When using func you can go through the FuncDispatcher. For example, to run the :program:`pupped --test` command on 10.10.10.10 you would do the following inside of an XML-RPC view::

    FUNC_JOB_SERVERS = ("func.overlord.client", 'logging')

    ...

    dispatcher = _helpers.FuncPPDispatcher(host, 'command.run',
        FUNC_JOB_SERVER_MODULES, settings.PIPBOY_JOB_SERVERS)
    return dispatcher('puppetd --test')

The results you will get should look like this::

    [False, {'value': 'Can\'t find any minions matching "127.0.0.1". '}]

or::

    [True, {'value': 0}]

*Note*: the first item is always success/fail while the second item could be just about anything!


Interfacing With The Service
----------------------------

Invoking XML-RPC Methods from Python
````````````````````````````````````
It's very simple to invoke the XML-RPC methods in Python. All you need
is access to the service and access to the jkmanage url. By using
SimpleProxy you can get and send requests quickly and simply.::

   #!/usr/bin/env python

   from xmlrpclib import ServerProxy

   # Set up a server proxy to the service
   s = ServerProxy('http://127.0.0.1:8080')

   # It's nice to reuse these two things ...
   auth = ('admin', 'password')
   url = 'http://proxyjava01.web.qa.ext.intdev.redhat.com/jkmanage?mime=xml'

   # Print out the results of modjk's get_all_workers method
   print s.modjk.get_all_workers(auth, url)

The results come back like so::

   [{'balancer': 'queueAdmin',
     'host': 'esbjava02.web.qa.ext.intdev.redhat.com',
     'name': '5c5e715c-svc'},
    {'balancer': 'queueAdmin',
     'host': 'esbjava01.web.qa.ext.intdev.redhat.com',
     'name': '6807bb3f-svc'},
    {'balancer': 'wsvc',
     'host': 'java02.web.qa.ext.intdev.redhat.com',
     'name': 'a8159895-svc'},
    {'balancer': 'wsvc',
     'host': 'java01.web.qa.ext.intdev.redhat.com',
     'name': 'b917f0a9-svc'},
    {'balancer': 'wapps_sticky',
    'host': 'java02.web.qa.ext.intdev.redhat.com',
     'name': 'a8159895'},
    {'balancer': 'wapps_sticky',
     'host': 'java01.web.qa.ext.intdev.redhat.com',
     'name': 'b917f0a9'},
    {'balancer': 'svc',
    'host': 'java02.web.qa.ext.intdev.redhat.com',
     'name': 'a8159895-svc'},
    {'balancer': 'svc',
     'host': 'java01.web.qa.ext.intdev.redhat.com',
     'name': 'b917f0a9-svc'},
    {'balancer': 'kbase',
     'host': 'kbase01.web.qa.ext.intdev.redhat.com',
     'name': '36531e8d'},
    {'balancer': 'kbase',
     'host': 'kbase02.web.qa.ext.intdev.redhat.com',
     'name': 'fdafd6e4'}]


Invoking XML-RPC Methods from Ruby
``````````````````````````````````
It's also simple to invoke XML-RPC methods in Ruby.::

   #!/usr/bin/env ruby

   require "xmlrpc/client"

   # Setup a client connection proxy
   server = XMLRPC::Client.new( "127.0.0.1", "/", 8080 )

   # It's nice to reuse these two things
   auth = ['admin', 'admin']
   url = 'http://proxyjava01.web.qa.ext.intdev.redhat.com/jkmanage?mime=xml'

   # Print out the results of modjk's get_all_workers method
   puts server.call( "modjk.get_all_workers", auth, url )

The results look like so::

   name5c5e715c-svcbalancerqueueAdminhostesbjava02.web.qa.ext.intdev.redhat.com
   name6807bb3f-svcbalancerqueueAdminhostesbjava01.web.qa.ext.intdev.redhat.com
   namea8159895-svcbalancerwsvchostjava02.web.qa.ext.intdev.redhat.com
   nameb917f0a9-svcbalancerwsvchostjava01.web.qa.ext.intdev.redhat.com
   namea8159895balancerwapps_stickyhostjava02.web.qa.ext.intdev.redhat.com
   nameb917f0a9balancerwapps_stickyhostjava01.web.qa.ext.intdev.redhat.com
   namea8159895-svcbalancersvchostjava02.web.qa.ext.intdev.redhat.com
   nameb917f0a9-svcbalancersvchostjava01.web.qa.ext.intdev.redhat.com
   name36531e8dbalancerkbasehostkbase01.web.qa.ext.intdev.redhat.com
   namefdafd6e4balancerkbasehostkbase02.web.qa.ext.intdev.redhat.com

or like this in it's structured form::

   [{"name"=>"5c5e715c-svc", "balancer"=>"queueAdmin", "host"=>"esbjava02.web.qa.ext.intdev.redhat.com"},
    {"name"=>"6807bb3f-svc", "balancer"=>"queueAdmin", "host"=>"esbjava01.web.qa.ext.intdev.redhat.com"}, 
    {"name"=>"a8159895-svc", "balancer"=>"wsvc", "host"=>"java02.web.qa.ext.intdev.redhat.com"},
    {"name"=>"b917f0a9-svc", "balancer"=>"wsvc", "host"=>"java01.web.qa.ext.intdev.redhat.com"},
    {"name"=>"a8159895", "balancer"=>"wapps_sticky", "host"=>"java02.web.qa.ext.intdev.redhat.com"},
    {"name"=>"b917f0a9", "balancer"=>"wapps_sticky", "host"=>"java01.web.qa.ext.intdev.redhat.com"},
    {"name"=>"a8159895-svc", "balancer"=>"svc", "host"=>"java02.web.qa.ext.intdev.redhat.com"},
    {"name"=>"b917f0a9-svc", "balancer"=>"svc", "host"=>"java01.web.qa.ext.intdev.redhat.com"},
    {"name"=>"36531e8d", "balancer"=>"kbase", "host"=>"kbase01.web.qa.ext.intdev.redhat.com"},
    {"name"=>"fdafd6e4", "balancer"=>"kbase", "host"=>"kbase02.web.qa.ext.intdev.redhat.com"}]


Invoking XML-RPC Methods from Java
``````````````````````````````````

It's a little cumbersome but it is not too bad. Here is an example using `ws-xmlrpc <http://ws.apache.org/xmlrpc/>`_::

   import java.net.URL;
   import java.net.MalformedURLException;
   import org.apache.xmlrpc.client.XmlRpcClient;
   import org.apache.xmlrpc.client.XmlRpcClientConfigImpl;
   import org.apache.xmlrpc.XmlRpcException;


   class ServiceClient {

       public static void main(String args[]) {
           XmlRpcClientConfigImpl config = new XmlRpcClientConfigImpl();
           try {
               config.setServerURL(new URL("http://127.0.0.1:8080/"));
           } catch (MalformedURLException e) {
               System.err.println(e);
               System.exit(1);
           }

           XmlRpcClient client = new XmlRpcClient();
           client.setConfig(config);
           try {
               Object[] params = new Object[]{new Object[]{"admin", "admin"}};
               System.out.println((String) client.execute("health.ping", params));
           } catch (XmlRpcException e) {
               System.err.println(e);
               System.exit(2);
           }
       }
   }


To compile the example you will need somehting like this::

   javac -cp xmlrpc-3.1/lib/commons-logging-1.1.jar:xmlrpc-3.1/lib/ws-commons-util-1.0.2.jar:xmlrpc-3.1/lib/xmlrpc-client-3.1.jar:xmlrpc-3.1/lib/xmlrpc-common-3.1.jar:xmlrpc-3.1/lib/xmlrpc-server-3.1.jar:. ServiceClient.java

You can then run it like so::

   java -cp xmlrpc-3.1/lib/commons-logging-1.1.jar:xmlrpc-3.1/lib/ws-commons-util-1.0.2.jar:xmlrpc-3.1/lib/xmlrpc-client-3.1.jar:xmlrpc-3.1/lib/xmlrpc-common-3.1.jar:xmlrpc-3.1/lib/xmlrpc-server-3.1.jar:. ServiceClient



Invoking XML-RPC Methods from Perl
``````````````````````````````````

You can interface with the service in Perl using the Fonrtier::Client class.

::

   #!/usr/bin/env perl 

   use strict;
   use warnings;
   use Data::Dumper;
   use Frontier::Client;

   my $url  = "http://127.0.0.1:8080/";
   my @args = (['admin', 'admin'],
               'http://proxyjava01.web.qa.ext.intdev.redhat.com/jkmanage?mime=xml');

   my $client = Frontier::Client->new( url   => $url,
                                       debug => 0);

   print Dumper($client->call('modjk.get_all_workers', @args));


The results come back like so::

   $VAR1 = [
             {
               'balancer' => 'queueAdmin',
               'name' => '5c5e715c-svc',
               'host' => 'esbjava02.web.qa.ext.intdev.redhat.com'
             },
             {
               'balancer' => 'queueAdmin',
               'name' => '6807bb3f-svc',
               'host' => 'esbjava01.web.qa.ext.intdev.redhat.com'
             },
            {
               'balancer' => 'wsvc',
               'name' => 'a8159895-svc',
               'host' => 'java02.web.qa.ext.intdev.redhat.com'
             },
             {
               'balancer' => 'wsvc',
               'name' => 'b917f0a9-svc',
               'host' => 'java01.web.qa.ext.intdev.redhat.com'
             },
             {
               'balancer' => 'wapps_sticky',
               'name' => 'a8159895',
               'host' => 'java02.web.qa.ext.intdev.redhat.com'
             },
             {
               'balancer' => 'wapps_sticky',
               'name' => 'b917f0a9',
               'host' => 'java01.web.qa.ext.intdev.redhat.com'
             },
             {
               'balancer' => 'svc',
               'name' => 'a8159895-svc',
               'host' => 'java02.web.qa.ext.intdev.redhat.com'
             },
             {
               'balancer' => 'svc',
               'name' => 'b917f0a9-svc',
               'host' => 'java01.web.qa.ext.intdev.redhat.com'
             },
             {
               'balancer' => 'kbase',
               'name' => '36531e8d',
               'host' => 'kbase01.web.qa.ext.intdev.redhat.com'
             },
             {
               'balancer' => 'kbase',
               'name' => 'fdafd6e4',
               'host' => 'kbase02.web.qa.ext.intdev.redhat.com'
             }
   ];
