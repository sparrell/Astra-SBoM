## Copyright (c) 2019 AT&T Intellectual Property. All rights reserved.

import sys
from load_db import load_graph
from sbom_helpers import mypprint
from load_db import pkg_subset
from load_db import svr_subset
from sbom_helpers import get_gdbpath
from sbom_helpers import validate_file_access
from analyze_data import bar_image

## For given day graph, summarize state of non-suppressed, non-multiversion, cve
##

## input one environmental variables: GDBPATH
##    GDBPATH is path to graphdb directory

## initialize from env
gdbpath = get_gdbpath()

if( len(sys.argv) != 2 ):
   print("There should be one argument, date of GraphDB")
   exit()
else:
   d = sys.argv[1]
   gfile = get_gdbpath() + d + '.gdb'

## validate the file exists
validate_file_access([gfile])

graphdata = load_graph(gfile)

## dictionary to hold the data
cvebins = {}

## First make a list of all cve nodes
##    i.e. all nodes connected to "type_cve"
cves = graphdata.neighbors("type_cve")

## bin cve's by cvss score
cve10 = [] # CVE's with cvss=10
cve7 = []  # CVE's with cvss<10,>=7
cve5 = []  # CVE's with cvss<7,>=5
cve0 = []  # CVE's with cvss<5,>=0

for cve in cves:
  ## put cve in bin
  cvss = graphdata.nodes[cve]['cvss']
  if(cvss == 10.):
      cve10.append(cve)
  elif(cvss >= 7.0):
      cve7.append(cve)
  elif(cvss >= 5.0):
      cve5.append(cve)
  else:
      cve0.append(cve)

## find all packages for each bin
pkg10 = pkg_subset(graphdata,cve10)
pkg7 = pkg_subset(graphdata,cve7)
pkg5 = pkg_subset(graphdata,cve5)
pkg0 = pkg_subset(graphdata,cve0)

## find all servers for each bin
svr10 = svr_subset(graphdata, pkg10)
svr7 = svr_subset(graphdata, pkg7)
## make the lists unique
svr7s = [ item for item in svr7 if item not in svr10]
svr5 = svr_subset(graphdata, pkg5)
svr5s = [ item for item in svr5 if item not in (svr10 + svr7s)]
svr0 = svr_subset(graphdata, pkg0)
svr0s = [ item for item in svr0 if item not in (svr10 + svr7s + svr5s)]

cvebins['1. Servers with Worst CVSS=10'] = len(svr10)
cvebins['2a. Servers with Critical 7 <= CVSS <10'] = len(svr7)
cvebins['2b.        Unique Servers 7 <= CVSS <10'] = len(svr7s)
cvebins['3a. Servers with Medium 5 <= CVSS <7'] = len(svr5)
cvebins['3b.      Unique Servers 5 <= CVSS <7'] = len(svr5s)
cvebins['4a. Servers with Low 0 <= CVSS <5'] = len(svr0)
cvebins['4b.        Unique Servers CVSS <5'] = len(svr0s)

mypprint(cvebins)

## print 3 random servers in each class
print('up to 3 random servers with CVSS=10')
mypprint(svr10[:3])
print('up to 3 random servers with 7<=CVSS<10')
mypprint(svr7s[:3])
print('up to 3 random servers with 5<=CVSS<7')
mypprint(svr5s[:3])
print('up to 3 random servers with CVSS<5')
mypprint(svr0s[:3])
