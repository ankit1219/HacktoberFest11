
########################################################################################################################
#
#TOPOLOGY :
# 				  _____________      
#  				 |             |     
# 				 |             |     
#       ---------|             |----------
#  				 |UUT1(FX2)    |    
#|               |             |
#  				 |             |     
# 				 |_____________|     
# 
# This script covers N3548 does not display all SPAN sessions in SPAN drop output:--
#
#  topology requirement :- 1 FX2 switch
#                         
#    					   
########################################################################################################################



from ats import tcl
from ats import aetest
from ats.log.utils import banner
import time
import logging
import os
import sys
import re
import pdb
import json
import pprint
import socket
import struct
import inspect
#########################################
# pyATS imports
from pyats.topology import loader
#from pyats import aetest
#from ats.async import pcall
from pyats.async_ import pcall
from pyats.async_ import Pcall
#from unicon.eal.dialogs import Statement, Dialog
#from unicon.eal.expect import Spawn, TimeoutError
#import nxos.lib.nxos.util as util
#import ctsPortRoutines
#import pexpect
#import nxos.lib.common.topo as topo
##########################################
from ats import aetest
from ats.log.utils import banner
from ats.datastructures.logic import Not, And, Or
from ats.easypy import run
from ats.log.utils import banner
import parsergen
from unicon.eal.expect import Spawn
from unicon.eal.dialogs import Statement, Dialog
from unicon.eal.expect import Spawn, TimeoutError
from genie.conf import Genie
import pdb
import sys
import json
import os
########################################

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
global uut1           
global uut1_intf1, uut1_intf2



class ForkedPdb(pdb.Pdb):
    '''A Pdb subclass that may be used
    from a forked multiprocessing child1
    '''
    def interaction(self, *args, **kwargs):
        _stdin = sys.stdin
        try:
            sys.stdin = open('/dev/stdin')
            pdb.Pdb.interaction(self, *args, **kwargs)
        finally:
            sys.stdin = _stdin

################################################################################
####                       COMMON SETUP SECTION                             ####
################################################################################

class common_setup(aetest.CommonSetup):

    @aetest.subsection
    def span_topo_parse(self,testscript,testbed,R1):

        global uut1

        global uut1_ixia_intf1,uut1_ixia_intf2,uut1_ixia_intf3,uut1_ixia_intf4
        
        global custom
        global device1
        
        uut1 = testbed.devices[R1]
        uut1_ixia_intf1 = testbed.devices[R1].interfaces['uut1_ixia_intf1']
        testscript.parameters['uut1_ixia_intf1'] = uut1_ixia_intf1
        testscript.parameters['uut1_ixia_intf1'].name = testscript.parameters['uut1_ixia_intf1'].intf
        
        uut1_ixia_intf2 = testbed.devices[R1].interfaces['uut1_ixia_intf2']
        testscript.parameters['uut1_ixia_intf2'] = uut1_ixia_intf2
        testscript.parameters['uut1_ixia_intf2'].name = testscript.parameters['uut1_ixia_intf2'].intf
        
        uut1_ixia_intf3 = testbed.devices[R1].interfaces['uut1_ixia_intf3']
        testscript.parameters['uut1_ixia_intf3'] = uut1_ixia_intf3
        testscript.parameters['uut1_ixia_intf3'].name = testscript.parameters['uut1_ixia_intf3'].intf
        
        uut1_ixia_intf4 = testbed.devices[R1].interfaces['uut1_ixia_intf4']
        testscript.parameters['uut1_ixia_intf4'] = uut1_ixia_intf4
        testscript.parameters['uut1_ixia_intf4'].name = testscript.parameters['uut1_ixia_intf4'].intf
        
        uut1_ixia_intf1=uut1_ixia_intf1.intf
        uut1_ixia_intf2=uut1_ixia_intf2.intf
        uut1_ixia_intf3=uut1_ixia_intf3.intf
        uut1_ixia_intf4=uut1_ixia_intf4.intf
        
        log.info("uut1_ixia_intf1=%s" % uut1_ixia_intf1)
        log.info("uut1_ixia_intf2=%s" % uut1_ixia_intf2)
        log.info("uut1_ixia_intf3=%s" % uut1_ixia_intf3)
        log.info("uut1_ixia_intf4=%s" % uut1_ixia_intf4)
    @aetest.subsection
    def connect_to_devices(self, testscript, testbed, R1):
        
        log.info("\n************ Connecting to Device:%s ************" % uut1.name)
        try:
            uut1.connect()
            log.info("Connection to %s Successful..." % uut1.name)
        except Exception as e:
            log.info("Connection to %s Unsuccessful " \
                        "Exiting error:%s" % (uut1.name, e))
            self.failed(goto=['exit'])

            
   ################################################################################################################# 
    #ForkedPdb().set_trace()
class pvlan_span(aetest.Testcase):
    """Checking SPAN sessions in SPAN drop output"""
    @aetest.test 
    def configure_Monitor_Session(self,testscript, testbed,R1):
        global uut1_ixia_intf1,uut1_ixia_intf2,uut1_ixia_intf3,uut1_ixia_intf4
        """Configure Monitor Session"""
        
        log.info("Enable switchport monitor at interface")
        cmd = """int %s
                 switchport
                 switchport monitor"""%(uut1_ixia_intf2)
        uut1.configure(cmd)
        
        cmd = """int %s
                 switchport
                 switchport monitor"""%(uut1_ixia_intf4)
        uut1.configure(cmd)
        
        log.info("Create Monitor Session")
        cmd = """monitor session 1
                 source interface %s both
                 destination interface %s
                 no shut"""%(uut1_ixia_intf1,uut1_ixia_intf2)
        uut1.configure(cmd)
        
        log.info("Create Monitor Session")
        cmd = """monitor session 2
                 source interface %s both
                 destination interface %s
                 no shut"""%(uut1_ixia_intf3,uut1_ixia_intf4)
        uut1.configure(cmd)

        cmd ="""show monitor session all drops"""
        op=uut1.execute(cmd)
        if "Session Number: 2" in op:
            self.passed("SPAN session 2 is coming")
        else:
            self.failed("SPAN session 2 is missing")
        
########################################################################################################################
################################################################################
####                       COMMON CLEANUP SECTION                           ####
################################################################################


class common_cleanup(aetest.CommonCleanup):

    @aetest.subsection
    def remove_configuration(self,testbed,testscript):
    
        #############################################################
        #clean up the session, release the ports reserved and cleanup the dbfile
        ############################################################
        time.sleep(30)
        # ForkedPdb().set_trace()
        cmd = """ default interface %s,%s,%s,%s
                no monitor session 1
                no monitor session 2"""%(uut1_ixia_intf1,uut1_ixia_intf2,uut1_ixia_intf3,uut1_ixia_intf4)
        uut1.configure(cmd)

if __name__ == '__main__': # pragma: no cover
    import argparse
    from ats import topology
    parser = argparse.ArgumentParser(description='standalone parser')
    parser.add_argument('--testbed', dest='testbed', type=topology.loader.load)
    parser.add_argument('--R1', dest='R1', type=str)
    parser.add_argument('--mode',dest = 'mode',type = str)
    args = parser.parse_known_args()[0]
    aetest.main(testbed=args.testbed,
                R1_name=args.R1,
                mode = args.mode,
                pdb = True)
