# standard
import re
import getpass, sys, logging
from optparse import OptionParser

# related
from eventlet import api

# pyogp
from pyogp.lib.client.agent import Agent
from pyogp.lib.client.region import Region
from pyogp.lib.client.settings import Settings
from pyogp.lib.client.enums import AssetType
from pyogp.lib.base.datatypes import UUID

# pyogp messaging
from pyogp.lib.base.message.message import Message, Block


log = logging.getLogger('map_item_request')

def login():
    """ login an to a login endpoint """ 

    parser = OptionParser(usage="usage: %prog [options] firstname lastname minx maxx miny maxy")

    logger = logging.getLogger("client.example")

    parser.add_option("-l", "--loginuri", dest="loginuri", default="https://login.agni.lindenlab.com/cgi-bin/login.cgi",
                      help="specified the target loginuri")
    parser.add_option("-r", "--region", dest="region", default=None,
                      help="specifies the region (regionname/x/y/z) to connect to")
    parser.add_option("-q", "--quiet", dest="quiet", default=False, action="store_true",
                    help="log warnings and above (default is debug)")
    parser.add_option("-d", "--verbose", dest="verbose", default=False, action="store_true",
                    help="log info and above (default is debug)")
    parser.add_option("-p", "--password", dest="password", default=None,
                      help="specifies password instead of being prompted for one")

    parser.add_option("-m", "--message", dest="message", default=None,
                      help="The message to chat")

    (options, args) = parser.parse_args()

    if len(args) != 6:
        parser.error("Expected 6 arguments")

    (firstname, lastname, minx, maxx, miny, maxy) = args
    minx, maxx, miny, maxy = int(minx), int(maxx), int(miny), int(maxy)
               
    console = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)-30s%(name)-30s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

        # setting the level for the handler above seems to be a no-op
        # it needs to be set for the logger, here the root logger
        # otherwise it is NOTSET(=0) which means to log nothing.
    if options.verbose:
        logging.getLogger('').setLevel(logging.INFO)
    elif options.quiet:
        logging.getLogger('').setLevel(logging.WARNING)
    else:
        logging.getLogger('').setLevel(logging.DEBUG)

    # example from a pure agent perspective

    #grab a password!
    if options.password:
        password = options.password
    else:
        password = getpass.getpass()

    # prep instance settings
    settings = Settings()

    settings.ENABLE_INVENTORY_MANAGEMENT = False
    settings.ENABLE_COMMUNICATIONS_TRACKING = False
    settings.ENABLE_OBJECT_TRACKING = False
    settings.ENABLE_UDP_LOGGING =True
    settings.ENABLE_EQ_LOGGING = True
    settings.ENABLE_CAPS_LOGGING = True
    settings.MULTIPLE_SIM_CONNECTIONS = False

    #First, initialize the agent
    client = Agent(settings)

    # Now let's log it in
    api.spawn(client.login, options.loginuri, firstname, lastname, password, start_location = options.region, connect_region = True)

    # wait for the agent to connect to it's region
    while client.connected == False:
        api.sleep(0)

    while client.region.connected == False:
        api.sleep(0)


    def got_region(region):
        print "%s (%d, %d)" % (region['name'], region['x'], region['y'])

    client.map_service.request_block(minx, maxx, miny, maxy, got_region)
        
    while client.running:
        api.sleep(0)


                    

def main():
    return login()    

if __name__=="__main__":
    main()

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2010&license=apachev2$

Copyright 2010, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

