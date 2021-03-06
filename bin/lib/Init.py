#!/usr/bin/python
################################################################################
#
# Module:      Init.py
#
# Author:      Paul Tindle ( mailto:Paul@Tindle.org )
#			 Joe White( mailto:joe@stoke.com )
#
# Descr:      Main Library for Intitialization
#
# Version:    (See below) $Id$
#
# Changes:    Conversion Perl V1.17 to Python - JSW
#			
#
# Still ToDo:
#
# License:   This software is subject to and may be distributed under the
#            terms of the GNU General Public License as described in the
#            file License.html found in this or a parent directory.
#            Forward any and all validated updates to Paul@Tindle.org
#
#            Copyright (c) 1993 - 2005 Paul Tindle. All rights reserved.
#            Copyright (c) 2005-2013 Stoke. All rights reserved.
#            Copyright (c) 2017 Joe White. All rights reserved.xx
#
################################################################################
VER= 'v0.1 5/23/2017'; # Conversion to Python from Perl 052317 JSW
CVS_VER = ' [ Git: $Id$ ]'
global CMtestVersion
if "CMtestVersion" not in globals() : CMtestVersion={}
CMtestVersion['Init'] = VER + CVS_VER

#_____________________________________________________________________________
import Globals
import sys #Added for Ubuntu 9.10 support should work with Fedora
import shutil
import os
# Not converted to Python use Cwd qw( abs_path ) What is it?
import time
usleep = lambda x: time.sleep(x/1000000.0)
# Not sure if this is going to be converted to Python JSW
##use SigmaProbe::SPUnitReport;
#use SigmaProbe::SPTestRun;
#use SigmaProbe::SPTimeStamp;
#use SigmaProbe::Local;
import Banner
from datetime import datetime, timedelta
import socket
if not os.name == "nt": import crypt, pwd
import getpass # No Default support for crypt in Windows
#from passlib.hash import bcrypt  # needs pip install
import bcrypt
import os.path
import FileOp
import Logs
import Util
import Stats # qw( %Stats %TestData %Globals $Stats_Path);
from os.path import isfile, join
#try:
    #import pwd
#except ImportError:
    #import winpwd as pwd


#__________________________________________________________________________
def Final():
    "Last thing that's run before completion of cmtest"
    "Figures status and creates Event log"
    global Stats
    #&Print_Out_XML_Tag ();
    ID = Stats['UUT_ID']
    slot=0
    if (os.path.getsize(Out_File) and
        not ((Stats['UUT_ID'] == '') and  not Log_All )) : 
        Stamp = PT_Date(Stats['TimeStamp'], 9)
        if ID == '' : ID = 'unknown'
        Test_Log = TestLogPath+"/" + ID+"-"+Stamp.xml
        if TestLogPath == '':
            Exit (999, "Undefined test log path for %s" % Test_Log)
        try : 
            shutil.copy2(Test_Log, Out_File) #Copy like cp -p
        except:
            Exit (7, 'Failed log file copy')

    Stats.Update_Test_Times()


    if TestData['TEC'] == 0 and Stats['Result'] == 'INCOMPLETE' :
        Stats['Result'] = 'PASS'

    Stats['Status'] = 'Finished'
    Stats['TTG'] = 0
    Stats.Update_All
    XML_Tail()  #Added JSW - Stoke
    Print_Out_XML_Tag ()
    Print_Log (1, "Writing new Event & Cfg Log records ... ")
    Log_Event (Op_ID, PN[0], SN[0], TestData['TID'], Stats['Result'], fnstrip (Test_Log,3))
    Log_Event_Record (Op_ID, PN[0], SN[0], TestData['TID'], Stats['Result'], fnstrip (Test_Log,3))
    for i in range(1,25):        # Updated for 14 Slot Chassis 1/10/07
        if SN[i] == '': Log_Cfg (Op_ID, SN[0], (i - 1), PN[i], SN[i]) 
        if SN[i] == '': Log_Cfg_Record (Op_ID, SN[0], (i - 1), PN[i], SN[i]) 
        slot=i-1;
        if not SFPData_slot_ar[(slot)][0]['TYPE'] == '' :
            for j in range(0,15) :
                if not SFPData_slot_ar[(slot)][j]['PowerdBm'] == '' :
                    if not SFPData_slot_ar[(slot)][j]['SerialNo'] == '' :
                        Log_Cfg (Op_ID, SN[0],slot+":"+j,SFPData_slot_ar[(slot)][j]['Vendor']+" "+SFPData_slot_ar[(slot)][j]['ModelNo']+" "+SFPData_slot_ar[slot][j]['PowerdBm']+"dBm",\
                                 SFPData_slot_ar[(slot)][j]['SerialNo']) 
                    else : pass
                    if not SFPData_slot_ar[(slot)][j]['SerialNo'] == '':
                        Log_Cfg_Record (Op_ID, SN[0],slot+":"+j,SFPData_slot_ar[(slot)][j]['Vendor']+" "+SFPData_slot_ar[(slot)][j]['ModelNo']+" "+SFPData_slot_ar[(slot)][j]['PowerdBm']+"dBm", \
                                        SFPData_slot_ar[(slot)][j]['SerialNo'])
                    else: pass
                else:
                    if not SFPData_slot_ar[(slot)][j]['SerialNo'] == '' : 
                        Log_Cfg (Op_ID, SN[0],slot+":"+j,SFPData_slot_ar[(slot)][j]['Vendor']+" "+SFPData_slot_ar[(slot)][j]['ModelNo'], SFPData_slot_ar[(slot)][j]['SerialNo']) 
                    else: pass
                    if not SFPData_slot_ar[(slot)][j]['SerialNo'] == '' :
                        Log_Cfg_Record (Op_ID, SN[0],slot+":"+j,SFPData_slot_ar[(slot)][j]['Vendor']+" "+SFPData_slot_ar[(slot)][j]['ModelNo'], SFPData_slot_ar[(slot)][j]['SerialNo']) 
                    else: pass


    Send_Email();  #Send our EMail Notifications

    #!!!    &Submit_SigmaQuest_Unit_Report;
    if GUI :Result (Stats['Result']) 
    #Convert seonds to Day Hour Min
    TTIME = datetime(1,1,1) + int(TestData['TTT'])
    TestTime = "DAYS:%i HOURS:%i MIN:%i SEC:%i" % TTIME.day, TTIME.hour, TTIME.minute, TTIME.second

    #Create Banner
    #Banner(new,fill,set)  final is tbd 
    banner_result = Banner(Stats['Result'], Stats['Result'])
    TID_result = Banner(TestData['TID'], TestData['TID'])

    Exit (0, "Finished! (%i) - %s %s %s!\n%s%s" % Test_Time, TestData['TID'],Session[Stats['Session']], Result[Stats['Result']],TID_result, banner_result)
    return
#_______________________________________________________________
def First_Time():
    " Check if test evironment is setup before running cmtest"
    
    if Debug : print("In Function %s" % __name__)
    Print_Log ( 1, "Running First_Time")

    print("\n\tThe main Test Controller configuration file (%s) is MIA!\n" % Cfg_File)
    print("\tPlease copy the defaults file '/var/local/cmtest/dist/cfgfiles/testctrl.defaults.cfg'\n")
    print("\tto /usr/local/cmtest and then edit the definitions as appropriate\n")
    print("\tAborting...\n\n")

    exit()

    # OR eventually if GUI...
    #system "java -jar First_Time.jar $Test_Cfg_XMLFile"
        #or die "Can't run java form";
    #&XML2Hash ($Test_Cfg_XMLFile); #This is now the one modified by Jez's jar
    # Then return to continue reading reading the cfg file
    return
#_______________________________________________________________
def Get_Release_Info():
    "Get our release pipe from env and compare to config"

    File = GP_Path+"/bin/Release.id"
    Str  = ''
    if os.path.exists(File) :
        Erc = Read_Cfg_File (File);
        if Erc: exit( "Init died with Erc=$Erc trying to read Cfg_File")                # NB: No Erc translation yet!
        TestData['Ver'] = Version
        TestData['Pipe'] = Pipe
        Str = "Release_Info: File = %s: Version=%s Pipe=%s" % File, Version, Pipe
        if not Pipe == os.getenv('CmTest_Release_Pipe',"Not Found") :
            exit("Init died with Pipe mismatch CMtest pipe:%s diff from ENV pipe:%s" % Pipe, os.getenv('CmTest_Release_Pipe',"Not Found") )
    else :
        Str = "File not found!" % File;

    if not Version == '' : return (Str)
    else: return("No version")

#__________________________________________________________________________
def Init_All(Util_only=0):
    " This is the 1st Init stage, done before getopts,"
    "usually called at the beginning of &main::Init"
    if Globals.Debug : print("In sub Function %s" % __name__)
    if getpass.getuser()=='root' and  not Util_only: exit(  "\n\tLet\'s not let \'root\' run a test - parochial ownership of files awaits!\n\n")
    # Acquired from cmtest.pl BEGIN block in v30 2006/02/15
    if os.name == "nt":
        Globals.OS = "NT"
    else:
        Globals.OS = "Linux"

    #GP_Path = FileOp.fnstrip()
    #if GP_Path == '' : GP_Path = '..'       # for a $0 of ./

    # Already done in cmtest.py, not sure this is used by other routines
    #Get our base directory and find the Station Config File 
    #FileOp.fnstrip()
    #if Debug > 0 : print ("OS: %s path detected is:" % OS,  File.fnstrip())
    #PPATH = FileOp.fnstrip()
    #if PPATH == '': PPATH = ".."

    #if OS == "NT":
        #try:  
            #os.path.isfile(PPATH + "\cfgfiles\testctrl.defaults.cfg")
            #Cfg_File = PPATH + "\cfgfiles\testctrl.defaults.cfg"
        #except:
            #Cfg_File = os.path.abspath(__file__) + "testctrl.defaults.cfg"
            #TmpDir = os.path.expanduser("~")
    #else:
        #try:
            #os.path.isfile('/usr/local/cmtest/testctrl.cfg')
            #Cfg_File = '/usr/local/cmtest/testctrl.cfg'
            #TmpDir = expanduser("~") + "/tmp"  
        #except:
            #Cfg_File = os.path.abspath(__file__) + "testctrl.defaults.cfg"

    #if OS == 'nt':
        #Cfg_File = PPath + "/" + "cfgfiles/testctrl.defaults.cfg"
        #Tmp = os.getenv('TMP', "NO_TMP")
    #else :
        #Cfg_File = r'/usr/local/cmtest/testctrl.cfg'
        #Tmp = os.getenv(os.path.expanduser("~") + "/tmp", "NO_TMP")


    #CmdFilePath = r"../" + GP_Path +r"/cmdfiles"
# end [acquired]

    try: 
        os.path.isdir(Globals.FileTmpDir) # $Tmp is declared in $Globals
        try:
            os.path.isfile(Globals.FileTmpDir)
        except:
            exit("Attempting to create \%s: file %s exists!" % Globals.FileTmpDir, Globals.FileTmpDir)
    except:
        try:
            os.mkdir(Globals.FileTmpDir)
        except:
            exit("Can\'t create tmp directory %s" % Globals.FileTmpDir)
    if Globals.Debug : print("Debug in Init all:%s" % Globals.Debug)
    if Globals.Debug and not os.path.isfile(Globals.Cfg_File) : print("Debug: Run config read with %s" % Globals.Cfg_File)
    if not Util_only:         # Required for test oriented scripts only ...
        try: 
            if Globals.Debug : print("Run config read with %s" % Globals.Cfg_File)
            os.path.isfile(Globals.Cfg_File)
            First_Time
            Globals.Erc = Util.Read_Cfg_File(Globals.Cfg_File)  # $Cfg_File is defined in main:: BEGIN block
            if Globals.Erc: exit("Init died with Erc=%s trying to read Cfg_File \'%s\'" % Globals.Erc, Globals.Cfg_File) 
        except:
            if Globals.Debug : print("exit Run config read with %s" % Globals.Cfg_File)
            if not os.path.isfile(Globals.Cfg_File):
                exit("Cfg_File:%s doesn\'t exist" % Globals.Cfg_File)    # Temporary, until ...

        Globals.Erc = Logs.Log_History(1)
        if Globals.Erc : exit("Init died with Erc=%s trying to open History log" % Globals.Erc)

        #!! Check to make sure that GUID is set
        TestLogPath = Globals.GlobalVar['LogPath'] + Globals.PathSep + "logfiles"
        if not os.path.isdir(TestLogPath) :
            Util.Exit(999, "No permenant log file path >%s<" % TestLogPath)
        return
#__________________________________________________________________________
def Init_Also(Util_only) :
    "This is the 3rd Init stage, done after getopts, etc"
    "usually called at the end of &main::Init"

    if Globals.Debug : 
        print( "Debug Quiet Verbose", Globals.Debug, Globals.Quiet, Globals.Verbose)

    Util.Show_INC
    #our $GUI = ($ENV{DISPLAY} eq '') ? 0 : 1;        # !!! but what about Win32?
    Globals.GUI = 0

    #!!! we can probably lose this test, since disty.pm is the only declarer
    #     of $Util_Only, since no one else uses Init.pm!
    if not Globals.Util_only :        # Session = '' ...
        if not Globals.SessionForce :
            Stats.Session ('next')               # Sets the next Session No.
        else :
            Globals.Stats['Session'] = Globals.Session;
            Pid = Stats.Session ('read');        # Returns 0 if available
                    # check the process table ...
            if Globals.Pid and not Globals.Pid == Globals.Stats['PID'] or Is_Running(GLobals.Pid, 1) :
                    # The requested session is already running!
                if not Globals.SessionForce : Exit(107, "Session %i start declined" % Globals.Session) 
                Print_Log (11, "Forcing session %i" % Session)
            Stats.Session('write')                # Tags the Session.
        if not os.path.isdir(Globals.FileTmpDir) : 
            try : os.mkdir(Globals.FileTmpDir)
            except: exit("Unable to Create tmp dir %s" % Globals.FileTmpDir)
        Globals.FileTmpDir += Globals.PathSep + 's' + str(Globals.Stats['Session'])
        if not os.path.isdir(Globals.FileTmpDir) : 
            try : os.mkdir(Globals.FileTmpDir)
            except: exit("Unable to Create tmp dir %s" % Globals.FileTmpDir)
        Logs.Arc_Logs (Globals.FileTmpDir, '_logs')
        os.umask(0)
        Arc_File = "2arc2_logs_" + str(Util.PT_Date(time.time(),5))
        try:
            if Globals.Verbose : print ("Init_Also Creating arc file %s " % join(Globals.FileTmpDir,Arc_File))
            fh = open(join(Globals.FileTmpDir,Arc_File),"w")
            #close(fh)
        except:
            exit("Unable to create Arc_File %s" % join(Globals.FileTmpDir,Arc_File))

    # Set up log files...
    Log_Str = ''
    Globals.XLog = join(Globals.FileTmpDir,Globals.Main)+r".log";
    #!!!    &Read_Version;
    Msg = Get_Release_Info      # Sets $Version, etc or Aborts on error!
    if not Globals.Quiet : print( "\n\n" )
    if Globals.Stats['Session'] : Log_Str += "Session "+ str(Globals.Stats['Session'])+": "
    Log_Str += "Starting %s version %s at %s" % (Globals.Main, Globals.TestData['Ver'], Util.PT_Date(time.time(), 2))
    Globals.Erc = Logs.Print_Log (1, Log_Str)
    Log_Str = ''
    if Globals.Erc : Util.Exit (3, "(%s)" % Globals.Xlog)
    Logs.Print_Log (11,"This PID = %s, ShellPID = %s" % (Globals.Stats['PID'], Globals.Stats['PPID']))
    if Globals.Debug : print ("Init_also GP_Path %s" % Globals.GP_Path)
    Logs.Print_Log (11, 'path = ' + Globals.GP_Path)
    #for Module in  sys.modules['os'] :
    #Vers = Globals.CMtestVersion[FileOp.fnstrip(sys.modules['os'], 7)]
    #Module  = sys.modules['OS']  #Value (Full path / filename)
    #if Module[0:1] == '.' :
        #Module = join(os.getcwd(),Module)
    #Log_Str = "Lib: " + Module
    #if Vers == '' : Log_Str += "\t[Ver: %s]" % Vers
    #if not str.find(Module, "python") : Print_Log (11, Log_Str)
    #IncAge = time.time() - stat.st_mtime(Module)
    #if IncAge < 1000 : Print_Log (1, "Using new Module") 

    Log_Str = ''

    if not Util_only:                 # Required for test oriented scripts only ...
        Util.Abort ('clear');             # Remove any lurking abort flags
        Globals.Stats['Status'] = 'UserID'
        Globals.Stats['Power'] = 0  #Power supply on count
        Stats.Update_All()
        if Globals.GlobalVar['UserID_Check'] == 1 :
            UserID_tmp = ''
            if Globals.CurrentUserID == 'none' :
                Globals.CurrentUserID = Util.Ask_User( 'text16', 'UserID', 'Please enter your UserID#' )
            UserID_tmp = bcrypt.hashpw(Globals.CurrentUserID.encode('utf-8'),bcrypt.gensalt()) # Still need to figure out key in python $Key;
            if Globals.Debug : print ("Init user password hash is : %s" %UserID_tmp)
            UID_Check (UserID_tmp)  #Exit on fail!  Use adduser.pl ...
            Globals.Stats['UserID'] = UserID
            
        Globals.Stats['Status'] = 'Menu'
        Stats.Update_All()

        Globals.Comm_Log = join(Globals.FileTmpDir,"Comm.log")
        # system "rm -f $Comm_Log";        # OR
        #        &Rotate_Log ($Comm_Log, 10);
                                                        # Aborts on error!
        Util.Abort ('check')             # Make sure there isn't an ABORT flag lurking

                                        # Figure the UUT_IP address ...

        IPA = Globals.GlobalVar['UUT_IP_Base'].split(r".")
        IPAint=int(IPA[3])
        UUT_IP_Top = IPAint + int(Globals.GlobalVar['UUT_IP_Range']) - 1        # Highest sub allowed
        IPAint += int(Globals.Stats['Session']) - 1            # 1 per session or
        if IPAint > UUT_IP_Top : Exit (28, "No IP addr available for this session") 
        Globals.UUT_IP  = "%s.%s.%s.%s" %(IPA[0],IPA[1],IPA[2],IPAint)
        IPAint += 1  ##$IPA[3]++;  There is a possibility of conflict, but we shuld end up using 2 session if the second IP is used.
        if IPAint > UUT_IP_Top : Exit (28, "No Secondary IP addr available for this session") 
        Globals.UUT_IP_SEC  =  "%s.%s.%s.%s" %(IPA[0],IPA[1],IPA[2],IPAint)

        Logs.Print_Log (11, "UUT_IP  = %s" % Globals.UUT_IP)
        Logs.Print_Log (11, "CmdFilePath = %s" % Globals.CmdFilePath)
        # Assign the output file ...
        Globals.Out_File = join(Globals.FileTmpDir,Globals.Out_File) # Default is cmtest.xml
        try:
            os.remove(Out_File)
        except: pass    
        Logs.Print_Out_XML_Tag ('Test')
        Globals.Erc = 0;
        Stats.Update_All

        PT_Log = join(Globals.FileTmpDir,"Expect.log")
        try:
            os.remove(PT_Log)
        except: pass
    return
#_______________________________________________________________
def Invalid(Usage):
    "May not be used, looks like was for command line processing in Perl"


    print("%s%s" % Bell, Usage)
    exit (Erc)


#_______________________________________________________________
def Mk_Port():
    "Make out minicom(linux) serial port configuration, used to modify baud rate"

    Port = Stats['Session']
    File = "/etc/minirc." + Port
    if Linux_gbl == 'Ubuntu': File = "/etc/minicom/minirc." +Port 

    UMask = os.umask;  os.umask(0)
    try: 
        OUT = open(File, 'w') #overwite old
        OUT.write("# Machine-generated file created " + PT_Date(time.time(), 2) + "\n")
        OUT.write("pr port             %s\n" % SPort[Port])
        print("Setting buad rate to %s\n" % Baud )  # Baud is from testctlr.cfg and menu execution
        OUT.write("pu baudrate         %s\n" % Baud)
        OUT.write("pu minit\n")
        OUT.write("pr rtscts           No\n")
        OUT.write("pu histlines        4000\n") # buffer size for text capture	
    except:
        Exit (35, "Can\'t cpen minicom cfg file %s for port %s" % File, Port);

    close(OUT)
    os.umask(Mask)
    return
#_______________________________________________________________
def UID_Check(UserTmp=''):
    "$UserID strarts out as an encypted pw, then ->user_name"
    "$UserID is our global, to be retrieved from %User_ID{PW"

    Globals.Erc = Util.Read_Data_File (Globals.GlobalVar["UsersCfgPath"])   # was $GP_Path/cfgfiles/users.cfg
    if Globals.Erc : Util.Exit ( 999, "Can't read User cfg file") 

    #    &Print_Debug;  $uid.pl
    Msg = "UID_Check: Key=\'%s\', " % Globals.CurrentUserID
    Globals.CurrentUser_Level = Globals.User_Level[Globals.CurrentUserID]
    Globals.CurrentUserID = Globals.User_ID[Globals.CurrentUserID]
    if Globals.CurrentUserID == '' : Msg += "UID=" + UserTmp + ', ' 
    Msg += "User=%s Level=%s" % Globals.CurrentUserID, Globals.CurrentUser_Level
    Print_Log (11, Msg)
    if Development == 0 : 
        if Globals.CurrentUserID == '' : Exit ( 999, "Failed user authentication") 
    else :
        if Globals.CurrentUserID == '' : Print2XLog ("Warning: Failed user authentication\n") 

    return ()
#__________________________________________________________________________
1;
