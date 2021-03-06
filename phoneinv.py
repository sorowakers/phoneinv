import re, urllib2, sys
#import openpyxl
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.styles import Font
from netaddr import *
from multiprocessing.pool import ThreadPool


#--------------------------------------------------------------------
# phoneinformation()
#     This function take ip Address and return IP Phone Information
#--------------------------------------------------------------------
def phoneinformation(ip_address):

    document = "/DeviceInformationX"
    url = "http://"+ip_address+document
    try:
        html = urllib2.urlopen(url).read()
    except:
        return None
    else:    
        MA = re.findall('MACAddress\>([A-Z0-9]+)',html,flags=re.IGNORECASE)
        if len(MA) == 0:
            MA = ["N/A"]
        HN = re.findall('HostName\>([A-Z0-9]+)',html,flags=re.IGNORECASE)
        if len(HN) == 0:
            MA = ["N/A"]
        MN = re.findall('modelNumber\>([A-Z0-9]+\-[A-Z0-9]+)',html,flags=re.IGNORECASE)
        if len(MN) == 0:
            MN = ["N/A"]
        SN = re.findall('serialNumber\>([A-Z0-9]+)',html,flags=re.IGNORECASE)
        if len(SN) == 0:
            SN = ["N/A"]
        DN = re.findall('phoneDN\>([0-9]+)',html)
        if len(DN) == 0:
            DN = ["N/A"]
        
        output = (ip_address, DN[0], MA[0], HN[0], SN[0], MN[0])
    
        return output

    
#--------------------------------------------------------------------
# usage()
#     This function print usage
#--------------------------------------------------------------------
def usage():
    print "\nUsage:"
    print "\tphoneinv.exe -s x.x.x.x/y"
    print "\tx.x.x.x is Network Adress and y is Subnet Mask"
    print "\tFor single host use /32 as Mask"
    print "\nOR"
    print "\nUsage:"
    print "\tphoneinv.exe -o inputfile"
    print "\tinputfile is file text containing list of ip addresses"
        

#--------------------------------------------------------------------
# main()
#     This is a main function
#--------------------------------------------------------------------        
def main():

    try:
        if sys.argv[1]=="-s":
            subnet = IPNetwork(sys.argv[2])
            #Use netaddr library to parse IP Address subnet and return list of IP Address
            ip_list_temp = list(subnet)
            #delete network and broadcast address for non /32
            output_file = "ip_phone_list_"+str(ip_list_temp[0])+".xlsx"
            if len(ip_list_temp) > 1 :
                broadcast = len(ip_list_temp)-1
                del ip_list_temp[broadcast]
                del ip_list_temp[0]
            ip_list = list()
            for ip in ip_list_temp:
                ip_list.append(str(ip))
            
    
        if sys.argv[1]=="-o":
            fh = open(sys.argv[2])
            ip_list = fh.read().splitlines()
            output_file = "ip_phone_list_"+str(ip_list[0])+".xlsx"
            
    except:
        usage()
        sys.exit()
    
    #Formatting Excel Output
    wb = Workbook()
    ws1 = wb.active
    ws1.title = "IP Phone Data"
    fontObj1 = Font(name='Calibri', size=11, bold=True)
    ws1['A1'] = 'IP Address'
    ws1['A1'].font = fontObj1
    ws1['B1'] = 'Number'
    ws1['B1'].font = fontObj1
    ws1['C1'] = 'MAC Address'
    ws1['C1'].font = fontObj1
    ws1['D1'] = 'Host Name'
    ws1['D1'].font = fontObj1
    ws1['E1'] = 'Serial Number'
    ws1['E1'].font = fontObj1
    ws1['F1'] = 'Model'
    ws1['F1'].font = fontObj1
    ws1.column_dimensions["A"].width = 13.0
    ws1.column_dimensions["C"].width = 15.0
    ws1.column_dimensions["D"].width = 18.0
    ws1.column_dimensions["E"].width = 14.0
    ws1.column_dimensions["F"].width = 9.0

    print "IP Address\t Number\t MAC Address\t Host Name\t Serial Number\t Model"

    #multithreading process
    results = ThreadPool(100).imap_unordered(phoneinformation, ip_list)

    for html in results:
        if html is None:
            continue
        else:
            print '\t'.join(html)
            ws1.append(html)
    
    wb.save(filename = output_file)
    print "Output file is saved in",output_file

if __name__ == "__main__":
    main()
    #try:
    #    main()
    #except:
    #    usage()