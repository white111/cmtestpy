#!/usr/bin/python
################################################################################
#
# Module:      Logs.py
#
# Author:      Paul Tindle ( mailto:Paul@Tindle.org )
#			 Joe White( mailto:joe@stoke.com )
#
# Descr:      Subs for log files operations
#
# Version:    (See below) $Id$
#
# Changes:    Conversion to Python from Perl 050917 JSW
#
# Still ToDo:
#            Convert to logging python package in python
#
# License:   This software is subject to and may be distributed under the
#            terms of the GNU General Public License as described in the
#            file License.html found in this or a parent directory.
#            Forward any and all validated updates to Paul@Tindle.org
#
#            Copyright (c) 1993 - 2005 Paul Tindle. All rights reserved.
#            Copyright (c) 2005-2008 Stoke. All rights reserved.
#            Copyright (c) 2017 Joe White. All rights reserved.
#
################################################################################
VER= 'v0.1 5/9/2017'; # Conversion to Python from Perl 050917 JSW
CVS_VER = ' [ CVS: $Id$ ]';
global CMtestVersion
if "CMtestVersion" not in globals() : CMtestVersion={}
CMtestVersion['Logs'] = VER + CVS_VER
#_____________________________________________________________________________
import os.path
from os import listdir
from os.path import isfile, join
import time
import sys
import Globals
import Util
import Logs
import Stats
import FileOp
import re

#What to use here for python?
#use Time::HiRes qw(gettimeofday tv_interval);
#use Term::ANSIColor;
#__________________________________________________________________________
def Arc_Logs (Path, Label) :
     """Alternative to Rotate_Logs, creates a folder based on the creation date of 
     the first file arc'd, and moves any files(not dirs) found to the new sub-dir.
     Move = mv
     Delete = rm -f
     From 
     To 
     fh 
     Arc_File
     """
     Arc_File = ""
     #if Globals.OS == 'NT' : 
          #Move = 'ren'
          #Delete = 'del'

     Dir_list = os.listdir(Path)
     if Globals.Verbose : print ("Arc_Logs Dir list: %s" % Dir_list)
     if Globals.Verbose : print ("Arc_Logs Path: %s" % Path)
     for index in os.listdir(Path) :
          if re.search( "2arc2", index ) and isfile(join(Path,index)) :
               #value =  re.escape(Globals.PathSep+ r'2arc2(.*)' + Globals.PathSep)  #Need to escape the \
               #pattern = re.compile(value)
               #Arc_File = re.sub(value, "", index)  #Time Stamp for aour Arcive dir
               if Globals.Debug : print("Removing %s %s"  % (index, Arc_File) )
               try: os.remove(join(Path,index))
               except: print ("Arch_Logs unable to remove %s " % join(Path,index))
               try: 
                    Arc_File = replace("2arc2", "",index)
                    if Globals.Debug : print("Arc_Logs creating directory %s" % join(Path,Arc_File))
                    os.makedirs(join(Path,Arc_File))
                   
               except:
                    print("Arc_Logs failed creating directory %s" % join(Path,index))
                    
     File_Count = FileOp.File_List(Path, 1); # Don't recurse any subs
     if not File_Count : return 
     
     for index in os.listdir(Path) :
          if isfile(join(Path, index)) and not Arc_File == '' :
                    if Globals.Debug : print("Arc_Logs renaming file %s to %s" % (join(Path,index),join(Path,Arc_File)))
                    Globals.Erc = os.rename(join(Path,index), join(Path,Arc_File),index)

     if Globals.Erc : Exit (999,"Arc_Logs returned a %s" % Globals.Erc)

     return
#__________________________________________________________________________
def Get_Cfg_Recs(Date, Location, HostID, Parent_ID, SN_Masks):
     "# Called by someone with an Event rec data looking for child cfg \
     records. It requires handle <CFG> to already be open for read"

     Cfg_Recs = [];
     Rec = [];
     Buf = ''

     PrintLog ("Get_Cfg_Recs: Date=%s, Location=%s, HostID=%s, Parent_ID=%s" % Date,Location,HostID,Parent_ID %  1);
     Last_Rec = []
     Last_Rec = gBuf[0].split(r";");
     if Date < Last_Rec[1] : 
          return;  # The date we want is earlier than the last record read,
                    #   so don't bother with any more
     Done = 0
     while (not Done) :
               # <CFG>  # perl had <CFG> barewood file handel that is open 
          ###################### Stop ###########################
          CFG_line = CFG.readline().rstrip; # Read and chomp return
          CFG_Line_num = CFG.tell() # get the file line postion

          PrintLog ("Read CfgLog line: " + CFG_Line_num , 1);
          if CFG_line == None : Done = 1 
          Buf = CFG_line ;          # Save it in case we overrun the date (-> gBuf[0])
          Rec  = split( ";", CFG_line) 	    # Split the records on ;
          if Rec[0] != 2 and not Done :
               Exit(999, "Unrecognized file format for CFG record line: " + CFG_Line_num);
          elif Rec[1] < Date :   # Cfg rec is too early
               next;                     # Skip
          elif Rec[1] > Date :   # Too late, we'll stop with this record
               Done = 1               #  still loaded in gBuf[0]
          else :
               gBuf.append( CFG_Line)
               PrintLog (CFG_Line, 1);

               #0: $Type, 1: $Date, 2: $Location, $HostID, $OpID, $Parent_ID, $Slot, $PN, $SN)

     Msg = ''
     for index in gBuf :
          Rec  = split(";", index)
          SNum = Rec[8]
          if SN_Masks == 0 :
               SN_Match = SN_Masks # Assume a match if no mask list provided

          if Debug : PrintLog("SN_Match[0]=" + SN_Match,1) 
          for index2 in SN_Masks : 
               if re(r"^"+ index2, SNum ) : SN_Match = 1 

          if Debug : PrintLog("SN_Match[1]=" +SN_Match,1)

#        #!!! Still in debug ...
#        foreach ( @Exclude ) {
#            $SN_Match = 0 if $SNum =~ /^$_/;
#        }
#        &PrintLog("SN_Match[2]=$SN_Match",1) if $Debug;

          if ((Rec[2] == Location)   and
              (Rec[3] == HostID)     and
              (Rec[5] == Parent_ID)) :
               #  and
               # ($SN_Match)){

               Msg += ', ' + SNum;
               Cfg_Recs.appen(SNum)

          #, $Date, $Location, $HostID, $OpID, $Parent_ID, $Slot, $PN, $SN)

     PrintLog("Returned: " + Msg, 1);

     gBuf = Buf        # Just the last one

     return ( Cfg_Recs )

#__________________________________________________________________________
def Log_Cfg(OpID, Sys_ID, Slot, PN, SN):
     "Write a single (parent / child) record. Caller must construct \
     sequence of invocations to create all the necessary records \
     to describe the DUT"

     # Event log is a 'Type 2' record:
     # 2;Date;Location;HostID;OpID;Parent_ID;Slot;Part_No;Serial_No;
     # (NB $TimeStamp, $Location, $Host_ID and $Op_ID are global, declared in &Init_All)
     File = LogPath + r"/" + Cfg.log

     try  :
          OUT = open(File, 'r+')
          OUT.write("2;"+Stats['TimeStamp']+r";"+Location+r";"\
                    +Host_ID+r";"+Op_ID+r";"+Sys_ID+r";"+Slot+r";"+PN+r";"+SN+";\n")
     finally:
          Exit (1, File) 

     File_Close (OUT);
     return
#__________________________________________________________________________
def Log_Cfg_Record(OpID, Sys_ID, Slot, PN, SN):
     "Write a single (parent / child) record. Caller must construct \
     sequence of invocations to create all the necessary records \
     to describe the DUT"

     # Event log is a 'Type 2' record:
     # 2;Date;Location;HostID;OpID;Parent_ID;Slot;Part_No;Serial_No;
     # (NB $TimeStamp, $Location, $Host_ID and $Op_ID are global, declared in &Init_All)

     File = Tmp + r"/"+ Cfg.log           # Send to $tmp dir so we can email or export record
     try :
          OUT = open(File, 'r+')  
          OUT.write("2;"+Stats['TimeStamp']+r";"+Location+r";"\
                    +Host_ID+r";"+Op_ID+r";"+Sys_ID+r";"+Slot+r";"+PN+r";"+SN+";\n")
     finally:
          Exit (1, File) 

     File_Close (OUT);
     return
#__________________________________________________________________________

def Log_Error(Msg):
     "An error just occured, log it!"

     Globals.TestData['TOLF'] = int(time.time()) #epoch time;      # Time of Last Failure
     Globals.Errors[0] +=1
     Globals.Errors[1] +=1
     Globals.TestData['TEC'] +=1
     Globals.Stats['Result'] = 'FAIL';

     if Globals.TestData['TTF'] == '': # Only the first time
          Globals.TestData['TTF'] = Globals.TestData['TOLF'] - Globals.Stats['TimeStamp']

     Stats.Update_All;
     Util.ASCIIColor('red') 
     Print_Log (2, 'Log_Error: ' + Msg);
     #Added JSW 051906 Adding Error Messages to XML file
     Print_Out_XML_Tag("Error")
     Print_Out( '		Log_Error: ' + Msg);
     Print_Out_XML_Tag();
     Util.ASCIIColor('reset');
     if (Globals.Exit_On_Error) :
          Exit_On_Error_Count -= 1
          # THis must be Erc=0 to avoid dancing forever with $Exit
          #&Exit (0, "Exit_On_Error") if $Exit_On_Error_Count < 1;
          if (Globals.Exit_On_Error_Count < 1) :  # if Error count reached Exit
               Print_Log (2, 'Exit on too Many Errors ');
               #&Exit (0, "Exit_On_Error");
               Final()

     return (0);

#__________________________________________________________________________________
def Log_Event(OpID, PN, SN, TID, Result, Ptr):
     " Write a test event record to LogPath"

     # Note that, as of 05/12/02 the Data list is no longer passed as an arg
     # Event log is a 'Type 1' record:
     # 1;Date;Location;HostID;OpID;Part_No;Serial_No;TestID;Result;Data;LogFilePtr;
     Data  = ''            
     OpID.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     PN.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     SN.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     TID.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     Result.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     Ptr.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     #        my ($OpID, $PN, $SN, $TID, $Result, $Data, $Ptr) = @Args; ->05/12/02
     # (NB $TimeStamp, $Location, $Host_ID and $Op_ID are global, declared in &Init_All)

     File = LogPath+r"/" + Event.log
     for Key in TestData :	   
          if TestData[Key] != '': Data += Key + r"=" + TestData[Key]

     Data = Data[:-1] # Chomp last character
     try :
          OUT = open(File, 'r+')  
          OUT.write("1;"+Stats['TimeStamp']+r";"+Location+r";"\
                    +Host_ID+r";"+Op_ID+r";"+PN+r";"+SN+r";"+TID\
                       +r";"+Result+r";"+Data+r";",Ptr+";\n")
     finally:
          Exit (1, File) 

     File_Close (OUT);
     return
#__________________________________________________________________________________
def Log_Event_Record(OpID, PN, SN, TID, Result, Ptr):
     "Write a test event record to tmp path"

     # Note that, as of 05/12/02 the Data list is no longer passed as an arg
     # Event log is a 'Type 1' record:
     # 1;Date;Location;HostID;OpID;Part_No;Serial_No;TestID;Result;Data;LogFilePtr;

     Data= ''
     OpID.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     PN.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     SN.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     TID.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     Result.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)
     Ptr.replace(r";",r",")  # Convert any ';' -> ',' (field separator!)

     #        my ($OpID, $PN, $SN, $TID, $Result, $Data, $Ptr) = @Args; ->05/12/02

          # (NB $TimeStamp, $Location, $Host_ID and $Op_ID are global, declared in &Init_All)

     File = Tmp + r"/" + Event.log
     for Key in TestData :	   
          if TestData[Key] != '': Data += Key + r"=" + TestData[Key]

     Data = Data[:-1] # Chomp last character
     try :
          OUT = open(File, 'r+')  
          OUT.write("1;"+Stats['TimeStamp']+r";"+Location+r";"\
                    +Host_ID+r";"+Op_ID+r";"+PN+r";"+SN+r";"+TID\
                    +r";"+Result+r";"+Data+r";",Ptr+";\n")
     finally:
          Exit (1, File) 

     File_Close (OUT);
     return

     #__________________________________________________________________________________

def Log_History(Type):
     "Log script start / end activity "
     
     if Globals.GlobalVar['LogPath'] == '' : sys.exit( Globals.GlobalVar['LogPath']+" not defined in: "+ "Log_History")
     LogFile = Globals.GlobalVar['LogPath'] + Globals.PathSep + "history.log"
     Msg = Util.PT_Date(str(time.time()), 1) + ":\t"+str(Globals.Stats['TimeStamp'])
     Msg += "\t"+Globals.Op_ID+"\t"+Globals.Stats['Host_ID']
     if Globals.Stats['Session']: Msg += "-"+str(Globals.Stats['Session'] )
     Msg += "\t"

     
     #perl  SWITCH: {Why needed ? in a loop see perl last 
     if Type == 1 :
          Msg += "Starting $Main ... "   #; last SWITCH; }
     elif Type == 2 :
          Msg += "Ending $Main" # ;                last SWITCH; }
     else:
          Exit(999, '(Invalid call to Log_History)')


     # This next one needs to be a 'die' since &Exit will &Log_History!
     try :
          if Globals.Debug : print("Log_History trying to open: %s" % LogFile)
          LOG = open(LogFile, 'r+')  
          LOG.write(Msg+'\n')
          LOG.close()
     except:
          exit("Can\'t open History file: " + LogFile )

     return (0);
#________________________________________________________________________________________
def Log_MAC(Product_ID, MAC_Addr):
     "First checks to make sure this MAC address has not been used before \
      then cats a new record to MAC.log in LogPath"

     # MAC log is a 'Type 4' record:
     # 4;Date;Product_ID;MAC_Address;
     # eg:    4;1134001942;0020140050000031;00-12-73-00-0E-40

     #    our @ID4MAC = ();

     File = LogPath+r"/"+MAC.log
     try :
          IN = open(File, 'r')  
     finally: 
          Exit (1, "Can\'t open "+File+" for read") 

     Found = 0
     for line in IN:
          line = line[:-1] # Chomp last character
          linesplit=line.split(r";")
          Type = linesplit[0]
          Date = linesplit[1]
          Prod_ID = linesplit[2]
          MAC = linesplit[3]
          if MAC == MAC_Addr :
               Found = 1;
               if Prod_ID != Product_ID :
                    #my $orig_date  = &PT_Date($Date, 7);
                    return (3, "MAC "+MAC+" already assigned to: "+Prod_ID)

     IN.close()
     if Found : return (0)

     #    $ID4MAC{$MAC_Addr} = $Product_ID; # from args

     #    foreach $Key ( sort keys %TestData ) {
     #            $Data .= "$Key=$TestData{$Key},"
     #                    if $TestData{$Key} ne '';
     #    }
     #    chop $Data;

     try :
          OUT = open(File, 'r+')  
     finally: 
          Exit (1, "Can\'t open "+File+" for append") 

     # do not see the point not converting to python Time = (defined $Stats{'TimeStamp'}) ? $Stats{'TimeStamp'} : time;
     Stats['TimeStamp'] = int(time.time()) #epoch time

     OUT.write("4;"+Time+";"+Product_ID+";"+MAC_Add+r"\n")

     File_Close (OUT);

     return (0);
     #________________________________________________________________________________________
def Log_MAC_Record(Product_ID, MAC_Addr):
     "First checks to make sure this MAC address has not been used before \
      then cats a new record to MAC.log in LogPath\
      Duplicate of Log_MAC()?? why"

     # MAC log is a 'Type 4' record:
     # 4;Date;Product_ID;MAC_Address;
     # eg:    4;1134001942;0020140050000031;00-12-73-00-0E-40

     #    our @ID4MAC = ();

     File = LogPath+r"/"+MAC.log
     try :
          IN = open(File, 'r')  
     finally: 
          Exit (1, "Can\'t open "+File+" for read") 

     Found = 0
     for line in IN:
          line = line[:-1] # Chomp last character
          linesplit=line.split(r";")
          Type = linesplit[0]
          Date = linesplit[1]
          Prod_ID = linesplit[2]
          MAC = linesplit[3]
          if MAC == MAC_Addr :
               Found = 1;
               if Prod_ID != Product_ID :
                    #my $orig_date  = &PT_Date($Date, 7);
                    return (3, "MAC "+MAC+" already assigned to: "+Prod_ID)

     IN.close()
     if Found : return (0)

     #    $ID4MAC{$MAC_Addr} = $Product_ID; # from args

     #    foreach $Key ( sort keys %TestData ) {
     #            $Data .= "$Key=$TestData{$Key},"
     #                    if $TestData{$Key} ne '';
     #    }
     #    chop $Data;

     try :
          OUT = open(File, 'r+')  
     finally: 
          Exit (1, "Can\'t open "+File+" for append") 

     # do not see the point not converting to python Time = (defined $Stats{'TimeStamp'}) ? $Stats{'TimeStamp'} : time;
     Stats['TimeStamp'] = int(time.time()) #epoch time

     OUT.write("4;"+Time+";"+Product_ID+";"+MAC_Add+r"\n")

     File_Close (OUT);

     return (0);
#__________________________________________________________________________________
def Print2XLog(Msg="", DontPrint2Screen=0, NoNewLine=0, TagAsError=0): 
     "Print a line to the execution log # Replacement for Print_Log"

     #!!! Find out whos calling with $NoNewLine set, and who cant just use Global Quiet the same as everyone else!!
     Util.chomp(Msg)  # chomp return to make sure we do not have two
     # perl not converting  see if needed  or fix my $EOL_Ch = ($NoNewLine) ? '' : "\n";
     EOL_Ch = r"\n"
     if not Globals.Quiet or not DontPrint2Screen : print(Msg) 
     Globals.Run_Time = Globals.Start_Time  # Also at PT2.pm

     # Tagging the date after so many minutes DOES NOT WORK (yet)
     ReDate = 2; # Time stamp every $ReDate sec
     Last_Log_Interval = int(time.time()) - Globals.Last_Log_Time #epoch time
     if TagAsError :
          Tag = "ERR " + Globals.Erc+ ":"
     else:
          Tag = '   '
     if Last_Log_Interval > ReDate : TimeField = Util.PT_Date(int(time.time()), 2) 
     else: print("Globals.Run_Time \t %.3f" % Globals.Run_Time)

     if Msg.startswith("done") : return (0) 
     LOG=''
     if not Globals.New_Log : #!!! Required for Win32 - otherwise really slow! (Opened in Yield.pl)
          try :
               LOG = open(Globals.XLog, 'r+') 
               LOG.write(TimeField+":\t"+Tag+"\t"+Msg+"\n")
               if not Globals.New_Log :
                    LOG.close               
               return (3)
          except: 
               Util.Exit(1, "Can\'t open "+Globals.XLog+" for append")          

    


     Globals.Last_Log_Time = int(time.time()) #epoch time

     return (0);

#__________________________________________________________________________________
def Print_Log(Mode=0, Msg=""):
     """obsolete! use Print2XLog instead"""

     if Mode > 11 : TagAsError = 1
     else : TagAsError = 0
     DontPrint2Screen = Mode

     Globals.RC = Print2XLog(Msg, DontPrint2Screen, 0, TagAsError);

     return (Globals.RC)
#__________________________________________________________________________________
def Print_Out(Msg):
     "Print a line to the output file Out_File"

     try :
          Out_File = open(fh, 'r+')   
     finally: 
          return (3)

     fh.write(Msg)
     fh.close

     return (0);
#__________________________________________________________________________________
def Print_Out_XML_Tag(Tag=''):
     "Add XML Tags"

     if Tag == '' :                 # It's an end tag - pop it off the stack
          Tag = '/' + Globals.XML_Tags.pop()
     else :                   
          Globals.XML_Tags.append(Tag) #!!! may want to do a split of any attribute later...

     Globals.RC = Print_Out("r\<"+Tag+r"\>"+"\n");
     return
#__________________________________________________________________________
def Rotate_Log(LogFile, Count):
     "Copy file.log.{n-1} to file.log.{n} ..."
     # Copy file.log.1 to file.log.2
     # Copy file.log to file.log.1
     # Delete file.log

     Move = 'mv'
     Delete = 'rm -f'
     From = ''
     To = ''

     if sys.name == 'NT' :
          Move = 'ren'
          Delete = 'del'

     PFN = fnstrip (LogFile,2)
     Ext = fnstrip(LogFile,8)

     while (Count) :
          To = PFN+Globals.PathSep+"."+Count+Globals.PathSep+"."+Ext
          Count -= 1
          From   = PFN+Globals.PathSep+"."+Count+Globals.PathSep+"."+Ext
          try:
               os.rename(From, To)
          finally:
               print ("Failed to move: " + From + " To: " + To )


     # This will only work if the logfile hasn't been opened yet!

     try:
          os.rename(LogFile, From)
     finally:
          print ("Failed to move LogFile: " + LogFile + " To: " + From )     

     # $From still contains the ...0.log

     if Globals.Erc : Exit (Globals.Erc,'') 
     Print2XLog ("Rotating log files ... -> " +To, 1);    # To the new log file!
     return()
#__________________________________________________________________________
def XML_Header():    #        Header information for XML File
                         #
     xmlfile=join(Globals.FileTmpDir,Globals.Out_File)
     try:
          if Globals.Debug : print("XML_Header trying to open: %s" % xmlfile)
          LOG = open(xmlfile, 'w')  
     except:      
          Util.Exit (3, "Can't open xml {} for cat".format(xmlfile))
     else:  
          LOG.write( "  \<Test_Head\> " + "____________________________________________" + "\n" )
          LOG.write( "	\<Startdate\>" + Util.PT_Date() + "</Startdate>\n")
          LOG.write( "	\<UserID>$Stats{'UserID'}</UserID>\n")
          LOG.write( "		\<Host_ID\>$Stats{'Host_ID'}</Host_ID>\n")
          LOG.write( "		\<Session\>$Stats{'Session'}</Session>\n")
          LOG.write( "		\<TID\>$TestData{'TID'}</TID>\n")
          LOG.write( "  <\/Test_Head\>\n")
          LOG.close


#__________________________________________________________________________
1;
