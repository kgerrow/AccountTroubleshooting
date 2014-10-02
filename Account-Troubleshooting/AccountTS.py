#-------------------------------------------------------------------------------
# Name:            ArcGIS Online Account Diagnostic Tool
# Purpose:         Can help diagnose sign issues where a user knows their username
#                   and password
# Author:     Kelly Gerrow
#
# Created:     8/19/2014
# Copyright:   (c) kell6873 2014
# Licence:     <your licence>
#-------------------------------------------------------------------------------
#import xml.dom.minidom as DOM
import os, os.path
import sys
import urllib2, urllib, requests
import json
################################################################################


#variables
user = raw_input("Admin username:")
pw  = raw_input("Password:")

#generate token
def getToken(user, pw):
    data = {'username': user,
        'password': pw,
        'referer' : 'https://www.arcgis.com',
        'f': 'json'}
    url  = 'https://www.arcgis.com/sharing/rest/generateToken'
    try:
        jres = requests.post(url, data=data, verify=False).json()
        return jres
    except KeyError:
        print 'Incorrect password'

#Generate Short URL
def GetURL(token):
    URL= 'http://www.arcgis.com/sharing/rest/portals/self?f=json&token=' + token
    response = requests.get(URL).json()
    URLKey = response['urlKey']
    print URLKey
    return URLKey

#Is this a public Account?
def pubUser(user, token):
    url = 'https://www.arcgis.com/sharing/rest/community/users/{}?f=json&token='.format(user)+token
    response = requests.get(url, verify=False).json()
    try:
        if response['orgId']:
            userType=response['role']
    except KeyError:
        userType = 'pub'
    return userType


#admin Contact Info:
def adminContact(token, URLKey):
    maxURL ='http://{}.maps.arcgis.com/sharing/rest/portals/self/users'.format(URLKey)
    request = maxURL +"?f=json&token="+token
    response = requests.get(request)
    jres = json.loads(response.text)
    maxUsers = jres['total']
    start = 1
    number = 50
    userlist =[]
    while start < maxUsers:
        listURL ='http://{}.maps.arcgis.com/sharing/rest/portals/self/users'.format(URLKey)
        request = listURL +"?start="+str(start)+"&num="+str(number)+"&f=json&token="+token
        response = requests.get(request)
        jres = json.loads(response.text)
        for item in jres['users']:
            if item['role'] == 'org_admin':
                userlist.append(item['email'])
        start+=number
    return userlist


token = getToken(user,pw)


try:
    if token['token']:
        token = token['token']
        userType = pubUser(user, token)
        #Determine if Public account
        if userType == 'pub':
            print 'This is a public account please contact customer service regarding accessing your organization'
        else:
            URLKey = GetURL(token)
            #list entitlements if user is not an admin
            if userType != 'org_admin':
                AdminInfo = adminContact(token,URLKey)
                concat = ", "
                InfoString = concat.join(AdminInfo)
                #If user is not an admin this will display if the user has access to pro and admin contacts when needed
                print 'This username, '+user+ 'is an organziationational account, please contact your administrator for help regarding the privleges and licenses assigned to this user'
                print 'your admin contact information is as follows:'+InfoString
            else:
                #If user is an admin this will tell the user if they have been provisioned for pro
                print 'This username, '+user+ ' is an organziationational account, as the current user is an admin, please login to ArcGIS Online to resolve any issues or contact Esri Technical Support.'

except KeyError:
    if token['error']['messageCode'] == 'SB_0008':
            print 'your account has been disabled'


