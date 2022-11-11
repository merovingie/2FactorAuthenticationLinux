#!/usr/bin/env python
import os, subprocess
import sys
from base64 import b64encode
import crypt

def isUserExist(uname, fileHandler):
    for line in fileHandler:
        tempLine = line.split(':')
        if tempLine[0] == uname:
            return True
    return False

def getUserExist(uname, fileHandler):
    for line in fileHandler:
        tempLine = line.split(':')
        if tempLine[0] == uname:
            return tempLine
    return False

def chkPassowrdMatch(passwd, re_passwd):
    return True if passwd!=re_passwd else False

def sysExit(fault):
    print(fault)
    sys.exit()

def hashFunc(pass_token, salt, algo_num = '$6$'):
    return crypt.crypt(pass_token,'$6$' + salt)

def getSelection():
    print("Welcome to 2FA!")
    print("(1) Create User Account")
    print("(2) Login")
    print("(3) Update Password")
    print("(4) Delete User Account")
    return input("Your Selection: ")

def appendShadowFile(line):
    file=open("/etc/shadow","a+")
    file.write(line+'\n') # Making hash entry in the shadow file
    file.close()

def writeShadowFile(orginal_line, new_line):
    with open('/etc/shadow', 'r') as f:
        lines = f.readlines()

    with open('/etc/shadow', 'w') as f:
        for line in lines:
            if line == orginal_line:
                line = line.replace(orginal_line, new_line)
            f.write(line)
    f.close()

def deletelineShadowFile(orginal_line):
    with open('/etc/shadow', 'r') as f:
        lines = f.readlines()

    with open('/etc/shadow', 'w') as f:
        for line in lines:
            if line != orginal_line:
                f.write(line)
    f.close()

def deletelinePasswdFile(uname):
    with open('/etc/passwd', 'r') as f:
        lines = f.readlines()

    with open('/etc/passwd', 'w') as f:
        for line in lines:
            temp1=line.split(':')
            if temp1[0] != uname:
                f.write(line)
    f.close()

def writePasswdFile(line):
    file=open("/etc/passwd","a+") #Opening passwd file in append+ mode
    file.write(line)   #creating entry in passwd file for new user
    file.close()

def createDir(uname):
    try:
        os.mkdir("/home/"+uname) #Making home file for the user
    except:
        sysExit("Directory: /home/"+uname+" already exist")

def deleteDir(uname):
    try:
        os.rmdir("/home/"+uname)
    except:
        sysExit("Can't Delete Directory: /home/"+uname+".")

#Start Main

#check if Root
if os.getuid()!=0: sysExit("Please, run as root.")

#Get Selection
selection= getSelection()

#Check Selection
if selection=='1':
    uname=input("Enter your username: ")
    with open('/etc/shadow','r') as fp:
        if isUserExist(uname, fp):
            error_output = "Failure: user " + uname + " already exists"
            sysExit(error_output)
        passwd=input("Enter your password: ")
        re_passwd=input("Confirm your password: ")
        if chkPassowrdMatch(passwd, re_passwd): sysExit("Paswword do not match")
        salt=input("Enter the salt: ")
        init_token=input("Enter the initial token (IT) from the Token Generator: ")
        pass_token = passwd + init_token
        hash = hashFunc(pass_token, salt)       
        line = uname+':' + hash + ":17710:0:99999:7:::" #To-DO: check what those values mean to enter in shadow
        appendShadowFile(line)
        createDir(uname)
        count=1000
        with open('/etc/passwd','r') as f: #Opening passwd file in read mode
            arr1=[]
            for line in f:
                temp1=line.split(':')
                while (int(temp1[3])>=count and int(temp1[3])<65534): #checking number of existing UID
                    count=int(temp1[3])+1          #assigning new uid = 1000+number of UIDs +1
        count=str(count)
        str1=uname+':x:'+count+':'+count+':,,,:/home/'+uname+':/bin/bash\n'
        writePasswdFile(str1) 
        print ("SUCCESS: " + uname + " Created")

elif selection=='2':
    uname=input("Enter username: ")
    with open('/etc/shadow','r') as fp:
        temp_arr = getUserExist(uname, fp)
        if not(temp_arr):
            error_output = "Failure: user " + uname + " doesn't exists"
            sysExit(error_output)
        passwd=input("Enter Password for " + uname + ": ")
        current_token=input("Enter current token: ")
        next_token=input("Enter next token: ")
        pass_current_token = passwd + current_token
        pass_next_token = passwd + next_token
        salt_pass=(temp_arr[1].split('$'))
        salt=salt_pass[2]
        result=crypt.crypt(pass_current_token,'$6$' + salt) 
        if result==temp_arr[1]:                   
            print("SUCCESS: Login Successful") 
            orgLine = ':'.join(temp_arr)
            pass_next_token=crypt.crypt(pass_next_token,'$6$'+salt)
            temp_arr[1] = pass_next_token
            newLine = ':'.join(temp_arr)
            writeShadowFile(orgLine, newLine)
        else:
            sysExit("FAILURE: passwd/token incorrect")
    fp.close()

elif selection=='3':
    uname=input("Enter username: ")
    with open('/etc/shadow','r') as fp:
        temp_arr = getUserExist(uname, fp)
        if not(temp_arr):
            error_output = "Failure: user " + uname + " doesn't exists"
            sysExit(error_output)
        passwd=input("Enter Password for " + uname + ": ")
        new_passwd=input("Enter New Password for "+uname+": ")
        re_new_passwd=input("Confirm New Password for "+uname+": ")
        if chkPassowrdMatch(new_passwd, re_new_passwd): sysExit("Password do not match")
        new_salt=input("Enter new salt for "+uname+": ")
        current_token=input("Enter current token: ")
        next_token=input("Enter next token: ")
        pass_current_token = passwd + current_token
        pass_next_token = new_passwd + next_token
        salt_pass=(temp_arr[1].split('$'))
        salt=salt_pass[2]
        result=crypt.crypt(pass_current_token,'$6$' + salt)
        if result==temp_arr[1]:
            print("SUCCESS: user " + uname + " updated")
            orgLine = ':'.join(temp_arr)
            pass_next_token=crypt.crypt(pass_next_token,'$6$'+new_salt)
            temp_arr[1] = pass_next_token
            newLine = ':'.join(temp_arr)
            writeShadowFile(orgLine, newLine) 
        else:
            print("FAILURE: passwd/token incorrect")

elif selection=='4':
    uname=input("Enter username: ")
    with open('/etc/shadow','r') as fp:
        arr=[]
        temp_arr = getUserExist(uname, fp)
        if not(temp_arr):
            error_output = "Failure: user " + uname + " doesn't exists"
            sysExit(error_output)
        passwd=input("Enter Password for " + uname + ": ")
        current_token=input("Enter current token: ")
        pass_current_token = passwd + current_token
        salt_pass=(temp_arr[1].split('$'))
        salt=salt_pass[2]
        result=crypt.crypt(pass_current_token,'$6$' + salt)
        if result==temp_arr[1]:                   
            print("SUCCESS: User " + uname + " Deleted") 
            orgLine = ':'.join(temp_arr)
            deletelineShadowFile(orgLine)
            deleteDir(uname)
            deletelinePasswdFile(uname)
        else:
            sysExit("FAILURE: passwd/token incorrect")
    fp.close()

else: sysExit("Entered the wrong selection") 
