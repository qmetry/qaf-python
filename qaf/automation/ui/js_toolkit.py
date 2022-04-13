GLOBAL_WAIT_CONDITION = "return  (((typeof dojo === 'undefined') || " \
                        "(dojo.io.XMLHTTPTransport.inFlight.length==0))) && " \
                        "(((typeof Ext === 'undefined') || " \
                        "(Ext.Ajax.isLoading()==false))) && " \
                        "(((typeof jQuery === 'undefined') || " \
                        "(jQuery.active==0))) && " \
                        "(((typeof YAHOO === 'undefined') || " \
                        "(YAHOO.util.Connect.isCallInProgress==false))) && " \
                        "(((typeof PHP_JS === 'undefined') || " \
                        "(PHP_JS.resourceIdCounter==0))) && " \
                        "(((typeof Ajax === 'undefined') || " \
                        "(Ajax.activeRequestCount==0)));"
