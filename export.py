import os
from email.mime.multipart import MIMEMultipart 
from email.mime.text import MIMEText 
from email.mime.base import MIMEBase 
from email import encoders
from algo import encrypt, decrypt
import mysql.connector
import smtplib
from input_filters import input_alias, input_searchmenu, input_sno, input_yesorno

#LINKING PYTHON AND MYSQL:
mycon=mysql.connector.connect(host="localhost",user="root",password="MySQLPswd")    #Remember to change password

#CREATING DATABASE AND TABLE:
mycursor=mycon.cursor()
mycursor.execute("create database if not exists PasswordManager")
mycursor.execute("use PasswordManager")


def export_to_mail(usernamearea,keyarea):
    mycursor=mycon.cursor()
    f=open("exporttomail.txt","w")
    str2="select * from {}".format(keyarea)
    mycursor.execute(str2)
    data=mycursor.fetchall()
    L=['_'*135,'\n',f"|| {'Website':30} | {'Alias':30} | {'Username':15} | {'Password':45} ||",'\n','-'*135]
    f.writelines(L)
    f.write("\n")
    for row in data:
        site=decrypt(row[0],keyarea)
        alias=decrypt(row[1],keyarea)
        uname=decrypt(row[2],keyarea)
        pswd=decrypt(row[3],keyarea)
        f.write(f"|| {site:30} | {alias:30} | {uname:15} | {pswd:45} ||")
        f.write('\n')
    f.write('_'*135+'\n')    
    f.close()
    str1="select email from login where Username=%r"%encrypt(usernamearea,'lwosch')
    mycursor.execute(str1)
    y=mycursor.fetchone()
    fromaddr = "csprojectotpgenerator@gmail.com"
    toaddr = decrypt(y[0],'lwosch') 
    # instance of MIMEMultipart 
    msg = MIMEMultipart() 
    # storing the senders email address   
    msg['From'] = fromaddr 
    # storing the receivers email address  
    msg['To'] = toaddr 
    # storing the subject  
    msg['Subject'] = "Password Email Sync"
    # string to store the body of the mail 
    body = "Your passwords were securely and successfully synced with your mail"
    # attach the body with the msg instance 
    msg.attach(MIMEText(body, 'plain')) 
    # open the file to be sent  
    filename = "Website Password Table.txt"
    attachment = open("exporttomail.txt", "r") 
    # instance of MIMEBase and named as p 
    p = MIMEBase('application', 'octet-stream') 
    # To change the payload into encoded form 
    p.set_payload((attachment).read()) 
    # encode into base64 
    encoders.encode_base64(p)    
    p.add_header('Content-Disposition', "attachment; filename= %s" % filename) 
    # attach the instance 'p' to instance 'msg' 
    msg.attach(p) 
    # creates SMTP session 
    s = smtplib.SMTP('smtp.gmail.com', 587) 
    # start TLS for security 
    s.starttls()
    # Authentication 
    s.login("csprojectotpgenerator@gmail.com", "ssllxekmtvfvtshb") 
    # Converts the Multipart msg into a string 
    text = msg.as_string() 
    # sending the mail 
    s.sendmail(fromaddr, toaddr, text) 
    # terminating the session 
    s.quit()
    attachment.close()
    os.remove("exporttomail.txt")
    print("Data successfully sent to mail.")
    print("Returning to menu...")
    mycursor.close()    

def search_procedure(keyarea):      #keyarea is used just in case to avoid confusion
    #LINKING PYTHON AND MYSQL:
    mycon=mysql.connector.connect(host="localhost",user="root",password="MySQLPswd",database="PasswordManager")    #Remember to change password

    print("Please choose an method to search:\n\t1. Show all websites\n\t2. Search a website\n\t3. Exit\n")
    n=input_searchmenu()
    cur=mycon.cursor()
    if n==1:
        cur.execute("select website,website_alias,username from {}".format(keyarea))
        data=cur.fetchall()
        ctr=0
        print('_'*98)
        print(f"|| S.No | {'Website':34} | {'Alias':30} | {'Username':15} ||")
        print('-'*98)
        for i in data:
            ctr+=1
            site=decrypt(i[0],keyarea)
            alias=decrypt(i[1],keyarea)
            uname=decrypt(i[2],keyarea)
            print(f"||  {ctr:02}  | {site:34} | {alias:30} | {uname:15} ||")
        print('_'*98+'\n')
        sno=input_sno(ctr)         
        site=decrypt(data[sno-1][0],keyarea)
        uname=decrypt(data[sno-1][2],keyarea)
        mycon.close()
        return (site,uname)

    elif n==2:
        print("Enter website or alias to be searched")
        search_string=input_alias()
        cur.execute("select website,website_alias,username from {}".format(keyarea))
        data=cur.fetchall() 
        cur.close()

        L=[]
        for i in data:                                          #decrypting
            site=decrypt(i[0],keyarea)
            alias=decrypt(i[1],keyarea)
            uname=decrypt(i[2],keyarea)
            L+=[(site,alias,uname),]
                                                
        M=[]
        for i in range(len(L)):                              
            L[i]+=((len(((L[i][0]+L[i][1]).lower()).split(search_string.lower()))-1)*len(search_string),)
                                                
        L.sort(key=lambda x:x[-1], reverse=True)
        for i in range(len(L)):
            if L[i][-1]>0:                                      
                M+=[tuple(x for x in L[i] if type(x)==str)]
        if len(M)>10:                           
            M=M[:10]
        for i in range(len(M)):                                 
            M[i]=(i+1,)+M[i]
        
        if len(M)!=0:
            ctr=0
            print('_'*98)
            print(f"|| S.No | {'Website':34} | {'Alias':30} | {'Username':15} ||")
            print('-'*98)
            for i in M:
                ctr+=1
                site=i[1]
                alias=i[2]
                uname=i[3]
                print(f"||  {ctr:02}  | {site:34} | {alias:30} | {uname:15} ||")
            print('_'*98+'\n')
            sno=input_sno(ctr)     
            site=M[sno-1][1]
            uname=M[sno-1][3]
            mycon.close()
            return (site,uname)
        else:
            print("Data not found.")
            print("Would you like to try again? \n\t 1. YES \t 2. NO")
            y=input_yesorno()
            if y==1:
                search_procedure(keyarea)
            else:
                print("Returning to menu...")
                mycon.close()
                return None,None

"""
I have removed this option from search menu as well.
    elif n==3:
        mycon.close()
        print('This functionality will be available soon....)')

"""
