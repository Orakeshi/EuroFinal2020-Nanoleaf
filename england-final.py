import requests
import re
import json
from bs4 import BeautifulSoup
import time

UniversalIP = "192.168.0.182"
UniversalAuthCode = "IOe32CEizIqwNv15XNyk4ttlaT75jFE7"
defaultPort = "16021"

italyScore = 1
englandScore = 1

def checkScore():
    global italyScore
    global englandScore
    url = 'https://www.sportinglife.com/football/live/92310/form'
    response = requests.get(url)

    html_soup = BeautifulSoup(response.text, 'html.parser')

    type(html_soup)
    score_containers = html_soup.find_all('span', class_ = 'MatchScore__StyledScore-wxe8oz-2 dvrzWw')

    italy = score_containers[0].text
    england = score_containers[1].text
    print(england)

    print(italy)
    print(england)

    if(int(italy)==italyScore):
        checkScore.teamScored = "Italy"
        italyScore+=1
        GetLayout()
        return
    elif (int(england)==englandScore):
        checkScore.teamScored = "England"
        englandScore+=1
        GetLayout()
        return
    else:
        time.sleep(5)
        checkScore()
        return

def GetId(layout):
    leafId = []
    for i in range(len(layout)):
        if "panelId" in layout[i]:
            strippedData = layout[i].split(':')
            formatStripped = strippedData[1]
            temp = re.findall(r'\d+', formatStripped)
            leafId.append(temp)
    return leafId

def ReadPixelsInFile():
    leafId = GetId(outputFormat)
    test = []
    varStore={}
    for i in range (len(leafId)):
        teamName = checkScore.teamScored
        leafIdNum = str(leafId[i])
        tempId = leafIdNum.strip("[, ', ]")
        path = "Nanoleaf Testing-Enviroment/Pixel Data/" + teamName + "("+tempId + ")"+".txt"
        f = open(path, "r")
        tempArray = f.readlines()
        varStore[i] = tempArray
        f.close()
    return varStore

def SendRequest():
    leafId = GetId(outputFormat)
    varStore = ReadPixelsInFile()
    x=0
    f = open("Requests.txt", "a")
    while (True):
        for i in range (len(leafId)):
            x=x+1
            if(x>=5):
                x=0
            leafIdNum = str(leafId[i])
            print(leafIdNum)
            tempId = leafIdNum.strip("[, ', ]")
            rgbValue = str(varStore[0])
            tempNew = rgbValue.split(",")

            tempTempNew = str(tempNew[x])
            tempRGB = tempTempNew.strip("[, ]").replace('\\n', '').replace(",", '').replace("'", '')
            leafColour = '{"write" : {"command": "display","animType": "static","animData": "1 ' + tempId + ' 1 ' + tempRGB + ' 0 1","loop": false}}'
            f.write(leafColour)
            f.write("\n")

            newResponse = requests.put("http://"+str(UniversalIP.rstrip())+":"+defaultPort+"/api/v1/"+str(UniversalAuthCode.rstrip())+"/effects", leafColour)
            checkScore()
    
def GetLayout():
    global outputFormat
    newResponse = requests.get("http://"+str(UniversalIP.rstrip())+":"+defaultPort+"/api/v1/"+str(UniversalAuthCode.rstrip())+"/panelLayout/layout")
    output = str(newResponse.json())
    outputFormat = output[output.index('['):]
    outputFormat = outputFormat.split('}')
    PacketBuilder()
    return

def PacketBuilder():
    leafId = GetId(outputFormat)
    varStore = ReadPixelsInFile()
    f = open ("PacketSent.txt", "w")
    animDataList = []
    tempTest = []
    for i in range (len(leafId)):
        numPanels = len(leafId)
        leafIdNum = str(leafId[i])
        tempId = leafIdNum.strip("[, ', ]")
        timeDisplay = "2"
                    
        animDataNew = tempId+" "+str(len(varStore[i]))+" "
        animDataList.append(animDataNew)
        for x in range (len(varStore[i])):
            test = str(varStore[i][x].rstrip()+" 0 " + timeDisplay +" ")
            tempRGB = test.replace('\\n', '').replace(",", '').replace("'", '').replace("[", "").replace("]", "").replace("\"", "").replace("\\", "").replace("  ", " ")

            animDataList.append(tempRGB)

    str1 = ''.join(animDataList)

    leafColour = ('{"write": {"animData": "'+'{0} {1}'.format(numPanels, str1[:-1])+'","loop": true,"animType": "custom","palette": [],"version": "2.0","command": "display"}}')

    newResponse = requests.put("http://"+str(UniversalIP.rstrip())+":"+defaultPort+"/api/v1/"+str(UniversalAuthCode.rstrip())+"/effects", leafColour)
    f.write(leafColour)
    checkScore()
    return


checkScore()
GetLayout()
